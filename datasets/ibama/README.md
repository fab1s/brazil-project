# IBAMA licensing records

Status: current
Last updated: 2026-10-26
Version: 0.1
Scope: Preserved 8,494-record national licensing snapshot

Read and run [build.ipynb](build.ipynb). The notebook calls the active [IBAMA stage](../../code/brazil_project/infrastructure/projects.py), which applies the original sector translation to the configured local snapshot. [processing.py](processing.py) then compares every preserved field and geometry with the inventoried baseline before copying it byte for byte. Live acquisition is separate.

The input is `data/processed/ibama/licensed_projects_st.gpkg`, verified against the [baseline inventory](../../docs/evidence/baseline-files.csv). The local output is `final.gpkg`, a checked copy of `outputs/maps/notebook-exports/ibama.gpkg`, layer `licensed_projects_st`, EPSG:4674. It contains point, line and polygon licensing records. Counts are source records, not unique developments or impacts.

The public website retained a frozen IBAMA tile asset. Its locally saved highest-zoom tiles contain 8,492 of 8,494 source IDs; `136441` and `3347413` are absent from the tiles but preserved in this GeoPackage. The reason and attribute/geometry parity remain unverified; see the [map workflow](../../docs/web-map.md) and [original extraction report](../../research/reports/ibama_data_extraction.md).
