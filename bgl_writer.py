"""
bgl_writer.py – Minimal FSX/MSFS BGL writer for SceneryObject placement.

Generates a binary BGL file that places SimObjects (by containerTitle)
or LibraryObjects (by GUID) at specific GPS coordinates.

BGL format references:
  - FSX/P3D Scenery SDK (BGL file format)
  - Record type 0x001A = SimObject placement
  - Record type 0x000E = Library object placement (GUID)

Both MSFS 2020 and MSFS 2024 read these BGL files from Community packages.
"""

import struct
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ── Coordinate encoding ───────────────────────────────────────────────────────
# FSX/MSFS uses 32-bit integers for lat/lon in the BGL format
# Latitude:  0x10000000 per 90 degrees (range -90..90 → 0x00000000..0x20000000)
#            encoded as: (lat + 90) / 180 * 0x20000000  ...but signed
# Actually the standard encoding is:
#   lat_enc = round(lat * (0x20000000 / 90.0))   signed 32-bit
#   lon_enc = round(lon * (0x10000000 / 90.0))   unsigned 32-bit (0..360)

def encode_lat(lat_deg: float) -> int:
    """Encode latitude to FSX 32-bit signed integer."""
    return round(lat_deg * (0x20000000 / 90.0)) & 0xFFFFFFFF


def encode_lon(lon_deg: float) -> int:
    """Encode longitude to FSX 32-bit unsigned integer (0..360)."""
    return round(lon_deg * (0x10000000 / 90.0)) & 0xFFFFFFFF


def encode_alt_meters(alt_m: float) -> int:
    """Encode altitude in meters to FSX 32-bit integer (in meters * 1000)."""
    return round(alt_m * 1000)


def encode_heading(hdg_deg: float) -> int:
    """Encode heading to FSX 16-bit unsigned integer (0..360 → 0..0xFFFF)."""
    return round((hdg_deg % 360.0) / 360.0 * 0xFFFF) & 0xFFFF


# ── BGL Section / record helpers ──────────────────────────────────────────────
QMID_NONE = 0xFFFFFFFF


def lat_lon_to_qmid(lat: float, lon: float, level: int = 14) -> int:
    """
    Compute the Quad Mesh ID (QMID) for a given lat/lon at a given level.
    Level 14 is used for object placement in FSX/MSFS.
    The QMID indexes the 2^level × 2^level grid over the earth.
    """
    # Normalise lon to 0..360
    nlon = (lon + 360.0) % 360.0
    nlat = lat + 90.0  # 0..180

    cells = 1 << level  # 2^level
    x = int(nlon / 360.0 * cells) % cells
    y = int(nlat / 180.0 * cells) % cells
    return (y * cells + x) & 0xFFFFFFFF


def guid_str_to_bytes(guid_str: str) -> bytes:
    """
    Convert '{71b37f42-3f25-43ff-b1a4-9bcabb500fe4}' to 16 raw bytes (little-endian).
    BGL stores the GUID in mixed-endian format (Data1,2,3 as LE ints, Data4 as bytes).
    """
    clean = guid_str.strip("{}").replace("-", "")
    data1 = int(clean[0:8],  16)
    data2 = int(clean[8:12], 16)
    data3 = int(clean[12:16], 16)
    data4 = bytes.fromhex(clean[16:32])
    return struct.pack("<IHH", data1, data2, data3) + data4


# ── Record builders ───────────────────────────────────────────────────────────

def make_simobject_record(lat: float, lon: float, alt_m: float,
                          heading: float, container_title: str) -> bytes:
    """
    Build a BGL record for SimObject placement (type 0x001A).
    Supported by FSX, P3D, MSFS 2020, MSFS 2024.
    """
    title_enc = container_title.encode("ascii") + b"\x00"
    # Pad to 4-byte boundary
    pad = (4 - len(title_enc) % 4) % 4
    title_enc += b"\x00" * pad

    lat_enc = encode_lat(lat)
    lon_enc = encode_lon(lon)
    alt_enc = encode_alt_meters(alt_m)
    hdg_enc = encode_heading(heading)

    body = struct.pack(
        "<IIiHHHH",
        lon_enc,    # longitude (unsigned 32)
        lat_enc,    # latitude  (unsigned 32, sign-extended)
        alt_enc,    # altitude  (signed 32, metres * 1000)
        hdg_enc,    # heading   (unsigned 16)
        0x0001,     # flags: altIsAGL=1
        0,          # pitch (unused)
        0,          # bank  (unused)
    ) + title_enc

    # Record header: type (2 bytes) + size (4 bytes)
    rec_type = 0x001A
    rec_size = 6 + len(body)
    return struct.pack("<HI", rec_type, rec_size) + body


