# Brazil Research Project

This research project studies changes in population, housing, income, and basic services across Brazil, alongside government infrastructure and environmental licensing. It brings these sources together as four geographic datasets and an interactive map.

## 1. Datasets and their methods

Each dataset folder contains a codebook, a runnable processing notebook, and its descriptively named GeoPackage stored locally outside GitHub. Final spatial fields use English names; each GeoPackage also contains a `field_dictionary` for original provider names. Reviewed categories have original and English values; place names and free-form descriptions retain their original wording.

- **Census:** `census_comparison_areas_2010_2022.gpkg` · [codebook](datasets/census/CODEBOOK.md) · [processing notebook](datasets/census/build.ipynb).
- **Obrasgov:** `obrasgov_screened_locations.gpkg` · [codebook](datasets/obrasgov/CODEBOOK.md) · [processing notebook](datasets/obrasgov/build.ipynb).
- **IBAMA:** `ibama_licensed_projects.gpkg` · [codebook](datasets/ibama/CODEBOOK.md) · [processing notebook](datasets/ibama/build.ipynb).
- **Communities:** `ibge_favelas_communities_2022.gpkg` · [codebook](datasets/communities/CODEBOOK.md) · [processing notebook](datasets/communities/build.ipynb).

Each notebook follows its preserved input through processing to the named GeoPackage. The [build command](datasets/run.py) runs the same processing without Jupyter. Input locations are in [project settings](datasets/project.toml); [shared code](datasets/shared/) and [locked dependencies](datasets/requirements.lock) support all four folders.

For collaborators, `.venv/bin/python datasets/run.py handoff --output-dir PATH` verifies those four files and copies them into one local folder with descriptive filenames.

## 2. Interactive map

- **[Website source](website/):** code for the published map. The English-field handoff does not retile or republish it.

## 3. Earlier research material

- **[Archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27):** earlier reports, documents, and original code.

![Interactive Brazil project map](website/preview.png)

[Open the interactive map](https://sandy-ivory-k65c.here.now/)
