# Current Project Progress

Status: implemented and validated with recorded limitations
Last updated: 2026-10-05
Version: 0.4
Scope: Current Project Progress

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.4 | Codex | Recorded the approved harmonisation corrections and current verification scope. |

The complete original file collection is copied, organized, and checksum verified. The Python package and CLI are installed locally. Python dependencies and retained R dependencies are locked.

Python annual indicators and conference chart populations are implemented, and national outputs have been generated. Infrastructure snapshot processing is implemented; Obrasgov retains 133,417 records after cleaning, matching the original snapshot. IBAMA includes 8,494 records with translated sectors. Land-value annex imports and the available zone geometry are implemented; the exact cadastral input remains missing.

All 13 indicator calculations and conference chart populations match a fresh original R reference on complete common areas intersecting Belo Horizonte. Projected Python correspondence matches original R pairs and groups for that scope; geometry boundaries agree within the original one micrometre precision grid. Twelve national stored indicator outputs match; the remaining density absolute-change discrepancy is documented in [results](../verification/results.md).

The spherical overview preserves R sf/S2 and produces original comparison classifications and example maps. All nine Python-backed reports execute in fresh processes and render to HTML under `outputs/reports/notebooks/`; their 102 local asset references resolve. The original 18 tests were supplemented by 13 harmonisation contract tests; all 31 pass. National crosswalk recomputation and live external harvest parity are not declared validated. The original Linha Verde overlay is absent and is reported without substituting another geometry.

The [harmonisation update](../verification/harmonisation-update.md) addresses the audit findings: positive-area matching, complete groups, atomic versioned geometry/lookup bundles, merged analytical polygons, unique part IDs, and unmatched coverage inventories. The researcher accepts the documented boundary-change assumption; footprint diagnostics remain available and do not block groups automatically. National baseline processing has been regenerated under this policy. Explicit full-national geometric recomputation has not been run as part of this update.
