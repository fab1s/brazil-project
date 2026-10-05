# R Adapters And Reference Checks

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: R Adapters And Reference Checks

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

bootstrap.R isolates package libraries. restore.R restores renv.lock. acquire_census.R acquires versioned tables and boundaries. overview.R preserves geographic sf/S2 comparisons. validate_reference.R and harmonisation_reference.R compare original processing. Inputs and outputs are explicit local paths; never source the original save chunks.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.
