# Project Code

Status: current
Last updated: 2026-10-07
Version: 0.4
Scope: Project Code

Reusable processing and command-line tools live here; executable report cells live alongside their explanations under `research/reports/`.

- `brazil_project/`: installable Python package; processing, analysis and CLI.
- `scripts/`: acquisition, export, auditing and verification commands; `scripts/r/` contains necessary R adapters.
- `tests/`: automated verification.
- `config/`: category translations and report chunk mappings.

The single project configuration is [project.toml](../project.toml). Dependencies are locked at the project root. Inputs are under `data/`; saved artifacts and outputs follow [workflow commands](../docs/workflow.md). Run commands from the project root:

```bash
.venv/bin/brazil-project run indicators --config project.toml
.venv/bin/python -m pytest -q
```

Create a directory only when real inputs or outputs need it. Preserve research methods and update [progress](../docs/progress.md) after material changes.

`brazil_project/reporting.py` formats saved results and generates descriptive figures; it does not change analytical calculations. Definitions live in [the variable codebook](../docs/codebook.md), with the [presentation audit](../docs/report-readability.md).

The pipeline executes Markdown report cells after successful processing. `report_engine.py` validates markers, captures results and publishes only generated sections; the CLI passes the current configuration and scope. See [the integration contract](../docs/report-integration.md).
