# Research Processing Methods

Status: current
Last updated: 2026-10-06
Version: 0.3
Scope: Research Processing Methods

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.3 | Codex | Separated geographic quality filtering from translation. |
| 2026-10-05 | 0.2 | Codex | Recorded the harmonisation corrections and approved research assumptions. |

## Census correspondence

The original method transforms 2010 and 2022 tracts to EPSG:5880, sets precision at 1e6, and makes geometry valid. Each year selects its largest strictly positive polygon-area overlap in the other year. Edge-only and point-only contacts are excluded under the approved updated policy. The union of both directional match sets forms an undirected graph; connected components define common comparison areas. Relations are classified as one to one, split, merge, or many to many.

The reference tract base preserves all prepared 2022 geometry pieces. Active analytical spatial outputs dissolve the complete 2022 pieces by `common_id` and contain one feature per group. Disconnected pieces remain a MultiPolygon. Unmatched tracts are saved separately. Unchanged imported groups retain their original IDs; new or changed groups use member-derived identifiers. Membership remains the invariant. The default validates imported national correspondence edges for positive overlap; explicit recomputation matches nationally before any municipality selection.

The original national base contains 4,681 duplicate IDs among 472,778 rows. These geometry pieces remain present in reference outputs, with unique `part_id` values. They are not necessarily erroneous duplicates. Aggregation deduplicates each tract-to-common-area key before summing, preventing those display duplicates from multiplying counts.

The researcher accepts the assumption that differences between yearly group footprints do not materially change the inhabited population being compared. This assumption has not been independently verified against habitation data. Footprint diagnostics remain available and are not used as automatic rejection thresholds. See the [policy change record](harmonisation-policy.md).

## Annual proportions

Black, Brown, combined Black/Brown, literacy, rudimentary sanitation, water network, waste collection, sewer/septic, houses, village/condominium houses, and apartment indicators retain their original census variable mappings in the Python implementation.

Combined temporal counts coalesce specified missing components to zero. Most temporal aggregations ignore missing count entries; housing denominators remain missing when every denominator is missing. Ratios require positive denominators. Annual estimates are joined with an outer join; an absent year is not replaced by zero. Changes in proportions are differences and percentage-point values are those differences multiplied by 100.

Literacy uses the 2022 Pessoas table's own tract population, independently of whether the Basico table contains that tract. This distinction was verified against the original R implementation.

## Income

2010 income uses V020 household heads, V021 recipients, and V022 total income. Its tract mean is total income divided by valid positive recipients. The 2022 inputs use V06001 heads and V06004 mean income.

The implemented original aggregation weights valid tract means by household heads. Numerator and denominator use exactly the same eligible pairs. Missing weights and means are reported; incomplete coverage does not itself block the mean. Nominal 2010 results are multiplied by 6645.74 / 3200.06 to express July 2022 reais.

The original prose claims stronger restrictions on multi-tract means than its code actually imposes. The migration preserves the code and records the discrepancy rather than changing the method.

## Population density

Counts retain missing totals when every contributing value is missing. Component polygons are repaired, transformed to equal-area EPSG:6933, and dissolved to measure common-area km2. Density equals population divided by area. Absolute change is people per km2; relative change is the percentage change from a positive 2010 density.

The stored original population_density_change column repeats percentage changes rather than the absolute difference used by current source code. Both stored outputs and current source are retained. Fresh R reference validation determines translation parity.

## Conference sanitation charts

Unlike temporal rudimentary sanitation, conference inadequate sanitation includes no bathroom or toilet and excludes a tract from both numerator and denominator when any required component is missing or invalid. A group's 2022 component tracts must all be urban.

The change chart requires eligible data in both years. Racial-composition quintiles use paired 2022 areas, ordered by share then common_id, with larger ntile buckets first. The income chart independently uses all eligible urban 2022 areas; income tertile cutoffs are calculated before selecting the lowest and highest racial quintiles. Income intervals are right closed.

## Infrastructure and land value

IBAMA merges licensed point, line, and polygon records and translates sectors. Obrasgov expands taxonomy, sums planned investments, combines project pins, enriches available multidimensional geometries, translates categories, and removes empty or out-of-range geometries before repairing retained geometries.

Property processing remains exploratory. Its valuation workbook was parsed using AI in the original project and has not been independently authenticated. Exact dated inputs are required; no alternate date is substituted.

## Geographic overview

The original exploratory 2000-to-2010/2022 comparison is limited to Belo Horizonte. It classifies older tracts using overlap fractions of newer tracts: greater than 5 percent establishes a substantial match; a single match over 95 percent is stable. The sf/S2 adapter retains original geographic topology and area semantics.

## Original tract exploration

The original exploratory Black population maps cover Belo Horizonte, Vespasiano, São José da Lapa, Confins, Lagoa Santa, and Santa Luzia in Minas Gerais. These use raw annual tract ratios and the original share bands, separate from harmonised temporal estimates. The optional Linha Verde shapefile is absent from the source; the overlay is not reconstructed or substituted.

## Obrasgov location-quality derivative

The requested [location policy](obrasgov-location-policy.md) defines an independent diagnostic/map preprocessing stage. It retains all source project rows and investments, preserves coordinates and the prior translated snapshot, and writes component eligibility and review flags. Offshore status is screened with IBGE municipalities and generalized Natural Earth references. Eligibility is not verified coordinate accuracy; no automatic coordinate correction is performed.
