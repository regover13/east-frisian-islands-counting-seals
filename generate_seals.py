#!/usr/bin/env python3
"""
Frisian Islands Seals - MSFS 2020/2024 Addon Generator
Generates realistic seal positions around known Seehundbanken (seal sandbanks)
and writes the full MSFS package structure to E:/Addons/Community/devprops-counting-seals-frisian-islands/
"""

import json
import math
import os
import random
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# Import BGL writer (same directory)
import sys
sys.path.insert(0, str(Path(__file__).parent))
from bgl_writer import SceneryPlacement, write_bgl

# ── Constants ─────────────────────────────────────────────────────────────────
# Library Object GUIDs from Hummods.BGL (human-library-animated)
# These are the PLACEABLE GUIDs (not SimObject model GUIDs)
# Seals – placed at colony center
SEAL_GUIDS = [
    ("{6d82f7fe-e3a1-48a2-bd25-0e9f9f0e9b26}", 40),  # ahqa Seal Idle 1
    ("{d3b5ff4d-9641-41c0-abf5-e4a66ecf1ffd}", 30),  # ahqa Seal Idle 2
    ("{f9e9846b-95bd-41b3-b67d-72235fea7907}", 20),  # ahqa Seal Eating
]
_SEAL_POOL = [g for g, w in SEAL_GUIDS for _ in range(w)]

# Sea Lions – placed with offset from colony center (own sub-group)
SEALION_GUIDS = [
    ("{5e9f77b0-7cda-46a3-bdba-e93b20afa06e}", 4),  # ahqa Sea Lion Idle
    ("{b61e9c72-bfcd-45f3-bbef-8e2d4d58ac38}", 3),  # ahqa Sea Lion Idle 2
    ("{8bf69cd7-6f09-4f1f-853a-fa46d657c29f}", 2),  # ahqa Sea Lion Sleeping
    ("{0a4187f5-eede-4935-933c-fe13177004f2}", 1),  # ahqa Sea Lion Eating
]
_SEALION_POOL = [g for g, w in SEALION_GUIDS for _ in range(w)]

# Walruses – placed with different offset from colony center (own sub-group)
WALRUS_GUIDS = [
    ("{77206626-0631-468a-95ce-6376dba11050}", 3),  # ahqa Walrus Idle 1
    ("{8d476645-4699-42a2-82c1-54377260fe29}", 3),  # ahqa Walrus Idle 2
    ("{0187ca95-0566-4422-9f3b-98c11a414447}", 2),  # ahqa Walrus Eating
    ("{343907ea-d134-41cf-a6d1-8da90d1db541}", 2),  # ahqa Walrus Sleeping
]
_WALRUS_POOL = [g for g, w in WALRUS_GUIDS for _ in range(w)]
PACKAGE_NAME = "devprops-counting-seals-frisian-islands"
OUTPUT_ROOT  = Path(r"E:\Addons\Community") / PACKAGE_NAME
SCRIPT_DIR   = Path(__file__).parent
COLONIES_FILE = SCRIPT_DIR / "seal_colonies.json"

# SDK project: scene XML goes here, fspackagetool compiles it to BGL
SDK_SCENE_XML = Path(r"E:\Addons\PackageSources\scene\EDWG_Seals.xml")

# 1 degree latitude ≈ 111,320 m
# 1 degree longitude ≈ 111,320 * cos(lat) m  (at ~53.7° ≈ 66,400 m/deg)
METERS_PER_DEG_LAT = 111_320.0

# Vertical offset above ground (AGL) for all animals.
# Adjust if models sink into the terrain (positive = higher, negative = lower).
ALT_OFFSET_M = 0.10


def meters_per_deg_lon(lat_deg: float) -> float:
    return METERS_PER_DEG_LAT * math.cos(math.radians(lat_deg))


def random_offset(lat: float, lon: float, radius_m: float) -> tuple[float, float]:
    """Return a random point within radius_m metres of (lat, lon)."""
    # random angle & distance (uniform disk)
    angle = random.uniform(0, 2 * math.pi)
    dist  = random.uniform(0, radius_m) * random.uniform(0.3, 1.0)  # cluster toward center

    dlat = (dist * math.cos(angle)) / METERS_PER_DEG_LAT
    dlon = (dist * math.sin(angle)) / meters_per_deg_lon(lat)
    return lat + dlat, lon + dlon


