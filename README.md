# Brazil Research Project

Four national GeoPackages support research on Brazilian census change, government infrastructure, environmental licensing, and favelas and urban communities. The [interactive map](https://sandy-ivory-k65c.here.now/) displays related data; its browser code is in [website/](website/).

![Interactive Brazil project map](website/preview.png)

## The four datasets

Open a notebook to read the method and run its processing. Each folder also contains `processing.py`; shared methods are in [datasets/shared/](datasets/shared/). The output is a local `final.gpkg` beside the notebook.

| Folder and notebook | Final GeoPackage | What it contains |
| --- | --- | --- |
| [Census](datasets/census/build.ipynb) | `datasets/census/final.gpkg` | 287,178 merged 2010–2022 comparison areas, indicators, municipality overview, and a table mapping original field codes to clear English names. |
| [Obrasgov](datasets/obrasgov/build.ipynb) | `datasets/obrasgov/final.gpkg` | 224,495 map-eligible point/line components and 2,346 components excluded for lying entirely outside their reported primary state. |
| [IBAMA](datasets/ibama/build.ipynb) | `datasets/ibama/final.gpkg` | 8,494 preserved licensing records with translated sector labels. |
| [Communities](datasets/communities/build.ipynb) | `datasets/communities/final.gpkg` | 12,348 preserved IBGE 2022 community polygons. |

The GeoPackages are too large for ordinary GitHub storage and stay local. Their **2026-10-27 local-copy SHA-256 checksums**, in the same order as the table, are `7547b9773fe36a0d3407105a77bae8c861791cf85a2ce263828200c5d7e251b9`, `02fdccb46a40a857089c649a25b4eda4160f51e82bb91ec744fbe19958f31e1c`, `0df410feb5e5aaa975851107fc501c408d2ed7ceb15a72e21a573462e0773863`, and `aec748dc609a00eb89e652b7c289c7728255d209286e1d58be2fa881e4d2e9f0`. Share the four local files separately with collaborators and compare these hashes after transfer. A rebuild can record new generation metadata and change a whole-file hash even when its research rows are identical. Census geometry uses EPSG:5880; the other three files use EPSG:4674.

## Rebuild locally

Restore the original `data/` inputs at the paths in [datasets/project.toml](datasets/project.toml), including the census tables, preserved IBAMA and community GeoPackages, Obrasgov source GeoPackage, and the IBGE/Natural Earth location references. The inputs are excluded from Git; obtain them from the preserved local project or the source custodian. The [archived input checksum inventory](https://github.com/fab1s/brazil-project/blob/archive/full-project-2026-10-27/docs/evidence/baseline-files.csv) helps verify restored baselines. Neither notebook downloads source data. Then run from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r datasets/requirements.lock
.venv/bin/jupyter nbconvert --to notebook --execute --inplace datasets/census/build.ipynb
```

Replace `census` with `obrasgov`, `ibama`, or `communities` to build another file. Without Jupyter, run `.venv/bin/python datasets/run.py census` (or another dataset name). Outputs and intermediate files stay local. The complete earlier research workspace, documents, reports, and original code are preserved on the [archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27); the original OneDrive folder is untouched.

Data sources are IBGE, Obrasgov and IBAMA. Their original names and attribution are retained in the preserved materials. Browser-library license texts are in [website/vendor/](website/vendor/).
