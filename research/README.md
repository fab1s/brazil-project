# Research Materials

Status: current
Last updated: 2026-10-07
Version: 0.9
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

[Pipeline/source guide](../docs/pipeline-source.md) maps commands to processing functions, saved datasets and report cells. Each report links active implementations beside its executable sections; archived QMD identifiers preserve provenance.

Edit explanations and code in the Markdown report directly. Run `brazil-project report <report_name>` to process its inputs and refresh results automatically. Only marked generated sections change. See [commands and checks](../docs/report-integration.md).

## CS2Nordic conference materials

These original conference documents are preserved unchanged and tracked in GitHub:

- [Extended abstract](cs2nordic/extended_abstract_CS2Nordic.docx) (Word)
- [Poster](cs2nordic/poster_CS2.pptx) (PowerPoint)
- [Flash presentation](cs2nordic/CS2%20Flash%20Presentation.pptx) (PowerPoint)

Download these files to open them in Word or PowerPoint. The executable [conference charts report](reports/brazil_poroject_charts.md) is separate from these presentation documents.

## Saved Belo Horizonte reports

These municipality-scoped snapshots include their generated figures. They are separate from the maintained national reports and update only when a scoped workflow is run:

- [Belo Horizonte census harmonisation](../outputs/reports/municipality_3106200/ibge_census_tract_harmonisation.md)
- [Belo Horizonte temporal indicators](../outputs/reports/municipality_3106200/ibge_census_temporal_comparison.md)

[Original sources, figures and provider references](../data/README.md#research-material-included-in-github) preserve the material used to interpret and verify the pipeline.
