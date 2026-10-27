# Brazil Research Project

This research project studies changes in population, housing, income, and basic services across Brazil, alongside government infrastructure and environmental licensing. It brings these sources together as four geographic datasets and an interactive map.

## 1. Final datasets

Each dataset folder has a readable `build.ipynb`, its `processing.py`, and a local `final.gpkg`. The large GeoPackages are kept outside GitHub.

- **[Census](datasets/census/build.ipynb):** 2010–2022 comparison areas and social indicators.
- **[Obrasgov](datasets/obrasgov/build.ipynb):** screened infrastructure project locations.
- **[IBAMA](datasets/ibama/build.ipynb):** environmental licensing records.
- **[Communities](datasets/communities/build.ipynb):** IBGE favela and urban community boundaries.

## 2. Processing and rebuilding

- **[Shared methods](datasets/shared/):** the code used by the four dataset folders.
- **[Build command](datasets/run.py):** how to run a dataset pipeline locally.
- **[Project settings](datasets/project.toml) and [locked dependencies](datasets/requirements.lock):** input paths and software versions.

## 3. Interactive map

- **[Website source](website/):** code for the published map.

## 4. Earlier research material

- **[Archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27):** earlier reports, documents, and original code.

![Interactive Brazil project map](website/preview.png)

[Open the interactive map](https://sandy-ivory-k65c.here.now/)
