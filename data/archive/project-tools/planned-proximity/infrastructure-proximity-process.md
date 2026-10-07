# Infrastructure proximity: process and script audit

Status: implementation in progress; methodological extension, not translation
Last updated: 2026-10-07
Version: 0.1
Scope: Centroid-to-registered Obrasgov point distances and neighbourhood income/race associations

The researcher approved implementing the distance-based racial spatial stratification study. This adds a new analysis without changing census aggregation, source geometry, approved location exclusions or website publication.

## Design and decisions

Use complete harmonised `common_id` groups and 2022 census racial composition, household-head-weighted mean income and population density. Geometric centroids are a documented initial approximation; flag centroids outside their source polygons and excessive network snapping. Do not replace them with invented residential locations. Census-year demographics and a contemporary street/project snapshot are different observation times.

The primary outcome is shortest walking-network distance to the nearest distinct registered Obrasgov point project, including recorded origin/destination snapping connectors. Save straight-line benchmarks, nearest-k project identities/distances and a bounded inverse-distance score over those k projects. Project taxonomy expansion and multiple component locations must not multiply project counts. This does not measure service availability, catchments, beneficiaries or causal project effects. Line/polygon projects remain preserved and separately counted as outside this point-destination analysis.

Fit neighbourhood-level associations only where income–racial-composition support exists. Compare overall, income-adjusted and interaction/density-adjusted models on the same supported sample; keep incomplete income and failed routes visible. Use spatial-block uncertainty, rank checks and explicit unestimable notices. Income adjustment is not a decomposition of racism or proof of individual discrimination. Combined Black/Brown shares are accompanied by separate-composition sensitivity checks.

## Inputs and provenance

- Versioned harmonisation bundle and 2022 indicators, respecting the pipeline configuration and municipality scope.
- Frozen national `obrasgov-primary-state-filter/map_components.parquet` and completed producer contracts; do not rerun national screening as a hidden scoped dependency.
- A pinned local OpenStreetMap walking graph and acquisition manifest. Network acquisition is an explicit command; routine processing must not download.

No suitable local street graph was found at implementation start. Initial study geography is pending the researcher's preference, with Belo Horizonte proposed for the complete pilot. Full datasets remain local.

## Commands and generated outputs

Implementation, exact commands, output hashes and validation results will be recorded here before handoff. The executable Markdown report will link its processing, modelling and display functions and embed only figures generated from the current processing outputs.

## Audit status

Final audit pending: distinct-project routing, network topology and snapping, common-area/version consistency, income/race support, spatial uncertainty, interrupted output publication, acquisition isolation, report provenance and fresh-process execution.
