# Research Materials

Status: current
Last updated: 2026-10-06
Version: 0.3
Scope: Research Materials

## Edit History

| Date | Version | Edited by | Reason |
| --- | --- | --- | --- |
| 2026-10-06 | 0.3 | Codex | Simplified navigation and added rendered research-report previews. |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

- `notebooks/`: the nine active Quarto research reports; narratives display explicit saved processing artifacts.
- `cs2nordic/`: preserved conference abstract, poster and presentation.

Create manuscript or other conference folders when there are actual documents to put in them. Original notebooks remain under `data/archive/original_code/`. Rendering writes to `outputs/reports/`; it does not acquire new datasets. See [report commands](../docs/workflow.md). Preserve document contents and distinguish exploratory results from validated findings.

## Read the reports

Open the **preview** on GitHub; open the **Quarto source** for visual editing/execution. Local HTML reports are generated under `outputs/reports/research/notebooks/`.

| Report | Preview | Quarto source |
| --- | --- | --- |
| Obrasgov preprocessing and spatial exclusions | [Read](notebooks/obrasgov_preprocessing.md) | [Edit](notebooks/obrasgov_preprocessing.qmd) |
| Census harmonisation | [Read](notebooks/ibge_census_tract_harmonisation.md) | [Edit](notebooks/ibge_census_tract_harmonisation.qmd) |
| Temporal indicators | [Read](notebooks/ibge_census_temporal_comparison.md) | [Edit](notebooks/ibge_census_temporal_comparison.qmd) |
| Dataset overview | [Read](notebooks/ibge_dataset_overview.md) | [Edit](notebooks/ibge_dataset_overview.qmd) |
| Conference charts | [Read](notebooks/brazil_poroject_charts.md) | [Edit](notebooks/brazil_poroject_charts.qmd) |
| IBAMA | [Read](notebooks/ibama_data_extraction.md) | [Edit](notebooks/ibama_data_extraction.qmd) |
| Obrasgov data extraction | [Read](notebooks/obrasgov_data_extraction.md) | [Edit](notebooks/obrasgov_data_extraction.qmd) |
| Census data extraction | [Read](notebooks/ibge_census_data_extraction.md) | [Edit](notebooks/ibge_census_data_extraction.qmd) |
| Land value | [Read](notebooks/property_value.md) | [Edit](notebooks/property_value.qmd) |

Regenerate both views with `.venv/bin/python code/scripts/render_reports.py`. See [preview setup and verification](../docs/report-previews.md).
