# Current Project Progress

Status: implemented and validated with recorded limitations
Last updated: 2026-10-06
Version: 0.7
Scope: Current Project Progress

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.7 | Codex | Recorded national Obrasgov location QA and reproducible derivatives. |
| 2026-10-05 | 0.6 | Codex | Recorded Obrasgov map display changes and location review. |

The complete original file collection is copied, organized, and checksum verified. The Python package and CLI are installed locally. Python dependencies and retained R dependencies are locked.

Python annual indicators and conference chart populations are implemented, and national outputs have been generated. Infrastructure snapshot processing is implemented; Obrasgov retains 133,417 records after cleaning, matching the original snapshot. IBAMA includes 8,494 records with translated sectors. Land-value annex imports and the available zone geometry are implemented; the exact cadastral input remains missing.

All 13 indicator calculations and conference chart populations match a fresh original R reference on complete common areas intersecting Belo Horizonte. Prepared geometry boundaries agree within the original one micrometre precision grid; the historical local R matcher’s point-only contact intentionally differs under the approved positive-area policy. Twelve national stored indicator outputs match; the remaining density absolute-change discrepancy is documented in [results](../verification/results.md).

The spherical overview preserves R sf/S2 and produces original comparison classifications and example maps. All nine Python-backed reports execute in fresh processes and render to HTML under `outputs/reports/notebooks/`; their 102 local asset references resolve. The original 36 analytical/map tests are joined by 15 location and utility tests; all 51 pass. National crosswalk recomputation and live external harvest parity are not declared validated. The original Linha Verde overlay is absent and is reported without substituting another geometry.

The [harmonisation update](../verification/harmonisation-update.md) addresses the audit findings: positive-area matching, complete groups, atomic versioned geometry/lookup bundles, merged analytical polygons, unique part IDs, and unmatched coverage inventories. The researcher accepts the documented boundary-change assumption; footprint diagnostics remain available and do not block groups automatically. National baseline processing has been regenerated under this policy. Explicit full-national geometric recomputation has not been run as part of this update.

The maintained here.now map source is under `website/`. Its census export has 287,178 merged common areas, all 13 indicators, 17 vector archives, and unmatched coverage summaries. Numeric exports match the research tables after existing map presentation exclusions. Existing infrastructure/community assets are preserved from the previous map publication. Build and browser verification are recorded in [the map update](../verification/web-map-update.md).

Obrasgov polygons are excluded from map rendering and picking at researcher request; source records and investment summaries remain preserved. Points and lines remain visible. [Initial location screening](../verification/obrasgov-spatial-review.md) found 46 illustrative offshore point components from 38 projects; this is not a national coastline classification. No point locations have been corrected or removed.

The national [Obrasgov location preprocessing](../verification/obrasgov-location-qa.md) is implemented and verified independently of faithful snapshot translation. All 134,929 source rows and original geometry/attributes are preserved. Recursive decomposition yields 230,356 components: 226,309 eligible point/line components, 2,037 quarantined components and 2,010 polygon components excluded from map output. Suspicious offshore locations account for 428 components across 236 project IDs. Coastal, foreign-border, marine-description and administrative uncertainty is flagged rather than silently resolved. No coordinates are corrected.

Two fresh CLI runs have identical contracts and all five GeoParquet hashes; source attributes and geometry WKB match exactly, and map/quarantine partition and source-row investment coverage checks pass. The full suite passes 51 tests, including 11 location QA tests. The snapshot contains 4,968 repeated-ID rows, and source-row investment sums are explicitly separated from a consistent-ID budget diagnostic. The public map still uses its previous frozen point/line archive; the new GeoPackage is a local reviewed-software derivative, not a live-map publication or scientific certification.

The concise [process record](obrasgov-location-qa-process.md) includes commands, recorded outputs and the embedded generated figure. The completed [script audit](../verification/obrasgov-location-qa-script-audit.md) records utility fixes and remaining limitations; future agents must maintain these records under the updated root AGENTS.md.
