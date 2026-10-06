# Infrastructure Category Processing, Cleaning And Charts

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Infrastructure Category Processing, Cleaning And Charts

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.2 | Codex | Added independent location-quality preprocessing. |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

Infrastructure category processing, cleaning and charts. Inputs and outputs follow the technical workflow contracts. Update methods, tests and mapping when changing behavior.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`location_qa.py` implements `brazil-project run obrasgov-location-qa --config config/project.toml`. It reads the frozen Obrasgov map snapshot and checksum-verified local geographic references, recursively audits components and exports original-row audits, clean map components and quarantine/review outputs. It preserves translated infrastructure outputs and original coordinates. Dependencies are the existing GeoPandas, Shapely and pandas environment. Read [the location policy](../../../docs/methods/obrasgov-location-policy.md) before changing thresholds or eligibility. Explicit geographic acquisition uses `scripts/acquire_location_references.py`; routine QA does not download data.
