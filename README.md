# Brazil Research Project

This research project studies changes in population, housing, income, and basic services across Brazil, alongside government infrastructure and environmental licensing. It brings these sources together as four geographic datasets and an interactive map.

## 1. Datasets and their methods

Each dataset folder has a short codebook for reading its columns and a runnable notebook for its source and processing decisions. The notebook calls the adjacent `processing.py` and shared code. Each `final.gpkg` is stored locally, outside GitHub. Final spatial fields use English names; each file also contains a `field_dictionary` for original provider names. Reviewed categories have original and English values; place names and free-form descriptions retain their original wording.

- **Census:** [codebook](datasets/census/CODEBOOK.md) · [processing notebook](datasets/census/build.ipynb) — 2010/2022 comparison areas and indicators.
- **Obrasgov:** [codebook](datasets/obrasgov/CODEBOOK.md) · [processing notebook](datasets/obrasgov/build.ipynb) — screened infrastructure locations and exclusions.
- **IBAMA:** [codebook](datasets/ibama/CODEBOOK.md) · [processing notebook](datasets/ibama/build.ipynb) — licensed-project records and category translations.
- **Communities:** [codebook](datasets/communities/CODEBOOK.md) · [processing notebook](datasets/communities/build.ipynb) — 2022 IBGE community polygons.

Each notebook follows its preserved input through processing to `final.gpkg`. The [build command](datasets/run.py) runs the same processing without Jupyter. Input locations are in [project settings](datasets/project.toml); [shared code](datasets/shared/) and [locked dependencies](datasets/requirements.lock) support all four folders.

For collaborators, `.venv/bin/python datasets/run.py handoff --output-dir PATH` verifies those four files and copies them into one local folder with descriptive filenames.

## 2. Interactive map

- **[Website source](website/):** code for the published map. The English-field handoff does not retile or republish it.

## 3. Earlier research material

- **[Archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27):** earlier reports, documents, and original code.

![Interactive Brazil project map](website/preview.png)

[Open the interactive map](https://sandy-ivory-k65c.here.now/)
