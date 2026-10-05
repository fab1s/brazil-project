# Harmonisation Pipeline Audit

Status: historical audit; see implemented remediation
Last updated: 2026-10-05
Version: 0.2
Scope: Census correspondence, common-area geometry, aggregation, and reuse of stage artifacts

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.2 | Codex | Preserved the audit findings and linked their implemented remediation. |

The [implemented remediation](harmonisation-update.md) addresses the requested code and output changes. The findings below describe the pre-update implementation; footprint disagreement remains a diagnostic under the researcher-approved assumption.

## Assessment

Counts and indicators are aggregated by `common_id`. Exported spatial indicators keep the prepared 2022 tract pieces, repeating their common-group values. A common-group geometry is dissolved temporarily for density, but no reusable dissolved comparison-area layer is published. This preserves the original migration contract; it is an output limitation if research consumers expect one polygon feature per comparison group.

The more serious issue is that connected components of the bidirectional largest-overlap graph do not guarantee equal geographic footprints in both years. Dissolving the 2022 pieces alone does not establish geographic comparability. Two implementation problems also affect municipality recomputation: incomplete boundary groups and reuse of stale density geometry.

No analytical implementation, source data, or generated research output was changed during the audit. Evidence is recorded in [harmonisation-audit-evidence.json](harmonisation-audit-evidence.json).

## Findings

### 1. High: recomputation can reuse incompatible density geometry

In `src/brazil_project/harmonisation/census.py`, baseline municipality runs write `comparison_geometry.parquet`; recomputed runs neither replace nor invalidate it. Both modes share the same municipality artifact directory. `src/brazil_project/indicators/temporal.py` selects this file based on existence alone.

Existing Belo Horizonte baseline comparison geometry has 3,790 group IDs. The recomputed reference has 3,781 group IDs, with zero ID overlap. Switching from baseline to recomputed harmonisation in that directory would leave density using the wrong area lookup, producing missing areas for these new group IDs. On other inputs, coincident numbering could associate an area with an unrelated group. This is a confirmed artifact-contract defect; the deliberately incompatible indicator run was not executed against production outputs.

Recommendation: separate artifacts by correspondence version/mode, replace the complete comparison geometry on every successful run, and validate its provenance and group membership before consumption. Publish a complete stage only after all related artifacts are ready.

### 2. High: municipality recomputation excludes contributors and changes groups

The recomputed branch filters both source years by municipality before matching. The baseline branch instead selects complete national groups touching the requested display area. These operations implement different research scopes.

Complete groups touching Belo Horizonte contain nine 2010 tract rows and 15 2022 tract rows outside the municipality. Municipality-only recomputation merges nine sets of originally separate baseline groups among the in-city 2022 tracts. The original national groups are therefore not merely being relabelled.

Recommendation: derive a subset from a complete versioned correspondence, or expand the matching region until contributing groups are complete. Record an explicitly clipped local method as a separate analytical choice if desired.

### 3. High methodological risk: common IDs do not guarantee common footprints

`largest_overlap` keeps only one candidate per source geometry row in each direction. Secondary positive overlaps may connect tracts assigned to different common IDs. A `1:1` classification describes membership counts and does not mean unchanged boundaries.

For 3,790 complete baseline groups touching Belo Horizonte, using prepared source geometries in EPSG:5880:

- Median footprint difference is 2.01%; the 95th percentile is 20.78% and maximum is 62.93%.
- 2,441 groups exceed 1% difference and 502 exceed 10%.
- There are 12,283 cross-group old/new intersections above 1 m², totalling approximately 5.66 km² of pairwise intersection area. This sum is a diagnostic, not an estimate of distinct affected land area.

Footprint difference is `area(symmetric_difference(union_2010, union_2022)) / area(union(union_2010, union_2022))`. It measures disagreement, not the cause of that disagreement. Source boundary corrections can contribute alongside real boundary changes. The audit did not establish national footprint error rates.

Consequently, common-group indicator changes can combine demographic change with geographic coverage differences. Density uses the 2022 group footprint for both populations, which needs an explicit analytical justification when the 2010 footprint differs.

Recommendation: publish unions for each year and diagnostics for coverage, spillover, and footprint agreement. Evaluate alternative correspondence/aggregation methods separately from faithful translation. Including every positive overlap can create large chains through slivers; it should not be adopted without sensitivity checks.

### 4. Medium output gap: no dissolved common-area product

`correspondence` attaches group attributes to the individual 2022 geometries. The harmonisation runner saves `base_geometry_2022`; indicator export joins group values back to those geometries. Only the density calculation dissolves by common ID, and its geometry is discarded after computing area.

Nationally, 94,644 groups contain more than one distinct 2022 tract. Maps can therefore display internal tract boundaries within a single analytical observation. Consumers counting features or summing repeated common-area totals would overcount.

Recommendation: retain the existing display layer and additionally publish a dissolved 2022 common-area layer with one record per `common_id`, group membership, coverage diagnostics, and clearly named attributes. Where a group has disconnected pieces, a single feature can legitimately be a MultiPolygon. Distinguish this output enhancement from changing how groups are constructed.

