# Obrasgov Spatial Review

Status: initial screening; display change published and verified
Last updated: 2026-10-05
Version: 0.1
Scope: Obrasgov geometry display and exploratory coordinate-quality screening

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.1 | Codex | Removed Obrasgov polygons from display and screened suspicious locations. |

## Implemented display decision

All Obrasgov polygon components are excluded from rendering and feature picking. Point and line components remain, including those in mixed records. This policy is applied when layers are created and survives visibility toggles and background replacement. IBAMA polygons, census areas and community polygons are unaffected. The frozen archives and research source remain intact. Interface counts and investment summaries explicitly describe source records, including projects whose polygon locations are not displayed. This is a display decision, not a methodological exclusion from research totals.

Local browser checks covered point/line layers, absence of the polygon layer, toggle off/on, Light and OpenStreetMap backgrounds, retained IBAMA fill layers, merged census features, overview/mid/detail zooms, common-ID search, income, density change, summaries and mobile viewport. There were no page errors or failed HTTP responses. Equivalent live-site checks passed with zero page errors or failed HTTP responses; all 121 published asset hashes match the local build. [Map evidence](obrasgov-map-evidence.json) records both runs. Published version: `01M466S499KKFR6X9WY7QDQEMM`. The publication helper uploaded four changed browser files and skipped 117 unchanged files, preserving frozen archives.

## Read-only screening

Input: `data/processed/obrasgov/projects_st.gpkg`, layer `projects_st`, 134,929 source records, declared EPSG:4674. These are the original frozen map inputs; the research cleaner's 133,417 retained records are a different derivative. This display update does not substitute one for the other.

| Source geometry | Records |
| --- | ---: |
| MultiPoint | 132,636 |
| MultiPolygon | 1,493 |
| MultiLineString | 638 |
| GeometryCollection | 162 |

Three source records have geometry bounds outside valid longitude/latitude ranges. The declared geographic CRS is incompatible with those numeric ranges: overall bounds extend to approximately −6.5 million longitude and −8.9 million latitude. This warrants per-record investigation of units, metadata or corrupt coordinates. It does not establish a replacement CRS for those records.

One-level extraction identified 202,653 finite point components within longitude/latitude ranges. Two illustrative offshore boxes, `(lon > -37 and lat < -15) OR (lon > -47 and lat < -25)`, selected 46 point components belonging to 38 distinct project IDs. These boxes are examples, not an exhaustive or authoritative coastline test. Extraction does not establish completeness of nested geometry collections, and repeated coordinates are counted as components.

Examples needing review:

| Project ID | Description / declared state | Longitude | Latitude |
| --- | --- | ---: | ---: |
| 16112.27-86 | Urban paving / AL | −35.29666 | −24.47633 |
| 91784.21-76 | Household sanitation in Feira Nova do Maranhão / MA | −43.42342 | −28.44879 |
| 94736.42-35 | Household sanitation in Garopaba / SC | −28.07074 | −28.07074 |
| 39745.43-46 | Paving and drainage in Butiá / RS | −30.12606 | −30.12606 |

The project descriptions, state mismatch and identical latitude/longitude in some examples suggest individual location-entry errors. This is an inference, not a verified correction. No point has been moved or removed. The [official Obrasgov manual](https://www.gov.br/transferegov/pt-br/obrasgov/doc/manualdousuarioobrasgovbr2023_v1.8.pdf) specifies geographic longitude/latitude in decimal degrees with SIRGAS2000. Reprojecting all records would not repair a latitude copied into the longitude field.

Reproduce this initial screen without changing inputs:

```bash
.venv/bin/python scripts/audit_obras_locations.py --output .cache/obras-spatial-audit/recheck.json
```

[Screening evidence](obrasgov-spatial-screen.json) records the exact source checksum, extraction scope, bounds, range flags, counts and sample IDs. The script produces a diagnostic report only; its boxes must not be reused as a deletion rule.

## Proposed preprocessing, not yet implemented

1. Preserve original coordinates, CRS metadata, IDs and acquisition provenance. Store any reviewed coordinates separately, with reason, evidence and version.
2. Classify missing, nonfinite, out-of-range, empty and invalid geometries; extract collections recursively before assigning per-component flags.
3. Compare valid-degree locations with authoritative national, state and municipal boundaries, including islands. Measure coastal distance in a suitable metric CRS and retain the original geography.
4. Review offshore flags using project descriptions and geometry context. Ports, waterways and other marine works can be valid offshore; declared state or municipality is supporting evidence rather than an automatic correction.
5. Quarantine locations confirmed unreliable from geographic analyses or a future map default while keeping the project in nonspatial totals with an explicit location status. Record affected counts and investment amounts separately.
6. Correct only from verified provider coordinates or evidence establishing the actual original CRS. Never infer a CRS from magnitude alone, silently swap axes, snap points to the shore, or present municipal centroids as exact project locations.

A national coastline/state/municipality audit, reviewed exclusion policy and verified corrections remain outstanding. This screening supports review; it does not validate all retained locations.
