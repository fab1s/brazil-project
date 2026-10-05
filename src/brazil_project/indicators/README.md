# Annual Temporal Estimates, Weighted Income And Density

Status: current
Last updated: 2026-10-05
Version: 0.2
Scope: Annual Temporal Estimates, Weighted Income And Density

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.2 | Codex | Recorded the harmonisation corrections and approved research assumptions. |

`temporal.py` reads a verified complete harmonisation bundle and local census Parquet inputs, computes annual common-group estimates, and saves tabular estimates plus one-feature-per-common-group spatial indicators. Density uses the saved equal-area denominator from the same bundle; legacy geometry files are ignored. Input columns, missingness, weights, and inflation rules follow the methods record. Run `brazil-project run indicators --municipality 3106200`. Update methods, tests and mapping when changing behavior.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.
