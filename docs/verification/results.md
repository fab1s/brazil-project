# Verification Results

Status: verified with explicit limitations
Last updated: 2026-10-06
Version: 0.5
Scope: Verification Results

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.5 | Codex | Recorded national location screening and repeat verification. |
| 2026-10-05 | 0.4 | Codex | Recorded migration, harmonisation, and merged-area public map checks. |

## File integrity

All 344 original files were copied and SHA256 verified. The verification utility also rereads the OneDrive originals and confirms their recorded content hashes.

## Implemented checks

Focused tests cover projected correspondence, relations, unmatched tracts and ties, geometry preservation, count missingness, zero denominators, duplicate keys, weighted income, chart sanitation exclusions, ntile grouping, request resumption, wrong pages, fingerprints, and nested infrastructure records.

Independent evidence includes original stored-output comparisons and fresh R reference calculations. JSON reports under `data/intermediate/` record exact scopes, numerical tolerances, differences, and outcomes. The latest verification results are:

| Check | Result |
| --- | --- |
| Original file integrity | 344 source and copied file checksums match |
| Python method, adapter, map, location and utility tests | 51 pass |
| Indexed spherical intersection test | Matches original sf/S2 all-pairs results |
| Package dependencies and build | pip check passes; wheel and source distribution build |
| Fresh R indicator reference | All 13 calculations match on complete common areas intersecting Belo Horizonte |
| Fresh R conference chart reference | Both populations, summaries, and income cutoffs match |
| Historical local projected correspondence reference | Prepared geometry matches; one point-only R link and its connected partition intentionally differ under the approved positive-area rule |
| Prepared geometry boundaries | Maximum difference 0.0000009993095565430106 m within the 0.000001 m precision grid |
| National stored indicator results | 12 of 13 match; only stored density absolute-change values differ |
| Obrasgov snapshot cleaning | 133,417 retained records matches original count |
| IBAMA snapshot | 8,494 records with all sectors translated |
| Research report execution | All 62 Python cells in nine reports execute in fresh processes |
| Quarto HTML rendering | Nine reports rendered with Quarto 1.9.38; all 102 local asset references exist |
| Figure inspection | Four generated conference and infrastructure PNGs visually inspected |

The national density comparison covers 468,097 unique tract attribute records. Its population_density_change column differs in 463,254 records because the stored baseline repeats percentage change. Other compared density values, including area, annual densities, and percentage change, match. Current R code and Python agree on the absolute-difference calculation in the independent reference scope.

The copied base contains 4,681 additional rows for repeated tract IDs; they are retained and aggregation keys are deduplicated independently. The strict optional sanitation baseline is also preserved, but current temporal source code is compared against its matching standard baseline.

## Limits

Missing property input prevents that exploratory workflow from completing. New live infrastructure downloads were not performed. HTML reports were rendered with the checksum-verified portable Quarto runtime under `.cache/quarto/`. Browser layout inspection remains a research review task; the execution and local asset checks do not certify browser appearance. Archived results are preserved even when they differ from current code.

## Report runtime

Quarto 1.9.38 for macOS was downloaded from the [official release](https://github.com/quarto-dev/quarto-cli/releases/tag/v1.9.38). Its archive SHA256 matched the published checksum: `47089a5020cfb41981ba0d4b46e110edfa608722aea45ef248e14efba6d6b18a`. The portable runtime and rendered reports are excluded from Git.

## Later harmonisation policy verification

The researcher-approved [harmonisation update](harmonisation-update.md) supersedes the original tract-level display contract with merged common-area outputs and complete versioned bundles. National baseline memberships remain unchanged after positive-area validation. Fresh regional R calculations still match all 13 indicators and chart tables. The boundary-change assumption remains explicit and unverified against habitation data.

## Public map verification

The [here.now map update](web-map-update.md) exports one row per common ID, all 13 indicators, and complete-group summaries. All exported values match the corresponding research tables after existing map presentation exclusions. Browser checks cover overview/mid/detail loading, common-ID popups and search, density change, income, unmatched coverage, and desktop/mobile rendering.

## Obrasgov location-quality preprocessing

[National location QA](obrasgov-location-qa.md) is a new separate method, not translation parity. Two fresh CLI executions produce byte-identical GeoParquet artifacts, preserve 134,929 original rows and exact geometry/attributes, and conserve original source-row investment coverage. All 51 tests pass. The separate map derivative contains 226,309 eligible point/line components and 2,037 quarantined components; 2,010 polygons remain excluded by display policy. Location eligibility does not establish coordinate accuracy. Public website data have not adopted this derivative.
