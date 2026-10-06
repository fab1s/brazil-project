# Harmonisation Policy Change Record

Status: approved and implemented; regional verification complete
Last updated: 2026-10-06
Version: 0.2
Scope: Changes from the faithful original translation to the active harmonisation policy

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.2 | Codex | Updated paths and navigation for the simplified project layout. |
| 2026-10-05 | 0.1 | Codex | Recorded the researcher-approved harmonisation changes separately from translation. |

On 2026-10-05 the researcher approved the changes discussed in the [audit](harmonisation-audit.md). The original code, lookups, geometry, and results remain unchanged in their preserved locations. The active policy is `positive-area-common-geometry-v1`.

## Matching and subsets

Bidirectional largest overlap and connected components remain the comparison method. Polygon intersection area must be finite and strictly greater than zero. Line and point contacts are not eligible; there is no arbitrary positive-area minimum or geographic-distance fallback. Equal positive overlaps retain the original target-row tie rule. This is an intentional methodological change from the original R contact behavior, not an assertion of identical results on every dataset.

Imported baseline edges are checked using complete source geometry pieces. An edge is eligible when any pair of source pieces has positive polygon overlap. Rejected edges are saved with their reason, and connected components and relationship counts are recalculated. Unchanged baseline components retain their IDs; changed components receive a stable hash of their sorted year-prefixed members.

Imported municipality processing starts from complete components of the national baseline. Since edge rejection can only split those components, validation can be cached for that complete component selection. Final groups are selected through their 2022 municipality membership. Explicit geometric recomputation always uses all national geometries, caches the result against source/configuration fingerprints, and selects municipality groups afterwards. It must never match clipped municipal inputs.

## Common geometry and display

The analytical spatial unit is `common_id`. Complete matched 2022 pieces are dissolved into one feature per group, including contributors outside a requested municipality. Thus a selected group can extend outside the municipal boundary. Cropping these features would change the analytical footprint and must be requested separately.

Original prepared tract pieces remain in reference outputs. `part_id` uniquely identifies each piece within a bundle; `id_2022` identifies the tract and is not a unique geometry-feature key. Unmatched tracts and geometry pieces are published separately and are not forced into neighbouring groups.

Density preserves the original numerical operation order: repair pieces, transform each piece to EPSG:6933, dissolve by group, then measure area. The group display geometry is dissolved in the configured correspondence CRS. Projecting its already-dissolved shape is not used to recalculate the density denominator.

## Accepted assumption and diagnostics

Boundary differences between years are assumed not to materially change the inhabited population being compared, because the researcher expects differences to occur mainly in uninhabited areas. This is an explicit research assumption rather than a verified spatial fact. Yearly union areas and symmetric-difference fractions are published for review, not used as automatic cutoffs. Matching counts alone do not establish footprint equivalence.

## Coverage and artifact contract

Each run reports matched and unmatched IDs, available population/household totals, missing values, and the unmatched share of known totals. A missing value is not treated as zero. For municipal runs the reporting universe comprises the complete selected groups, originally unmatched tracts in the municipality, and contributors losing correspondence within the validated component selection.

A complete generation contains lookups, memberships, group counts, merged geometry, tract references, unmatched inventories/geometries, diagnostics, and checksums. Publication atomically switches a `current.json` pointer only after all artifacts are written. Consumers check checksums, source/configuration fingerprints, scope, mode, and membership counts. Legacy loose geometry files cannot override the selected generation.
