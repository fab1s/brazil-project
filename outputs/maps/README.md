# Generated Maps

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Generated Maps

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.2 | Codex | Documented local Obrasgov clean/quarantine layers. |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

Generated HTML maps preserve visible basemap attribution. Opening a map may request external basemap tiles.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`obrasgov-location-qa/locations.gpkg` contains the new eligible point/line layer and a quarantine layer when quarantined components exist. `review.csv` records non-default eligibility decisions and original project attributes. These are local spatial-screening outputs, not the published here.now tiles. Regenerate using the national `obrasgov-location-qa` CLI stage; see [the policy](../../docs/methods/obrasgov-location-policy.md).
