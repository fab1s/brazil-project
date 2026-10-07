# National government-data quality: process and script audit

Status: implemented; software verified; source quality remains under review
Last updated: 2026-10-07
Version: 0.3
Scope: National Obrasgov snapshot and census prerequisites for a future distance study

Read the [concise assessment](../research/reports/gov_data_quality.md) for six findings and three essential figures. The [detailed annex](../research/reports/gov_data_quality_annex.md) preserves the complete explanations, seven original executable cells, diagnostic tables, all eleven figures and provenance. This stage examines the preserved national Obrasgov snapshot and 2010/2022 census inputs. It makes no new exclusions or corrections and performs no network acquisition, distances or regressions. IBAMA licensing is a separate dataset, outside this assessment.

## Reproduce and trace the process

```bash
brazil-project run gov-data-quality --config project.toml
# Refresh only, after verifying saved producers and artifacts:
brazil-project report gov_data_quality --from-saved --config project.toml
```

Execution: [CLI](../code/brazil_project/cli.py) → [national orchestration](../code/brazil_project/infrastructure/gov_quality.py) → [attribute checks](../code/brazil_project/infrastructure/gov_quality_attributes.py) and [census checks](../code/brazil_project/infrastructure/gov_quality_census.py) → saved tables/figures → protected Markdown refresh. Source functions are linked beside the report's executable cells and in the [pipeline guide](pipeline-source.md).

Inputs are the immutable `data/processed/obrasgov/projects_st.gpkg`, completed location-QA/primary-state artifacts and pinned IBGE/Natural Earth references, the current complete national harmonisation bundle, raw census Parquets, and saved Black/Brown, income and density indicators. Hashes bind the consumed files and prior screening contracts. The original Obrasgov SHA-256 is `091c27860f78eee1e6abe989dbbef65a8b7412f87d82616d74c30ca6774f17cc`.

The audit intentionally reads verified frozen upstream results; it does not require an older producer's whole-package hash to include newly added diagnostic code. Relevant upstream code/policy and exact input/output hashes are checked instead. Current audit producers and report publication use the normal configuration, code and artifact checks. Missing or changed prerequisites fail with an explicit processing/recovery instruction.

`project.toml` records `as_of_date = "2026-10-07"` and `shared_coordinate_threshold = 25`. Date parsing accepts translated datetimes or unambiguous ISO text. Sharing uses exact coordinates and different project IDs, without rounding. Thresholds 2, 5, 10, 25, 50 and 100 provide sensitivity diagnostics. These choices flag concerns; they do not change analytical eligibility.

Outputs comprise 32 nonempty diagnostic tables and eleven figures under `data/intermediate/gov-data-quality/` and `outputs/figures/gov-data-quality/`. The report saves exact figure bytes in `research/reports/assets/`; only small reviewed figures are copied to `docs/assets/`. Full project/coordinate/tract diagnostics remain local. The [initial audit verification](evidence/gov-data-quality-verification.json) and [current summary/annex verification](evidence/gov-data-quality-annex-verification.json) record the respective publication generations and checksums.

## Report layout and automatic updates

The main report starts with an executive summary and presents six findings and three figures in plain language. Essential definitions and limits sit beside the findings. Processing instructions and source links remain in the annex; the main report's single presentation cell is hidden in a validated HTML comment, so ordinary Markdown readers see only its results. The annex retains the original seven cell bodies and explanations; no numerical method, threshold, source input or exclusion changed. The original detailed report is preserved in [an archive](../data/archive/project-tools/gov-data-quality-before-annex-20261007.zip), with a [preservation manifest](evidence/gov-data-quality-annex-preservation.json). The [previous concise version](../data/archive/project-tools/gov-data-quality-summary-before-reader-edit-20261007.zip) is also preserved.

`run gov-data-quality` processes once, then refreshes the annex and main report in that order. `report gov_data_quality --from-saved` refreshes both without processing or acquisition. Report lists deduplicate the annex. A failed annex leaves the main report untouched and returns a nonzero command status; completed processing retains its own status. Each document retains protected, atomic publication. The [initial layout verification](evidence/gov-data-quality-annex-verification.json) and [executive-summary verification](evidence/gov-data-quality-reader-verification.json) record preservation, repeat refresh, figures and pipeline checks.

## Main observations and consequences

