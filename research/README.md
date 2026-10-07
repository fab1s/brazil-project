# Research Materials

Status: current
Last updated: 2026-10-07
Version: 0.6
Scope: Research Materials

- `reports/`: nine readable Markdown reports, with saved tables, figures and narratives.
- `cs2nordic/`: preserved conference abstract, poster and presentation.

Executable Python cells live inside each Markdown report; reusable analytical processing lives in the Python package. Original research code and the former QMD files are preserved under `data/archive/` and in Git history. Create other research folders only when real documents need them.

[Variable and dataset codebook](../docs/codebook.md) explains units, source codes, denominators and missingness. Reports present readable summaries; executable cells and complete processing provenance are collapsed.

## Read the reports

- [Obrasgov preprocessing and spatial exclusions](reports/obrasgov_preprocessing.md)
- [Census harmonisation and merged-area illustrations](reports/ibge_census_tract_harmonisation.md)
- [Temporal indicators, units and coverage](reports/ibge_census_temporal_comparison.md)
- [Dataset overview](reports/ibge_dataset_overview.md)
- [Conference charts](reports/brazil_poroject_charts.md)
- [IBAMA](reports/ibama_data_extraction.md)
- [Obrasgov data extraction](reports/obrasgov_data_extraction.md)
- [Census data extraction](reports/ibge_census_data_extraction.md)
- [Land value](reports/property_value.md)

Edit explanations and code in the Markdown report directly. Run `brazil-project report <report_name>` to process its inputs and refresh results automatically. Only marked generated sections change. See [commands and checks](../docs/report-integration.md).
