# Brazil Research Project

This research project studies changes in population, housing, income, and basic services across Brazil, alongside government infrastructure and environmental licensing. It brings these sources together as four geographic datasets and an interactive map.

## 1. Datasets and their methods

Start with a dataset notebook. It explains the source, processing decisions, checks, and final file. The notebook calls the adjacent `processing.py` and shared code; these are parts of the same workflow. Each `final.gpkg` is stored locally in its dataset folder, outside GitHub.

- **[Census](datasets/census/build.ipynb):** 2010–2022 comparison areas and social indicators.
- **[Obrasgov](datasets/obrasgov/build.ipynb):** screened infrastructure project locations.
- **[IBAMA](datasets/ibama/build.ipynb):** environmental licensing records.
- **[Communities](datasets/communities/build.ipynb):** IBGE favela and urban community boundaries.

Each notebook traces its preserved local input through processing to `final.gpkg`. It does not recreate the original download; the notebooks state what is known about retrieval and what remains unknown. The [build command](datasets/run.py) runs the same processing without Jupyter. Input locations are in [project settings](datasets/project.toml); [shared code](datasets/shared/) and [locked dependencies](datasets/requirements.lock) support all four folders.

## 2. Interactive map

- **[Website source](website/):** code for the published map.

## 3. Earlier research material

- **[Archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27):** earlier reports, documents, and original code.

![Interactive Brazil project map](website/preview.png)

[Open the interactive map](https://sandy-ivory-k65c.here.now/)
