# Brazil Research Project

This research project studies changes in population, housing, income, and basic services across Brazil, alongside government infrastructure and environmental licensing. It brings these sources together as four geographic datasets and an interactive map.

## 1. Datasets and their methods

Each dataset folder contains a processing notebook, a short codebook, and its named GeoPackage stored locally outside GitHub. The notebook follows source records through decisions, transformations, and checked results. Final fields use English names; original field mappings and reviewed original/English category pairs remain in the GeoPackage.

Code opens collapsed in JupyterLab so explanations and saved results are visible first. Expand a cell's input bar to read its code; GitHub uses its own static notebook display.

- **Census:** `census_comparison_areas_2010_2022.gpkg`, layer `comparison_areas` · [codebook](datasets/census/CODEBOOK.md) · [processing notebook](datasets/census/build.ipynb).
- **Obrasgov:** `obrasgov_screened_locations.gpkg` · [codebook](datasets/obrasgov/CODEBOOK.md) · [processing notebook](datasets/obrasgov/build.ipynb).
- **IBAMA:** `ibama_licensed_projects.gpkg` · [codebook](datasets/ibama/CODEBOOK.md) · [processing notebook](datasets/ibama/build.ipynb).
- **Communities:** `ibge_favelas_communities_2022.gpkg` · [codebook](datasets/communities/CODEBOOK.md) · [processing notebook](datasets/communities/build.ipynb).

The [build command](datasets/run.py) executes that same notebook and saves its tables and figures: `.venv/bin/python datasets/run.py census` (or `obrasgov`, `ibama`, `communities`). Add `--from-saved` to refresh the explanation's evidence using verified existing outputs. Open a notebook in its own folder to run it interactively. The notebook owns stage order; the adjacent `processing.py` supplies display/export helpers, and [shared code](datasets/shared/) implements the analytical methods. [Project settings](datasets/project.toml) locate the preserved inputs; [locked dependencies](datasets/requirements.lock) define the environment.

For collaborators, `.venv/bin/python datasets/run.py handoff --output-dir PATH` verifies those four files and copies them into one local folder with descriptive filenames.

## 2. Interactive map

- **[Website source](website/):** code for the published map. The English-field handoff does not retile or republish it.

## 3. Earlier research material

- **[Archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27):** earlier reports, documents, and original code.

![Interactive Brazil project map](website/preview.png)

[Open the interactive map](https://sandy-ivory-k65c.here.now/)
