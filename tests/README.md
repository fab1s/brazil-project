# Scientific And Workflow Tests

Status: current
Last updated: 2026-10-06
Version: 0.4
Scope: Scientific And Workflow Tests

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.4 | Codex | Added location QA contracts. |
| 2026-10-05 | 0.3 | Codex | Recorded harmonisation contracts and weighted web-map export checks. |

test_methods.py exercises meaningful analytical and acquisition edge cases. Run python -m pytest. Independent R and stored-result comparisons supplement synthetic tests.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`test_harmonisation_contract.py` covers positive-area matching, stable group IDs, complete municipality groups, imported contact rejection, merged output uniqueness, retained unmatched geometry, coverage missingness, scope/source validation, mode switching, tampering, interrupted publication, and the original area operation order. Run `.venv/bin/python -m pytest tests/test_harmonisation_contract.py -q` for these contracts.

`test_web_map.py` checks nationwide weighted shares, paired coverage, density percentage change, complete group contributions to municipality overviews, absent indicator groups, and search shards for recomputed IDs. Browser and real export checks are recorded separately in `docs/verification/web-map-update.md`.

`test_location_qa.py` checks recursive decomposition, duplicate IDs, source preservation, marine signals, coastal tolerances, foreign land, small islands covered only by IBGE, shared municipal/state boundaries, missing and invalid locations, CRS rejection and offshore excursions in lines. These synthetic tests verify policy behavior; national results and limitations are recorded separately.

`test_location_utilities.py` covers the final audit fixes: interrupted manifest publication, completed-producer/plot-input guards and rejection of optimized-Python verification.
