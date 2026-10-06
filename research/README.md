# Research Materials

Status: current
Last updated: 2026-10-06
Version: 0.4
Scope: Research Materials

## Edit History

| Date | Version | Edited by | Reason |
| --- | --- | --- | --- |
| 2026-10-06 | 0.4 | Codex | Kept one Markdown report per topic with separate executable Python scripts. |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

- `reports/`: nine readable Markdown reports, with saved tables, figures and narratives.
- `cs2nordic/`: preserved conference abstract, poster and presentation.

Executable report code lives under `code/reports/`; analytical processing lives in the Python package. Original research code and the former QMD files are preserved under `data/archive/` and in Git history. Create other research folders only when real documents need them.

## Read the reports

- [Obrasgov preprocessing and spatial exclusions](reports/obrasgov_preprocessing.md)
- [Census harmonisation](reports/ibge_census_tract_harmonisation.md)
- [Temporal indicators](reports/ibge_census_temporal_comparison.md)
- [Dataset overview](reports/ibge_dataset_overview.md)
- [Conference charts](reports/brazil_poroject_charts.md)
- [IBAMA](reports/ibama_data_extraction.md)
- [Obrasgov data extraction](reports/obrasgov_data_extraction.md)
- [Census data extraction](reports/ibge_census_data_extraction.md)
- [Land value](reports/property_value.md)

Edit the Markdown report directly. Generate new output review copies with `.venv/bin/python code/scripts/render_reports.py`; review and copy results into reports when needed. Refreshing never overwrites your edits. See [commands and checks](../docs/report-previews.md).