### 5. Medium: boundary contacts count as correspondence, with a Python/R edge-case difference

The candidate predicate is `intersects`, and there is no positive-area filter. A synthetic pair of polygons sharing only an edge is assigned a common ID and classified `1:1`, despite having zero overlap area. This contact behavior is also present in the original R method; rejecting it would be a methodological change.

A separate translation discrepancy is confirmed: when every candidate intersection is lower-dimensional, installed R `sf::st_join(largest=TRUE)` ranks by intersection length. Python always ranks by area and then target row order. In a synthetic example, contacts of lengths one and two metres cause Python to choose the first, shorter contact while R chooses the longer contact. Ordinary positive-area matching is not affected by this particular example. No national prevalence was estimated.

Recommendation: explicitly define dimensional eligibility and distinguish a faithful R ranking fix from a proposed positive-area matching rule. Report low-overlap and contact-only matches.

### 6. Medium: unmatched tracts silently leave the analytical universe

National raw-to-lookup comparison finds 16 unmapped 2010 IDs and 24 unmapped 2022 IDs. The display base contains 42 rows without `common_id` because some IDs have multiple geometry pieces. Graph construction includes only matched vertices; aggregation drops missing common IDs.

The harmonisation stage reports totals and repeated IDs, but does not publish an unmatched-tract inventory or the population/household coverage excluded from comparison. Zero missing common IDs in the lookups themselves does not prove complete source coverage.

Recommendation: publish unmatched IDs, geometry status, exclusion reasons where established, and affected indicator denominators. Keep exclusion explicit rather than silently filling missing comparisons.

### 7. Medium: repeated IDs represent geometry parts, and identifiers are not feature-unique

The national base has 472,778 rows but 468,097 distinct tract IDs. There are 914 repeated tract IDs covering 5,595 rows, accounting for 4,681 additional rows. None of these groups consists entirely of topologically identical geometries. Of the repeated IDs, 907 have nonidentical pieces without significant overlap; seven have overlapping pieces at the audit threshold (overlap fraction greater than 1e-8). These overlaps are small: approximately 0.51–74.73 m² per affected tract, with a maximum overlap fraction of approximately 0.00618%; the audit does not establish that they are scientifically material.

Deduplicating by tract ID would discard geometry. Numerical aggregation already deduplicates tract-to-group keys, which is appropriate. However, `base_id = 't2022_' + id_2022` repeats across pieces and is unsuitable as a unique feature key. A recomputed repeated tract can also accumulate graph links from multiple geometry rows, which should be documented as a part-level matching rule.

Recommendation: preserve all pieces, distinguish tract IDs from geometry-part IDs, inspect the seven overlapping-piece cases, and use geometric union when deriving area. Do not interpret every repeated ID as an erroneous duplicate.

### 8. Medium: validation establishes translation parity, not harmonisation quality

All 18 existing tests pass. Prior R comparisons establish Belo Horizonte overlap-pair and component parity; national stored indicator comparisons mostly establish consistency with archived calculations. Neither check proves equivalent common footprints, stable component identifiers, complete national recomputation, or safe switching between correspondence modes.

Component IDs are sequential encounter-order labels. Reordering source rows or changing the matching scope can relabel groups, and largest-overlap ties are input-order dependent. Existing files lack a versioned group identity or sufficient artifact fingerprints to prevent accidental mixing. The runner also does not reconcile the imported display geometry, lookup memberships, and group-size table as one contract before publishing them.

Recommendation: add focused checks for mode switching, subset boundaries, boundary-only candidates, output common-area uniqueness, unmatched coverage, footprint agreement, and input-order sensitivity. Compare membership independently of arbitrary numbering; persist a correspondence version or membership fingerprint. Keep national recomputation marked unverified until checked.

## Evidence and scope

The audit reads the copied tract GeoPackage, original lookup GeoPackage, base geometry, group-size CSV, and existing regional reference artifacts. National checks cover identifier assignments, group sizes, coverage, municipality membership, and repeated geometry parts. Regional footprint calculations select complete baseline groups touching 2022 Belo Horizonte display tracts, read every contributing source tract, apply the existing preparation routine, and dissolve independently by year. Synthetic probes exercise zero-area contacts, secondary overlaps, and the R length-ranking fallback. Existing tests were rerun with `.venv/bin/python -m pytest -q`.

The national lookup has no tract assigned to multiple common IDs, and its stated per-year group sizes match the distinct lookup memberships. Those checks passed. Acquisition, the live website implementation, and full national geometric recomputation were outside this audit.

## Suggested order of work

1. Repair stale artifact selection and establish complete, versioned geometry/lookup contracts.
2. Correct or explicitly isolate municipality-only recomputation scope.
3. Add a dissolved common-area output and unique part-level feature IDs while retaining the original display layer.
4. Publish coverage and footprint diagnostics, including unmatched and low-overlap cases.
5. Review any change to the largest-overlap research method separately, using sensitivity analysis before regenerating validated results.
