# IBGE favelas and urban communities, 2022 — codebook

Status: current  
Last updated: 2026-10-27  
Version: 1.0  
Scope: `ibge_favelas_communities_2022.gpkg`, the preserved 2022 IBGE community handoff

The `favelas_2022` layer has 12,348 community polygons in EPSG:4674, one per `community_code`. All seven source values and geometry blobs were preserved; only column **names** changed to English. Codes are identifiers, not numbers to calculate with. `fid` is the GeoPackage row ID; `geom` is the original multipolygon. This file has no population or service-access measure.

| Column | Meaning |
| --- | --- |
| `community_code` | Unique IBGE favela/urban-community code (`cd_fcu`). Keep as text. |
| `community_name` | Original community or favela name (`nm_fcu`); place names are not translated. |
| `state_code`, `state_name`, `state_abbreviation` | IBGE state code, original state name, and two-letter abbreviation (`cd_uf`, `nm_uf`, `sigla_uf`). |
| `municipality_code`, `municipality_name` | IBGE municipality code and original name (`cd_mun`, `nm_mun`). Preserve the code as text. |

The nonspatial `field_dictionary` gives all original-to-English field-name mappings; `export_metadata` records source and code fingerprints. The [runnable notebook](build.ipynb) describes the saved source and verification. No boundary cleaning, splitting, reprojection or newer IBGE release was applied.
