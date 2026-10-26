# IBGE favelas and communities

Status: current
Last updated: 2026-10-26
Version: 0.1
Scope: Preserved 2022 IBGE community polygons

Read and run [build.ipynb](build.ipynb). No active cleaning or reprojection of this source is documented, so [processing.py](processing.py) verifies its byte count, checksum, GeoPackage integrity, CRS and unique `cd_fcu` codes before making an exact copy. It does not acquire a newer IBGE release.

The input is `data/processed/ibge/Data/favelas_2022.gpkg`, recorded in the [baseline inventory](../../docs/evidence/baseline-files.csv). The local output is `final.gpkg`, a checked copy of `outputs/maps/notebook-exports/communities.gpkg`, layer `favelas_2022`, EPSG:4674. The notebook shows counts by state, not populations.

The website retained a frozen community tile asset. All 12,348 source `cd_fcu` codes appear in the locally saved highest-zoom tiles. That verifies identifier coverage, not exact geometry or attributes; see the [map workflow](../../docs/web-map.md).
