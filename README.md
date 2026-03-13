# Counting Seals – Frisian Islands MSFS Addon

Simuliert Robbenkolonien auf den ostfriesischen Inseln für realistische Tierzählungen aus der Luft in MSFS 2024.

## Abhängigkeiten

- **[human-library-animated](https://flightsim.to/addon/33166/animated-humans-library)** (muss im Community-Ordner aktiv sein)
- MSFS 2024 SDK (fspackagetool für BGL-Kompilierung)

## Tiere

Aus dem Paket `human-library-animated` werden drei Arten gemischt platziert:

| Tier | Anteil | Varianten |
|------|--------|-----------|
| Seehund | ~74 % | Idle 1, Idle 2, Eating |
| Seelöwe | ~15 % | Idle, Idle 2, Sleeping, Eating |
| Walross | ~11 % | Idle 1, Idle 2, Eating, Sleeping |

Seelöwen und Walrosse haben 4–5 m Mindestabstand zu anderen Tieren.

## Kolonien (manuell auf Strandpositionen kalibriert)

Alle Positionen wurden im MSFS World Editor auf tatsächliche Strandabschnitte verschoben und als Zentroide gespeichert.

| Insel | Kolonie | Lat | Lon | Tiere |
|-------|---------|-----|-----|-------|
| Borkum | Südstrand West | 53.555536 | 6.725568 | 12–20 |
| Borkum | Südstrand Ost | 53.557510 | 6.727395 | 20–35 |
| Juist | Oststrand | 53.687456 | 7.047294 | 15–35 |
| Juist | Weststrand | 53.678601 | 6.954844 | 10–20 |
| Norderney | Oststrand | 53.723505 | 7.250180 | 20–40 |
| Norderney | Nordstrand | 53.723091 | 7.203580 | 15–30 |
| Baltrum | Oststrand | 53.733038 | 7.378404 | 10–25 |
| Baltrum | Weststrand | 53.727809 | 7.328515 | 8–20 |
| Langeoog | Oststrand | 53.758866 | 7.565573 | 15–35 |
| Langeoog | Nordstrand | 53.756560 | 7.509365 | 10–20 |
| Spiekeroog | Ostende | 53.779879 | 7.819503 | 15–30 |
| Spiekeroog | Westende | 53.755090 | 7.641781 | 10–25 |
| Wangerooge | Ostende | 53.787793 | 7.937940 | 20–40 |
| Wangerooge | Westende | 53.781440 | 7.859459 | 12–28 |

**Gesamt:** ~347 Tiere auf 14 Kolonien (7 Inseln)

## Dateien

| Datei | Beschreibung |
|-------|-------------|
| `generate_seals.py` | Hauptskript – generiert `EDWG_Seals.xml` und schreibt komplettes Paket direkt nach Community |
| `seal_colonies.json` | Koloniekoordinaten (kalibriert) |
| `seal_colonies.gpx` | GPX-Export der Koloniezentren |
| `bgl_writer.py` | Hilfsbibliothek für BGL-Ausgabe |

## Build-Workflow (Entwickler)

```
1. python generate_seals.py
   -> schreibt E:\Addons\PackageSources\scene\EDWG_Seals.xml
   -> schreibt komplettes Paket nach E:\Addons\Community\devprops-counting-seals-frisian-islands\

2. MSFS Project Editor: E:\Addons\counting-seals.xml oeffnen -> Build All
   -> kompiliert BGL nach E:\Addons\counting-seals-build\Build\devprops-counting-seals-frisian-islands\

3. Addons Linker: devprops-counting-seals-frisian-islands zeigt auf
   E:\Addons\Community\devprops-counting-seals-frisian-islands\
   (Linkziel: ...\LocalCache\Packages\Community\devprops-counting-seals-frisian-islands)
```

## SDK-Projektstruktur

```
E:\Addons\
+-- counting-seals.xml                                    <- Project Editor Projektdatei
+-- PackageDefinitions\
|   +-- devprops-counting-seals-frisian-islands.xml       <- AssetPackage-Definition
+-- PackageSources\
|   +-- scene\
|       +-- EDWG_Seals.xml                                <- generierte Tierplatzierungen
+-- counting-seals-build\Build\
    +-- devprops-counting-seals-frisian-islands\          <- kompiliertes Paket
E:\Addons\Community\
+-- devprops-counting-seals-frisian-islands\              <- Addons Linker Quelle
```

## Hinweise

- `generate_seals.py` verwendet einen zufaelligen Seed – jeder Lauf erzeugt leicht andere
  Positionen innerhalb der kalibrierten Kolonie-Bereiche (Radius 30 m um den Zentroid).
- `ALT_OFFSET_M = 0.10` – Tiere schweben 0,10 m über Grund (snapToGround=FALSE). Bei Terrain-Änderungen ggf. anpassen.
- `imageComplexity="NORMAL"` – Object Density muss in MSFS nicht auf Maximum stehen.
- Die GUIDs fuer alle Tiere stammen aus `Hummods.BGL` im Paket `human-library-animated`
  (nicht aus den SimObject-Model-XMLs – diese haben andere GUIDs).
