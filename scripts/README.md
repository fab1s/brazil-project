# Project Utilities

Status: current
Last updated: 2026-10-05
Version: 0.2
Scope: Project Utilities

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.2 | Codex | Documented migration, verification, and here.now map utilities. |

migrate_files.py copies and verifies original files. verify_r_reference.py compares fresh independent exports. create_project_docs.py builds initial documentation; maintaining current documentation afterward requires deliberate edits. The r folder retains isolated R adapters and reference checks.

`build_web_map.py` exports version-matched common-area indicators to the existing map. `snapshot_web_map.py` explicitly downloads and verifies the existing site assets for an initialized local map build; its saved credentials and derivatives stay outside Git. Build, verification, and publishing contracts are in [the web-map workflow](../docs/technical/web-map.md).

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.