def make_library_object_record(lat: float, lon: float, alt_m: float,
                               heading: float, guid_str: str,
                               scale: float = 1.0) -> bytes:
    """
    Build a BGL record for LibraryObject placement (type 0x000E).
    Places an object by GUID, independent of SimObject container title.
    """
    guid_bytes = guid_str_to_bytes(guid_str)

    lat_enc = encode_lat(lat)
    lon_enc = encode_lon(lon)
    alt_enc = encode_alt_meters(alt_m)
    hdg_enc = encode_heading(heading)
    scale_enc = round(scale * 100)  # percent

    body = struct.pack(
        "<IIiHHHHH",
        lon_enc,
        lat_enc,
        alt_enc,
        hdg_enc,
        0x0001,     # flags: altIsAGL=1
        0,          # pitch
        0,          # bank
        scale_enc,
    ) + guid_bytes

    rec_type = 0x000E
    rec_size = 6 + len(body)
    return struct.pack("<HI", rec_type, rec_size) + body


# ── BGL file assembler ────────────────────────────────────────────────────────

@dataclass
class SceneryPlacement:
    lat: float
    lon: float
    alt_m: float = 0.0
    heading: float = 0.0
    guid: Optional[str] = None
    container_title: Optional[str] = None


def write_bgl(path: Path, placements: list[SceneryPlacement]) -> int:
    """
    Write a minimal FSX/MSFS BGL file for scenery object placement.
    Returns the number of records written.
    """
    # Group placements by QMID (level 14) for the section structure.
    # For simplicity we put everything in one section (QMID of first placement).
    # This is valid for a geographically small addon.
    if not placements:
        return 0

    # Build all placement records
    records = b""
    for p in placements:
        if p.guid:
            records += make_library_object_record(p.lat, p.lon, p.alt_m, p.heading, p.guid)
        elif p.container_title:
            records += make_simobject_record(p.lat, p.lon, p.alt_m, p.heading, p.container_title)

    # SubSection:  header (16 bytes) + records
    qmid = lat_lon_to_qmid(placements[0].lat, placements[0].lon)
    subsec_data = records
    subsec_size = 16 + len(subsec_data)
    subsection = struct.pack("<IIII",
        qmid,                # QMID
        len(placements),     # num records
        16,                  # data offset within subsection
        len(subsec_data),    # data size
    ) + subsec_data

    # Section header (20 bytes)
    section_type = 0x0022   # Object placement section type
    section_size = 20 + len(subsection)
    section = struct.pack("<IIIII",
        section_type,
        0,                   # compression (0 = none)
        section_size,
        1,                   # num subsections
        20,                  # offset to subsections
    ) + subsection

    # BGL file header (56 bytes)
    bgl_header_size = 56
    num_sections = 1
    section_offset = bgl_header_size
    total_size = bgl_header_size + len(section)

    header = struct.pack("<IIIIIIIIIIIIII",
        0x19920201,          # magic
        total_size,
        0,                   # timestamp (0 = ignore)
        0,                   # MD5 part 1 (skip)
        0,                   # MD5 part 2 (skip)
        0,                   # MD5 part 3 (skip)
        0,                   # MD5 part 4 (skip)
        num_sections,
        section_offset,
        0, 0, 0, 0, 0,       # padding
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + section)
    return len(placements)


# ── Quick self-test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_path = Path("test_seals.bgl")
    pl = [
        SceneryPlacement(53.570, 6.710, 0.0, 45.0,
                         guid="{71b37f42-3f25-43ff-b1a4-9bcabb500fe4}"),
        SceneryPlacement(53.571, 6.711, 0.0, 90.0,
                         guid="{71b37f42-3f25-43ff-b1a4-9bcabb500fe4}"),
    ]
    n = write_bgl(test_path, pl)
    print(f"Written {n} records to {test_path} ({test_path.stat().st_size} bytes)")
