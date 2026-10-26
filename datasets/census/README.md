# Census comparison areas

Status: current
Last updated: 2026-10-26
Version: 0.1
Scope: National 2010–2022 common areas and indicators

Read and run [build.ipynb](build.ipynb). It calls the versioned harmonisation and indicator stages, rebuilds the full-resolution common-area map geometry and municipality overview, then runs the [English-field exporter](../../code/scripts/export_social_gpkg.py). The reusable method remains in the linked [census](../../code/brazil_project/harmonisation/census.py), [indicator](../../code/brazil_project/indicators/temporal.py) and [map preparation](../../code/scripts/build_web_map.py) code. This folder's [processing.py](processing.py) connects those steps without introducing a second matching rule.

Inputs are the configured local IBGE tracts, baseline correspondence, census tables and [project.toml](../../project.toml). The output is `final.gpkg`, a checked copy of `outputs/maps/notebook-exports/social.gpkg`, with `social`, `overview`, `field_dictionary` and `export_metadata` layers/tables. Source data and the existing `/Users/fa4850sc/Documents/Data/social.gpkg` copy are unchanged. The notebook does not build or publish website tiles.

The accepted boundary-change assumption, unmatched coverage and missingness rules are in the [methods](../../docs/methods.md) and [policy](../../docs/harmonisation-policy.md). Saved notebook plots describe common-area relationships, not residents. Run all cells to process; the committed output cells are a labeled preview of the already verified national export.