def point_dist_m(lat1, lon1, lat2, lon2) -> float:
    dlat = (lat1 - lat2) * METERS_PER_DEG_LAT
    dlon = (lon1 - lon2) * meters_per_deg_lon((lat1 + lat2) / 2)
    return math.sqrt(dlat * dlat + dlon * dlon)


def place_with_min_dist(clat, clon, radius, existing, min_dist, max_tries=50):
    """Random point within radius that is at least min_dist from all existing points."""
    for _ in range(max_tries):
        lat, lon = random_offset(clat, clon, radius)
        if all(point_dist_m(lat, lon, p.lat, p.lon) >= min_dist for p in existing):
            return lat, lon
    # Fallback: just return a random point without distance check
    return random_offset(clat, clon, radius)


def generate_placements(colonies_data: dict) -> tuple[list[SceneryPlacement], list[tuple[str, list[SceneryPlacement]]]]:
    """
    Generate all animal placements from colony data.
    Seals, Sea Lions and Walruses are mixed within the same colony area.
    Larger animals (Sea Lions, Walruses) keep a minimum distance from others.
    """
    all_placements = []
    colony_groups = []

    for island in colonies_data["colonies"]:
        for loc in island["locations"]:
            count = random.randint(loc["count_min"], loc["count_max"])
            colony_name = f"{island['island']} {loc['name']}"
            group = []

            # Seals – main group, 2m min distance between individuals
            for _ in range(count):
                lat, lon = place_with_min_dist(loc["lat"], loc["lon"], 30.0, group, min_dist=2.0)
                p = SceneryPlacement(lat=lat, lon=lon, alt_m=ALT_OFFSET_M,
                                     heading=random.uniform(0, 360),
                                     guid=random.choice(_SEAL_POOL))
                group.append(p)
                all_placements.append(p)

            # Sea Lions – 2-4 per colony, 4m min distance (larger animal)
            for _ in range(random.randint(2, 4)):
                lat, lon = place_with_min_dist(loc["lat"], loc["lon"], 30.0, group, min_dist=4.0)
                p = SceneryPlacement(lat=lat, lon=lon, alt_m=ALT_OFFSET_M,
                                     heading=random.uniform(0, 360),
                                     guid=random.choice(_SEALION_POOL))
                group.append(p)
                all_placements.append(p)

            # Walruses – 1-3 per colony, 5m min distance (largest animal)
            for _ in range(random.randint(1, 3)):
                lat, lon = place_with_min_dist(loc["lat"], loc["lon"], 30.0, group, min_dist=5.0)
                p = SceneryPlacement(lat=lat, lon=lon, alt_m=ALT_OFFSET_M,
                                     heading=random.uniform(0, 360),
                                     guid=random.choice(_WALRUS_POOL))
                group.append(p)
                all_placements.append(p)

            colony_groups.append((colony_name, group))

    return all_placements, colony_groups


def build_placement_xml(colony_groups: list[tuple[str, list[SceneryPlacement]]]) -> str:
    """Build FSData XML source (SceneryObject/LibraryObject format) from pre-generated placements."""
    total = sum(len(g) for _, g in colony_groups)
    num_colonies = len(colony_groups)

    blocks = []
    for colony_name, group in colony_groups:
        lines = [f"    <!-- Kolonie {colony_name} ({len(group)} Robben) -->"]
        for p in group:
            lines.append(
                f'    <SceneryObject lat="{p.lat:.6f}" lon="{p.lon:.6f}" alt="{p.alt_m:.14f}"'
                f' pitch="0.000000" bank="0.000000" heading="{p.heading:.6f}"'
                f' imageComplexity="NORMAL" altitudeIsAgl="TRUE">'
            )
            lines.append(f'        <LibraryObject name="{p.guid}" scale="1.000000"/>')
            lines.append('    </SceneryObject>')
        blocks.append("\n".join(lines))

    xml_lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<!-- Frisian Islands Seals - generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")} UTC -->',
        f'<!-- Total seals: {total} across {num_colonies} colonies -->',
        '<FSData version="9.0">',
        "",
        "\n\n".join(blocks),
        "",
        '</FSData>',
    ]
    return "\n".join(xml_lines)


