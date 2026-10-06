# Obrasgov Location Quality Policy

Status: implemented; national execution and repeat checks verified
Last updated: 2026-10-06
Version: 0.1
Scope: Separate location-quality preprocessing; no changes to faithful snapshot translation

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.1 | Codex | Recorded the requested location checks and conservative spatial-output policy before implementation. |

The researcher requested the full preprocessing proposed after offshore records were identified. This is a new diagnostic and display derivative, not a replacement for original infrastructure processing or research totals. Original coordinates, geometries, IDs, declared CRS and acquisition provenance remain immutable. No coordinate corrections, axis swaps, shore snapping or inferred reprojection are authorized by this policy.

Routine `obrasgov-location-qa` uses explicit local references. Acquisition is a separate script. IBGE municipality mesh 2022 supplies country, municipality and state coverage including its mapped islands. Natural Earth land and ocean coastline at 1:10 million provide approximate offshore screening and coastal distances. They are generalized screening references; small islands and fine coastal detail may be absent. An IBGE-covered point takes precedence over Natural Earth land coverage.

Recursive geometry decomposition gives each source row and component a stable ordinal, preserving repeated coordinates and duplicate project IDs. Missing, empty, invalid, nonfinite and out-of-range geometry are diagnosed separately. Polygons stay excluded from the map by the prior display instruction; they remain in the audit and original geometries. Point and line components receive location checks. Lines are assessed across vertices and a sampled path; long lines spanning countries or water are reviewed rather than assumed wholly onshore from their centroid.

Geographic flags use `intersects`, retaining all candidate municipalities at shared boundaries. Explicit municipality codes are checked when a documented code field is available. Municipality names inferred from descriptions are not treated as reliable IDs. The existing snapshot has no structured municipality code; this limitation is reported. `uf_principal` is supporting context; a mismatch alone does not exclude a location because projects may cross states.

The default cleaned map derivative quarantines nonfinite/out-of-range/invalid point and line components; locations outside Brazil on foreign land more than 1 km from its administrative coverage; and components wholly offshore beyond 5 km from both mapped IBGE coverage and the generalized coastline without a marine-description signal. Close coastal and foreign-border locations remain with uncertainty flags. Thresholds are explicit, configurable screening tolerances, not proof of source accuracy. Components spanning good and suspect positions are quarantined for review; endpoints alone never establish eligibility.

Marine signals come from specific description terms (e.g. offshore, port infrastructure, dredging, navigation works), not broad taxonomic categories, which can be inconsistent. These produce `possible_marine_review`, never a validated marine classification. Their locations remain visible in the conservative derivative with review flags. A reviewer can establish marine validity or correction using provider evidence in a later version.

Project-level reports preserve every source row and investment total. Component investment amounts are never summed because multi-location projects repeat the same record attributes. Quarantined and retained amounts are reported by source row, with mixed-location rows counted separately. Missing amounts and duplicate IDs are explicit. Geographic statistics must use eligibility/status fields and cite the policy version. Nonspatial project totals remain unchanged.

Outputs include the complete row audit with original geometry; recursive component audit with unchanged source geometry; clean point/line map components; quarantined components; review tables; and a report containing input/reference/policy fingerprints, counts, investment coverage, limitations and repeat-execution checks. Exporting an eligible subset does not declare its coordinates validated. The public website must identify any derivative it adopts; publishing is verified separately from preprocessing.

The source contains repeated project IDs. Source-row investment totals preserve the original snapshot and may count the same project amount more than once. A separate diagnostic reports each distinct ID once only when its reported amounts agree, and explicitly counts conflicting or entirely missing amounts. This diagnostic does not silently consolidate source rows or certify the budgets.

The metric screening domain is 80°W–25°W and 40°S–10°N, enclosing Brazil and its mapped offshore islands. Locations outside this domain are provisionally quarantined with `outside_screening_extent`, not reprojected or declared invalid geographic coordinates. The coastline is clipped with a surrounding margin for distance calculations. These checks concern longitude/latitude; no altitude validity claim is made.
