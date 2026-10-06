# Project Utilities

Status: current
Last updated: 2026-10-06
Version: 0.6
Scope: Project Utilities

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.6 | Codex | Documented primary-state checks and auditable exclusion utility. |
| 2026-10-05 | 0.3 | Codex | Documented map utilities and read-only Obrasgov coordinate screening. |

migrate_files.py copies and verifies original files. verify_r_reference.py compares fresh independent exports. create_project_docs.py builds initial documentation; maintaining current documentation afterward requires deliberate edits. The r folder retains isolated R adapters and reference checks.

`build_web_map.py` exports version-matched common-area indicators to the existing map. `snapshot_web_map.py` explicitly downloads and verifies the existing site assets for an initialized local map build; its saved credentials and derivatives stay outside Git. Build, verification, and publishing contracts are in [the web-map workflow](../docs/technical/web-map.md).

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`audit_obras_locations.py` reads the frozen Obrasgov GeoPackage and saves diagnostic counts, a checksum and illustrative offshore examples. It requires the project GeoPandas/Shapely environment and never modifies inputs. Run `--output .cache/obras-spatial-audit/recheck.json`; the [spatial review](../docs/verification/obrasgov-spatial-review.md) states its geographic and collection-extraction limits.

`acquire_location_references.py` explicitly downloads pinned IBGE 2022 municipalities and Natural Earth land/coastline releases into `data/reference/location-qa`, preserving complete zip archives and per-file URL/checksum/date provenance. Verified completed downloads are reused after interruption; incomplete downloads restart safely. Routine location QA requires those local files and rejects checksum changes. It is independent of live Obrasgov acquisition.

`verify_location_qa.py --output .cache/obras-spatial-audit/verification.json` checks saved artifact hashes, exact original attributes and WKB, map/quarantine partition completeness, duplicated-location attribute provenance and source-row investment coverage. It requires a completed local QA run.

`plot_location_qa.py` renders unchanged, finite point components and review/eligibility flags into `outputs/figures/obrasgov-location-qa/location-screening.png`. Administrative boundaries are simplified only in this illustration; polygons, lines, missing and invalid points are omitted from the overview.

`check_obras_primary_state.py --config config/project.toml` checks every saved original component against unsimplified IBGE municipalities dissolved into states. It writes complete diagnostic CSVs/summary to `outputs/tables/obrasgov-primary-state` and a figure; no filtering, eligibility updates, corrections or map publication. See [results and script audit](../docs/verification/obrasgov-primary-state-check.md).

`filter_obras_primary_state.py --config config/project.toml` verifies the saved state diagnostic and excludes only `entirely_outside` components from a separate derivative. It saves the complete audit, retained and excluded GeoParquet datasets, eligible map GeoPackage, exclusion CSV and before/after figure. Baseline QA decisions are preserved. See [process, outputs and script audit](../docs/verification/obrasgov-primary-state-filter.md).
