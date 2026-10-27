# Brazil Research Project

This research project studies changes in population, housing, income, and basic services across Brazil, alongside government infrastructure and environmental licensing. It brings these sources together as four geographic datasets and an interactive map.

## 1. Datasets and their methods

Start with a dataset notebook. It explains the source, processing decisions, checks, and final file. The notebook calls the adjacent `processing.py` and shared code; these are parts of the same workflow. Each `final.gpkg` is stored locally in its dataset folder, outside GitHub. Final spatial fields use English names. Each file's `field_dictionary` gives original provider field names; reviewed Portuguese categories have parallel original and English values. Place names and unreviewed free-form descriptions retain their original wording.

- **[Census](datasets/census/build.ipynb):** match 2010 and 2022 tracts → calculate indicators → export merged comparison areas.
- **[Obrasgov](datasets/obrasgov/build.ipynb):** translate projects → check locations and primary state → export retained points/lines and exclusions.
- **[IBAMA](datasets/ibama/build.ipynb):** translate licensing categories → verify the preserved records → export English fields and paired category values.
- **[Communities](datasets/communities/build.ipynb):** verify the preserved IBGE polygons → give source fields English names without changing place names or geometry.

Each notebook follows its preserved input through processing to `final.gpkg`. The [build command](datasets/run.py) runs the same processing without Jupyter. Input locations are in [project settings](datasets/project.toml); [shared code](datasets/shared/) and [locked dependencies](datasets/requirements.lock) support all four folders.

For collaborators, `.venv/bin/python datasets/run.py handoff --output-dir PATH` verifies those four files and copies them into one local folder with descriptive filenames.

## 2. Interactive map

- **[Website source](website/):** code for the published map. The English-field handoff does not retile or republish it.

## 3. Earlier research material

- **[Archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27):** earlier reports, documents, and original code.

![Interactive Brazil project map](website/preview.png)

[Open the interactive map](https://sandy-ivory-k65c.here.now/)
