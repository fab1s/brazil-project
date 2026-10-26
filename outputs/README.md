# Research Outputs

Status: current
Last updated: 2026-10-26
Version: 0.6
Scope: Research Outputs

`maps/notebook-exports/` holds the local census, IBAMA and community GeoPackages produced by the [dataset notebooks](../datasets/README.md). The Obrasgov notebook uses its existing approved output at `maps/obrasgov-primary-state-filter/locations.gpkg`. Each notebook exposes its checked result locally as `datasets/<name>/final.gpkg`; binaries stay outside Git.

- `figures/`: generated research and quality-check images.
- `maps/`: GIS exports, interactive maps and the local website publication bundle.
- `tables/`: deliberate diagnostic and shareable table exports.
- `reports/`: rendered research reports and their assets.
- `software/`: preserved local package build artifacts.

These outputs are outside Git and created when needed. Original outputs live under `data/archive/original_outputs/`. Processing inputs and commands are in [the workflow](../docs/workflow.md); review figures before publication and record provenance in [documentation](../docs/index.md).

`reports/` holds scoped Markdown copies, immutable report-generation evidence and historical HTML. National report results are refreshed automatically under `research/reports/`; municipality copies never replace national reports.

`maps/social-clean/social.gpkg` is the checked national census GIS export. Its `social` and `overview` layers use concise English names; `field_dictionary` records the original source codes and units. Its [process record](../docs/social-gpkg-export.md) describes regeneration and limits. Like the other full datasets, it stays local.
