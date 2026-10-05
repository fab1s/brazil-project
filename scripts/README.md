# Project Utilities

Status: current
Last updated: 2026-10-05
Version: 0.3
Scope: Project Utilities

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.3 | Codex | Documented map utilities and read-only Obrasgov coordinate screening. |

migrate_files.py copies and verifies original files. verify_r_reference.py compares fresh independent exports. create_project_docs.py builds initial documentation; maintaining current documentation afterward requires deliberate edits. The r folder retains isolated R adapters and reference checks.

`build_web_map.py` exports version-matched common-area indicators to the existing map. `snapshot_web_map.py` explicitly downloads and verifies the existing site assets for an initialized local map build; its saved credentials and derivatives stay outside Git. Build, verification, and publishing contracts are in [the web-map workflow](../docs/technical/web-map.md).

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`audit_obras_locations.py` reads the frozen Obrasgov GeoPackage and saves diagnostic counts, a checksum and illustrative offshore examples. It requires the project GeoPandas/Shapely environment and never modifies inputs. Run `--output .cache/obras-spatial-audit/recheck.json`; the [spatial review](../docs/verification/obrasgov-spatial-review.md) states its geographic and collection-extraction limits.
