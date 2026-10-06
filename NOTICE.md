# Sources And Attribution

Status: current
Last updated: 2026-10-06
Version: 0.4
Scope: Sources And Attribution

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.4 | Codex | Updated paths and navigation for the simplified project layout. |
| 2026-10-05 | 0.2 | Codex | Recorded original research sources and the existing map browser dependencies. |

The original research material was copied from the user's Brazil Project folder in OneDrive. It includes IBGE census data and boundaries, IBAMA environmental licensing geometries, Obrasgov infrastructure records, Belo Horizonte property references, and CS2Nordic research material. Original license and attribution documents are retained where present. This notice does not grant redistribution rights.

Documentation and agent-rule patterns were adapted from the user's RISSI repository, specifically its root AGENTS.md. Brazil remains an independent research project; no RISSI application code, operational defaults, or deployment infrastructure was copied.

Python processing was translated from the user's original R and Quarto workflows. `data/archive/original_code/` and `docs/evidence/workflow_mapping.csv` preserve their provenance.

Retained R packages include censobr, geobr, and sf/S2. Python uses pandas, GeoPandas, Shapely, NetworkX, PyArrow, requests, matplotlib, openpyxl, and Folium. Their own licenses remain applicable. Dependency versions are recorded in the Python and R locks.

Generated interactive maps retain the selected basemap's visible attribution. External basemap tiles may require network access when viewing a map; producing the analysis does not download original research data by default.

`website/` preserves browser source from the user’s existing here.now map. Its pinned browser vendor files have upstream license texts retained under `website/vendor/`: MapLibre GL JS (BSD 3-Clause), PMTiles (BSD 3-Clause), and Lucide (ISC). Website project/community data derivatives are frozen from the existing publication and excluded from Git; this does not establish a new dataset license.

Location-quality preprocessing uses [IBGE municipal mesh 2022](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/) and [Natural Earth land](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/) and [coastline](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-coastline/). Downloaded archives retain accompanying attribution and metadata; their manifest records exact versions, URLs and checksums. Natural Earth coastlines are generalized and omit some small islands; reference resolution is not a guarantee of positional accuracy.
