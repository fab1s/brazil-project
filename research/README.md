# Research Materials

Status: current
Last updated: 2026-10-07
Version: 0.12
Scope: Research Materials

- `reports/`: ten maintained research topics with executable primary Markdown reports, plus a detailed government-data quality annex. These contain saved tables, figures and narratives. The unregistered infrastructure-proximity draft is preserved separately from the runnable report registry.
- `cs2nordic/`: preserved conference abstract, poster and presentation.

Executable Python cells live inside each Markdown report; reusable analytical processing lives in the Python package. Original research code and the former QMD files are preserved under `data/archive/` and in Git history. Create other research folders only when real documents need them.

[Variable and dataset codebook](../docs/codebook.md) explains units, source codes, denominators and missingness. Reports present readable summaries; executable cells and complete processing provenance are collapsed.

## Read the reports

- [National government-data quality: concise assessment](reports/gov_data_quality.md) · [Detailed annex: locations, project attributes and census readiness](reports/gov_data_quality_annex.md)
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

The national quality report opens with an executive summary, then presents six findings and three figures in plain language. Its supporting presentation code is hidden from the rendered report; technical instructions, sources and methods remain in the annex, which preserves all seven executable audit sections and eleven diagnostic figures. Both read the same saved results and refresh together with `brazil-project run gov-data-quality --config project.toml` or `brazil-project report gov_data_quality --from-saved --config project.toml`.

The [processing source](../code/brazil_project/infrastructure/gov_quality.py) writes diagnostic tables and figures; the [process and script-audit record](../docs/gov-data-quality-process.md) documents execution and limitations. Report organization changes no numerical methods or study outputs. The audit does not acquire data, change existing exclusions or fit proximity models.

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
