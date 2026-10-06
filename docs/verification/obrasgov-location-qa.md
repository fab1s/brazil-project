# Obrasgov Location Preprocessing Verification

Status: implemented; national execution, exchange and repeat checks verified
Last updated: 2026-10-06
Version: 0.1
Scope: National location diagnostics and separate map eligibility derivative

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.1 | Codex | Implemented conservative component location checks and documented verification. |

The stage follows [the location policy](../methods/obrasgov-location-policy.md). It reads the original frozen map GeoPackage, not the translated cleaned snapshot, and preserves all source rows and investment values. It recursively decomposes collections, checks finite/range/validity constraints, intersects IBGE municipalities and states, screens land/coastal position, checks every line vertex plus interpolated samples, flags marine descriptions, and exports separate eligible and quarantined locations.

References were explicitly acquired from [IBGE municipal mesh 2022](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/) and pinned Natural Earth release 5.1.1 archives for [land](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/) and [coastline](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-coastline/). [Reference provenance](../reference/location-qa-references.json) records exact URLs, checksums and archive metadata. The coastline archive within release 5.1.1 contains an internal version label `5.0.0-pre9`; the archive checksum is the identity used for processing. Zip archives preserve accompanying metadata. Checksums are verified before routine offline runs. Natural Earth coastlines are generalized and omit some small islands; IBGE-covered islands take precedence.

## Checks

Eleven focused tests pass: recursive collections/duplicate project IDs/source preservation; offshore/marine/coastal/foreign land/island policy; shared municipal/state boundaries and explicit municipality codes; missing/empty/out-of-range/nonfinite locations and CRS rejection; and offshore line excursions despite onshore endpoints. Additional tests cover missing local references, explicit threshold changes, broad taxonomy/place-name false marine exceptions, and nullable metadata. Further tests cover foreign-border uncertainty and exact coastline distances after segment indexing. The full project suite passes 51 tests. Two fresh CLI runs produce identical contracts and all five byte-identical GeoParquet outputs; all results agree except generation timestamps. Source geometry WKB and original attributes match exactly; map/quarantine geometry provenance, partition completeness and source-row investment coverage pass. The [evidence](obrasgov-location-qa-evidence.json) records counts, hashes and exchange checks.

## Output contract

`data/intermediate/obrasgov-location-qa/` contains:

- `source_audit.parquet`: every source row with unchanged geometry and attributes, component counts and eligibility coverage.
- `component_audit.parquet`: stable source-row/component IDs, unchanged component geometry, diagnostic flags, sampled coastal distances, intersected municipalities and eligibility reasons.
- `map_components.parquet`: eligible point and line components with original project attributes and flags.
- `quarantined_components.parquet`: suspect location components preserved for review.
- `review_table.parquet`: non-default component decisions and source attributes without geometry.
- `report.json`: input, code, policy and reference fingerprints, counts, coverage, investment summaries and output hashes.

`outputs/maps/obrasgov-location-qa/locations.gpkg` exposes eligible and quarantine layers. `review.csv` provides a filterable per-component review table. Investment summaries are based on original source rows, not repeated component attributes. Duplicate IDs and unknown investment amounts remain explicit. The public website still uses its prior frozen point/line archive; no new geographic policy is silently applied there.

## Limits

This is location screening, not independently verified geocoding. No coordinates are corrected, swapped or inferred. Marine descriptions indicate plausibility requiring review. Coastal and border tolerances are conservative screening parameters. Line paths are sampled, and capping is flagged; all original vertices are still checked. Polygons receive coordinate/validity diagnostics and remain excluded from map output; they are not treated as validated footprints. The source snapshot has no structured municipality code, so description-derived municipal claims are not validated automatically. Administrative boundaries are a 2022 reference, not a date-specific reconstruction for historical works.

## National results

| Diagnostic result | Components |
| --- | ---: |
| Eligible, coordinates unverified | 224,103 |
| Administrative/coordinate review retained | 2,063 |
| Coastal review retained | 75 |
| Foreign-border review retained | 62 |
| Possible marine review retained | 6 |
| Quarantined missing/invalid/range/domain locations | 1,523 |
| Quarantined suspicious offshore locations | 428 |
| Quarantined outside Brazil on foreign land | 86 |
| Polygons excluded by display policy | 2,010 |
| Total recursively decomposed components | 230,356 |

The clean point/line derivative contains 226,309 components; quarantine contains 2,037. Far-offshore flags involve 236 distinct project IDs. There are 509 components with offshore samples, including retained coastal or possible marine locations. Components are not project counts. Lines may be quarantined because part of their path is suspect; complete source geometry remains available.

There are 134,929 source rows but 129,961 distinct project IDs. The 4,968 repeated-ID rows remain. All reported amounts agree within each project ID in this snapshot. Source-row sums are preserved separately from a one-amount-per-consistent-ID diagnostic; neither is declared an independently verified budget. Source-row coverage totals agree within relative tolerance 1e-12. No coordinates are corrected.

The [point overview and process record](../current/obrasgov-location-qa-process.md) was rendered and visually inspected. It preserves point coordinates, distinguishes review from quarantine, and deliberately omits lines, polygons and invalid locations. The eligible point/line GeoPackage exchange was checked separately from the overview.

Reproduce verification and the illustration:

```bash
.venv/bin/python scripts/verify_location_qa.py --output .cache/obras-spatial-audit/verification.json
.venv/bin/python scripts/plot_location_qa.py
```

The [post-implementation script audit](obrasgov-location-qa-script-audit.md) records fixes to plotting provenance, acquisition-manifest recovery and optimized-Python verification. These utility fixes do not change analytical eligibility or the completed national producer contract.
