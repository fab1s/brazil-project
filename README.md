# Brazil Research Project

This research project studies changes in population, housing, income, and basic services across Brazil, alongside government infrastructure and environmental licensing. It brings these sources together as four geographic datasets and an interactive map.

## Where to find things

- **[Census](datasets/census/build.ipynb):** 2010–2022 comparison areas and social indicators.
- **[Obrasgov](datasets/obrasgov/build.ipynb):** screened infrastructure project locations.
- **[IBAMA](datasets/ibama/build.ipynb):** environmental licensing records.
- **[Communities](datasets/communities/build.ipynb):** IBGE favela and urban community boundaries.
- **[Shared processing code](datasets/shared/):** methods called by the four notebooks. Each dataset folder also has its own `processing.py` and a local `final.gpkg` output. The large GeoPackages are kept outside GitHub.
- **[Build command](datasets/run.py), [settings](datasets/project.toml), and [dependencies](datasets/requirements.lock):** what you need to rebuild the datasets locally.
- **[Website](website/):** source code for the interactive map. Earlier reports and original material are preserved on the [archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27).

![Interactive Brazil project map](website/preview.png)

[Open the interactive map](https://sandy-ivory-k65c.here.now/)
