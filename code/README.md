# Project Code

Status: current
Last updated: 2026-10-26
Version: 0.10
Scope: Project Code

Reusable processing and command-line tools live here; executable report cells live alongside their explanations under `research/reports/`.

For a readable dataset entry point, start with the [four Jupyter notebooks](../datasets/README.md). Their adjacent `processing.py` files call this package's active functions and verify local final GeoPackages; the notebooks do not introduce separate analytical methods.

- `brazil_project/`: installable Python package; processing, analysis and CLI.
- `scripts/`: acquisition, export, auditing and verification commands; `scripts/r/` contains necessary R adapters.
- `tests/`: automated verification.
- `config/`: category translations and report chunk mappings.

The [pipeline/source guide](../docs/pipeline-source.md) links each CLI stage to its active function, inputs, saved outputs and reports. Report explanations link directly to these files and functions.

The single project configuration is [project.toml](../project.toml). Dependencies are locked at the project root. Inputs are under `data/`; saved artifacts and outputs follow [workflow commands](../docs/workflow.md). Run commands from the project root:

`scripts/build_web_map.py --gpkg-only --gpkg-output <path>` uses the original map preparation logic to create a national GeoPackage with concise English fields and a long original-code dictionary; `scripts/export_social_gpkg.py` checks exact source-to-output mappings and removes only redundant values. See the [field guide and audit](../docs/social-gpkg-export.md).

```bash
.venv/bin/brazil-project run indicators --config project.toml
.venv/bin/brazil-project run gov-data-quality --config project.toml
.venv/bin/python -m pytest -q
```

Create a directory only when real inputs or outputs need it. Preserve research methods and update [progress](../docs/progress.md) after material changes.

`brazil_project/reporting.py` formats saved results and generates descriptive figures; it does not change analytical calculations. Definitions live in [the variable codebook](../docs/codebook.md), with the [presentation audit](../docs/report-readability.md).

The pipeline executes Markdown report cells after successful processing. `report_engine.py` validates markers, captures results and publishes only generated sections; the CLI passes the current configuration and scope. See [the integration contract](../docs/report-integration.md).

The national `gov-data-quality` stage starts at [gov_quality.py → run()](brazil_project/infrastructure/gov_quality.py#L289). [Project-attribute](brazil_project/infrastructure/gov_quality_attributes.py) and [census-quality](brazil_project/infrastructure/gov_quality_census.py) helpers retain their source definitions and aggregation rules. The [concise quality report](../research/reports/gov_data_quality.md) presents essential findings; its [detailed annex](../research/reports/gov_data_quality_annex.md) retains the executable audit sections and complete figures. Both refresh from the same stage or `report gov_data_quality --from-saved` command and read identical saved diagnostics. The [process record](../docs/gov-data-quality-process.md) separates software checks from unresolved source review. This audit reads local inputs and makes no new exclusions, acquisitions or proximity-model estimates; the presentation split changes no study output.
