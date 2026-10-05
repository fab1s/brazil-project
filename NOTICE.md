# Sources And Attribution

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Sources And Attribution

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

The original research material was copied from the user's Brazil Project folder in OneDrive. It includes IBGE census data and boundaries, IBAMA environmental licensing geometries, Obrasgov infrastructure records, Belo Horizonte property references, and CS2Nordic research material. Original license and attribution documents are retained where present. This notice does not grant redistribution rights.

Documentation and agent-rule patterns were adapted from the user's RISSI repository, specifically its root AGENTS.md. Brazil remains an independent research project; no RISSI application code, operational defaults, or deployment infrastructure was copied.

Python processing was translated from the user's original R and Quarto workflows. `archive/original_code/` and `docs/reference/workflow_mapping.csv` preserve their provenance.

Retained R packages include censobr, geobr, and sf/S2. Python uses pandas, GeoPandas, Shapely, NetworkX, PyArrow, requests, matplotlib, openpyxl, and Folium. Their own licenses remain applicable. Dependency versions are recorded in the Python and R locks.

Generated interactive maps retain the selected basemap's visible attribution. External basemap tiles may require network access when viewing a map; producing the analysis does not download original research data by default.
