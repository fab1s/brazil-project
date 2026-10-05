# Census Correspondence And The Geographic Overview

Status: current
Last updated: 2026-10-05
Version: 0.2
Scope: Census Correspondence And The Geographic Overview

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.2 | Codex | Recorded the harmonisation corrections and approved research assumptions. |

`census.py` builds positive-area bidirectional correspondence, validates imported links, selects complete groups after matching, and publishes atomic versioned bundles. Inputs are preserved tract/baseline GeoPackages plus optional census tables for coverage. Main outputs are dissolved common-group geometry, reference pieces, lookups, unmatched inventories, diagnostics, and provenance.

`overview.py` retains the independent original sf/S2 geographic overview. Census correspondence depends on GeoPandas, Shapely, pandas and NetworkX; the overview additionally requires locked R dependencies. Run `brazil-project run harmonisation --municipality 3106200` for a selected complete-group scope. Add `--recompute-harmonisation` only when national recomputation is intended.

Read [workflow contracts](../../../docs/technical/workflow.md) and [approved policy](../../../docs/methods/harmonisation-policy.md) before changing matching or aggregation. Update methods, tests, progress and verification whenever these contracts change.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.
