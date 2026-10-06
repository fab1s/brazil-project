# Harmonisation Update Verification

Status: implemented; national baseline and regional numerical checks passed with recorded limits
Last updated: 2026-10-06
Version: 0.2
Scope: Researcher-approved harmonisation corrections following the audit

## Changes delivered

- Atomic complete bundles replace loose geometry/lookup selection. Consumers verify source fingerprints, correspondence mode, scope, artifact checksums, and group counts. Density cannot choose an earlier comparison geometry by file existence.
- Imported scopes retain complete national components. Explicit Python recomputation matches nationally and caches the result before selecting complete municipality groups.
- Analytical spatial indicators and `common_geometry_2022` have one feature per `common_id`. Full contributing pieces outside municipality boundaries are included. Original tract reference geometry, unique part IDs, and separate unmatched geometry remain available.
- Matching requires strictly positive polygon overlap in both imported validation and recomputation. Contact-only links are rejected and recorded. The original source files and baseline snapshots are preserved.
- Unmatched inventories include available population/household values, coverage totals, missingness, and shares of known totals. Unknown municipalities fail with an actionable error; an existing scope containing only excluded tracts can publish an empty matched layer with explicit unmatched inventories.
- The accepted boundary-change assumption and geometric diagnostics are recorded separately from the original translation in [harmonisation policy](harmonisation-policy.md).

## Verification results

| Check | Result |
| --- | --- |
| Python suite | 31 pass: original analytical/acquisition tests plus 13 harmonisation contract tests |
| National baseline links | Every imported edge has positive polygon overlap; zero edges removed |
| National common geometry | 287,178 features with unique common IDs: 276,669 Polygons and 10,509 MultiPolygons |
| National reference geometry | All 472,778 original 2022 pieces retained |
| National workflows | Harmonisation, indicators, and both conference charts complete |
| Stored national indicator reference | 12 of 13 match; only the previously recorded density absolute-change column differs |
| Fresh regional R reference | All 13 indicator calculations and both chart source populations, summaries, and cutoffs match |
| Regional merged output | 3,790 complete common-group features, with the original 5,167 in-city reference rows |
| Complete regional contributors | Includes all contributing source rows, including nine 2010 and 15 2022 rows outside Belo Horizonte |
| Repeated execution | Cached regional and national correspondence processing completes with consistent outputs |
| Historical local R geometry test | Prepared boundaries match; one point-only R link is intentionally rejected, changing the local connected partition |
| Quarto rendering | All nine reports render; all 102 local asset references exist |
| Notebook views | All 62 Python cells in nine reports execute in fresh processes using the current artifacts |
| Package and source checks | pip check and Python compilation pass; Markdown navigation and whitespace checks pass |

Regression tests cover contact-only candidates, stable member-based IDs, imported consistency, complete cross-municipality groups, mode switching, tampering, scope/input changes, interruption before publication, preserved part geometry, coverage missingness, empty matched scopes, and the original project-then-dissolve density area calculation.

## Unmatched coverage

The updated national baseline retains the same 16 unmatched 2010 IDs and 24 unmatched 2022 IDs as the audit. Available 2010 unmatched values include 87 people and 40 households; 12 excluded IDs have missing values for these measures, so these are known totals rather than complete estimates. In 2022 the excluded population is 281 with no missing population values; available excluded households total 80, with 21 missing household values. Reports also expose missing values among matched tracts, rather than treating coverage as complete automatically.

## Diagnostics and limitations

National footprint diagnostics flag 131,222 groups above a 10% symmetric-difference fraction under the configured projected-area diagnostic. These are not exclusions. The researcher accepts the assumption that boundary differences do not materially change the inhabited population; habitation data have not independently verified that assumption.

The corrected default validates existing national correspondence and preserves its group memberships on these inputs. Full national Python geometric recomputation has not been executed or benchmarked here. Synthetic full-input tests verify the new global-before-municipality control flow, and its results remain separately versioned from imported correspondence.

The historical stored density absolute-change mismatch remains exactly the known mismatch in 463,254 unique tract attribute records. It is not relabelled as a passing baseline comparison. Fresh regional R density calculations match after preserving the original area-operation order.

The historical municipality-clipped R geometry regression is not a reference for the approved national-before-scope method. Its prepared boundaries still match within the precision grid, but its overlap-pair and partition checks now fail intentionally: 2010 tract `310620025610235` and 2022 tract `310620025610645` intersect only at a point (zero square metres). The new matcher excludes that link. This result is recorded separately from the passing fresh regional R indicator calculations.

Machine-readable evidence is in [harmonisation-update-evidence.json](evidence/harmonisation-update-evidence.json). Generated GeoParquet and coverage inventories are outside Git; use the versioned bundle selected by `data/intermediate/harmonisation/current.json`, or its municipality counterpart, through the project context API.