def build_package_definition_xml() -> str:
    return """\
<?xml version="1.0" encoding="utf-8"?>
<PackageDefinition>
  <AssetGroups>
    <AssetGroup Name="seals-frisian">
      <Type>Scenery</Type>
      <Flags>
        <Flag Name="IsConvex" Value="false"/>
      </Flags>
      <AssetDir>Scenery\\</AssetDir>
      <OutputDir>..\\..\\scenery\\</OutputDir>
    </AssetGroup>
  </AssetGroups>
</PackageDefinition>
"""


def build_package_xml() -> str:
    return f"""\
<?xml version="1.0" encoding="utf-8"?>
<ModelInfo
  guid="{{{generate_guid()}}}"
  version="1.1">
</ModelInfo>
"""


def build_manifest_json() -> str:
    data = {
        "dependencies": [
            {"name": "human-library-animated", "package_version": "1.4.0"}
        ],
        "content_type": "SCENERY",
        "title": "Frisian Islands Seals",
        "manufacturer": "",
        "creator": "devprops",
        "package_version": "1.0.0",
        "minimum_game_version": "1.39.9",
        "release_notes": {
            "neutral": {
                "LastUpdate": "",
                "OlderHistory": ""
            }
        }
    }
    return json.dumps(data, indent=2)


def build_layout_json(output_root: Path) -> str:
    """Walk the package tree and build layout.json entries."""
    entries = []
    for path in sorted(output_root.rglob("*")):
        if path.is_file() and path.name != "layout.json":
            rel = path.relative_to(output_root).as_posix()
            size = path.stat().st_size
            # MSFS uses a date-based 'date' field (Win FILETIME int), use 0 as placeholder
            entries.append({"path": rel, "size": size, "date": 0})
    return json.dumps({"content": entries}, indent=2)


def generate_guid() -> str:
    """Generate a deterministic GUID-like string for the package."""
    h = hashlib.md5(PACKAGE_NAME.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    try:
        display = path.relative_to(OUTPUT_ROOT.parent)
    except ValueError:
        display = path
    print(f"  [OK] {display}")


def export_gpx(colonies_data: dict, out_path: Path):
    """Export seal colony centres as GPX waypoints for MSFS World Editor."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="counting-seals-generator"',
        '     xmlns="http://www.topografix.com/GPX/1/1">',
        '  <trk><name>Frisian Seal Colonies</name><trkseg>',
    ]
    for island in colonies_data["colonies"]:
        for loc in island["locations"]:
            name = f"{island['island']} – {loc['name']}"
            lines.append(
                f'    <trkpt lat="{loc["lat"]}" lon="{loc["lon"]}">'
                f'<name>{name}</name></trkpt>'
            )
    lines += ["  </trkseg></trk>", "</gpx>"]
    write_file(out_path, "\n".join(lines))


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    random.seed()  # non-deterministic each run for natural variation

    print(f"\nFrisian Islands Seals Generator")
    print(f"Output: {OUTPUT_ROOT}\n")

    with open(COLONIES_FILE, encoding="utf-8") as f:
        colonies_data = json.load(f)

    # 1. Generate all seal positions
    all_placements, colony_groups = generate_placements(colonies_data)
    total_seals = len(all_placements)

    # 2. Write scene XML for SDK compilation (Project Editor → Build compiles to BGL)
    write_file(SDK_SCENE_XML, build_placement_xml(colony_groups))

    # 3. GPX export for reference
    gpx_path = SCRIPT_DIR / "seal_colonies.gpx"
    export_gpx(colonies_data, gpx_path)
    print(f"  [OK] seal_colonies.gpx")

    print(f"\nDone! {total_seals} Robben auf 7 Inseln platziert.")
    print(f"  Scene XML: {SDK_SCENE_XML}")
    print(f"  Naechster Schritt: Project Editor → counting-seals.xml öffnen → Build")
    print(f"  MSFS starten → zu EDWB/EDWJ/EDWY/EDWI/EDWL/EDWS/EDWW fliegen")


if __name__ == "__main__":
    main()
