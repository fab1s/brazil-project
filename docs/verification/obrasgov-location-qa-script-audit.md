# Obrasgov Location QA — Final Script Audit

Status: audited; fixes verified
Last updated: 2026-10-06
Version: 0.1
Scope: Producer, reference acquisition, verification and figure generation

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.1 | Codex | Reviewed completed scripts, fixed three utility issues and recorded remaining limits. |

Reviewed `src/brazil_project/infrastructure/location_qa.py`, `scripts/acquire_location_references.py`, `scripts/verify_location_qa.py`, `scripts/plot_location_qa.py` and CLI/configuration wiring after successful national preprocessing. Checks covered provenance, source preservation, geometry decomposition, eligibility boundaries, repeated IDs, investments, failure handling, exchange formats and repeat execution.

| Finding | Resolution / evidence |
| --- | --- |
| Plotting previously read artifacts without checking the saved producer contract and hardcoded the municipal filename. | **Fixed:** require a completed report; verify component, source and municipal-reference checksums; use the recorded reference path. Tests reject incomplete runs and changed inputs. |
| Acquisition manifest writes could be interrupted mid-JSON, losing usable provenance. | **Fixed:** write a temporary manifest and replace atomically. An interruption test preserves the prior verified manifest and verifies retry. Incomplete downloads restart; completed checksum-matching archives are reused. |
| Verifier assertions could be disabled by Python `-O`. | **Fixed:** reject optimized Python before validation. A subprocess test exercises the guard. |
| Recursive collections, repeated project IDs and line excursions could distort geographic or investment coverage. | **Checked:** source rows/attributes/WKB remain exact; component partition and source-row investment coverage pass; offshore vertices and shared boundaries are tested. Consistent-ID budgets are separate from repeated source-row sums. |
| Refactoring expensive spatial indexes could change distances or results. | **Checked:** indexed coastline distances match the unsplit reference in tests; two fresh national runs produce byte-identical GeoParquet artifacts. |
| Simplified diagnostic maps could be mistaken for analysis geometry. | **Checked:** simplification is limited to the figure backdrop; point coordinates remain unchanged. The figure caption states its omissions. |

Remaining limitations are explicit: generalized coastline/islands, description-based marine signals, line sampling/capping, absent structured municipality codes and historical works checked against 2022 boundaries. No coordinate is certified or inferred. This is software verification, not scientific validation.

Outputs are atomic per GeoParquet file, not a transaction across the whole directory; the review CSV is written directly. Concurrent execution is unsupported. After interruption, rerun the stage and use `verify_location_qa.py` before consuming its GeoPackage/tables; mixed files are detected by the saved hashes and exchange checks. A versioned whole-stage bundle remains a future hardening option.

All 51 tests pass, including four tests for the audit fixes. The hardened verifier passes on the saved national outputs and the figure was regenerated with provenance checks; the embedded image is byte-identical to the generated output.

Counts and exact checks are in [verification evidence](obrasgov-location-qa-evidence.json). Commands and the rendered figure are in [the process record](../current/obrasgov-location-qa-process.md).
