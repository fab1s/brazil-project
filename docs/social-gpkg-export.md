# Concise national census GeoPackage

Status: complete; requested copy verified
Last updated: 2026-10-26
Version: 0.2
Scope: English field names and original-code traceability for the national research map data

The `social` layer has **one row per merged comparison area** and one English-named column per distinct saved measure. The `overview` layer holds municipality display summaries. The non-spatial `field_dictionary` is a long mapping table: each row lists an `original_column`, its `english_column`, unit and meaning. The `export_metadata` table records the inputs, original calculation code, checks and limits. Original coded data remain in the prepared map GeoPackage and versioned processing artifacts.

Examples from the new `social` layer:

| Original column | English column | Meaning |
| --- | --- | --- |
| `black_brown_n2022` | `black_brown_population_2022` | Black and Brown resident count |
| `black_brown_d2022` | `population_for_race_2022` | Total population used for the racial share |
| `black_brown_2022` | `black_brown_share_2022` | Share as a fraction: 0.25 means 25% |
| `population_density_n2022` | `total_population_2022` | Population used for density |

The 2022 Black, Brown and combined-race denominators match exactly, including missing values, so they share `population_for_race_2022`. `total_population_2022` remains separate: **2,184** areas have a density population value but no usable racial-share denominator. The export only combines fields with matching units, values and missingness, and checks every original field against its final English column. It does not alter census calculations. Share changes are percentage points; density and income changes are relative percentages. The website's tile schema and live map are unchanged.

Run from the project root:

```bash
.venv/bin/python code/scripts/build_web_map.py --config project.toml --work .cache/map-update/build --gpkg-only --gpkg-output outputs/maps/social-clean/social.gpkg
```

The mode uses the existing map preparation functions and checks the national harmonisation bundle, every saved indicator checksum, and the prepared map database. Choose a new output path for another run; it refuses to overwrite an existing file. It stages the complete GeoPackage beside its destination and publishes it only after all checks. A crash can leave `.gpkg.lock`; confirm no export is active before removing that stale lock and retrying. The final verified copy is `/Users/fa4850sc/Documents/Data/social.gpkg`.

## Code output and verification

The local export at `outputs/maps/social-clean/social.gpkg` and its copy in the requested `Data` folder are **599,494,656 bytes** with the same SHA-256 checksum, `23eb6c1d60ba62e6fbb5112838f76c486534e340e36c4716631e7191aab0e4d7`. The export has **287,178** distinct `common_id` values and **86** spatial attributes in `social`, and **5,570** municipality rows and **70** spatial attributes in `overview`. The long dictionary has **187 mappings**, one for each original attribute in the two source layers. The export combines 16 exactly equal source columns in `social` and 15 in `overview`; none of the differing indicator masks are filled or merged. For `common_id = 1`, the Black/Brown count remains **601**, the corresponding population remains **928**, and the share remains **0.6476293103448276**.

The producer compared every original source value and null pattern against the new file. It also checked common IDs, CRS, geometry and GeoPackage integrity; the user copy passed the same size, checksum, layer and integrity checks. Source Polygons may become MultiPolygons when saved to GeoPackage, with the same shape. The full project suite passed **199 tests**, including **18 focused map/export tests**. [Machine-readable evidence](evidence/social-gpkg-export.json) records file checksums, layer counts and the final tests.

## Script audit

- **Correctness:** The output uses the original `build_web_map.py` values. The dictionary reconstructs every source attribute exactly; grouping is allowed only with equal units, values and nulls. One feature remains per `common_id`.
- **Provenance:** The file stores the versioned bundle, indicator and prepared-map checksums plus the producing code paths. No acquisition runs.
- **Failure and recovery:** National scope and a new destination are required. A changed input, failed integrity check or interrupted staging prevents publication. The previous file remains until the final replacement is verified.
- **Limits:** The simplified columns retain the original missing-data rules. Software parity does not independently validate census source values, the accepted boundary-change assumption or the municipality overview's cross-boundary summaries.