| Check | National result | Consequence for the later study |
| --- | --- | --- |
| Counting unit | 134,929 rows, 129,961 project IDs, 230,356 geometry components | Do not count taxonomy rows or points as separate investment decisions. |
| Repeated IDs | 4,968 extra rows across 2,684 multirow IDs; observed disagreements concern taxonomy fields | Preserve multiple classifications; no arbitrary first-row collapse. No conflicting observed budgets/dates/statuses were found. |
| Shared coordinates | 27,953 of 127,081 finite-point project IDs (22.00%) use a coordinate shared by at least 25 IDs; 77 sites meet that threshold | Can dominate nearest-project or inverse-distance results. Co-location alone cannot establish an error or true construction site. |
| Largest exact site | 2,645 distinct IDs at longitude −38.51083, latitude −12.97111 | Inspect source records/provider evidence before treating each ID as a distinct local site. |
| Existing location policy | 224,495 map-eligible components after existing QA/state rules; 126,719 IDs have an eligible point | Eligibility does not certify geocoding. No new filtering occurred. |
| Categories | 25,216 IDs combine an education-description/provider signal with a water/ports category | Heuristic review signal; verify classifications before sector-specific analysis. |
| Actual events | 1,750 IDs have an actual start (1.35%); 1,241 have an actual finish (0.95%) | Registration/planned dates cannot support historical treatment timing by themselves. |
| Completed status | 41,626 of 42,850 IDs marked completed lack an actual finish | Status is not a verified opening date. |
| Investment | 20,532 IDs report R$0.01 (15.80%); 151 report zero | Planned amounts need review before distance weighting; these flags are not verified placeholders. |
| Census, 2022 | 284,994 areas have saved racial shares (99.24%); 256,991 have fully observed race inputs (89.49%) | Missing components can be hidden by preserved zero-coalescing; show coverage sensitivity. |
| Joint census coverage | 256,907 of 287,178 common areas (89.46%) have fully observed race and complete usable income in 2022 | Coverage varies by state; area averages cannot identify individual income by race. |
| Affected known population | 2022 source tracts with missing race components contain 3,821,787 known residents (1.88% of known source population) | Common-area percentages and population percentages have different denominators; missingness need not be random. |

Source-row budgets sum to approximately R$1.115 trillion; one agreed budget per ID sums to approximately R$1.017 trillion. This difference reflects repeated source rows, not newly discovered investment. Both are nominal planned amounts from the snapshot, not validated realised spending.

![National coordinate-sharing review](assets/gov-quality-location-overview.png)

Generated by the command above. Red sites hold at least 25 distinct project IDs; all finite world-range point sites, including quarantined ones, form the background. Seven sites outside the displayed viewport, lines, polygons, empty and invalid points are omitted. Coordinates are unchanged; the map does not locate verified facilities.

![Saved availability versus observed census input coverage](assets/gov-quality-census-coverage.png)

Generated by the same command. The denominator is all 287,178 common areas in each year. Saved racial shares may contain zero-coalesced missing components; complete usable income and fully observed racial inputs are separate checks. Bars do not measure population coverage or racial disparities in proximity.

## Final script audit and verification

The initial national audit passed 154 tests; all eleven figures were reviewed and a clipped axis label corrected. The summary/annex integration passed 165 tests; the executive-summary update passes 181 analytical, audit and report tests, including sixteen hidden-cell checks. Its national command processes once and refreshes all eight cells across both documents. Reprocessing preserves all 32 table hashes and eleven figure hashes; a repeated saved refresh preserves both complete Markdown files exactly. Browser checks confirm the main table, three main figures, 33 annex tables and eleven annex figures render. The main report contains 639 reader-visible words, with no code controls, processing instructions or separate how-to-read section. The two inherited wording checks were updated to recognize plain-language summaries; analytical tolerances were unchanged. Verification records source preservation, publication generations and protected failure behavior separately from scientific validation.

| Audited contract | Fix or verification |
| --- | --- |
| Project counting and source identity | ID/coordinate deduplication avoids taxonomy/component inflation; every source row and component ID is accounted for, and source-row/project identities must match. |
| Geographic contracts | Declared EPSG:4674, recorded geometry types and approved final eligibility are checked; integer flags are converted explicitly before boolean indexing. No CRS inference or coordinate correction. |
| State summaries | Nonstandard DataFrame indexes cannot misalign IDs; conflicting reported states remain explicit instead of selecting the first. |
| Frozen provenance | Contradictory hashes for the same path fail; approved policy, reference bytes and all five original QA outputs are verified. |
| Date screening | The explicit as-of date is inclusive of the full calendar day; same-day timestamps are not flagged as future. |
| Census compatibility | Unique keys, membership counts, common-area universe and harmonisation versions are checked. Inputs are hashed before/after reading. Saved income matches original eligible head-weighted calculations and configured inflation, including missingness (rtol 1e−9; atol R$1e−6). |
| Failure and publication | Processing lock prevents concurrent stage writes; completion is removed before output replacement. Failed/interrupted processing cannot certify a new generation. Protected report execution preserves prior Markdown on failure or concurrent edits; all figures need an interpretation. |
| Scope and acquisition | Municipality scope is rejected before writes. Routine audit/report commands perform no acquisition, models, new exclusions or website publication. |
| Reader-facing execution | Hidden HTML-comment cells retain stable IDs, sequential state, fresh processes and protected publication. Malformed boundaries and embedded comment delimiters fail before execution. Standard Markdown previews hide the source and expose its current findings. |

Remaining uncertainty concerns source validity, not an implementation test result: on-land/in-state points can be wrong; shared sites can be legitimate; category signals and tiny budgets need provider interpretation; parsed dates do not validate original text; census missingness and aggregate definitions limit inference. Distance and regression drafts are preserved as [deferred work](../data/archive/project-tools/planned-proximity/README.md), outside the active pipeline. Review the national diagnostics before choosing the later study population and exposure definitions.
