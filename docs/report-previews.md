# Markdown Research Reports

Status: implemented; content preservation and Python execution verified
Last updated: 2026-10-07
Version: 0.3
Scope: Single executable Markdown reports and safe result refreshes

[Read the nine reports](../research/README.md#read-the-reports). Each is a single Markdown document with explanations, collapsible executable Python cells, generated tables and figures. There is no active QMD or separate report-script counterpart.

Use `brazil-project run <stage>` for processing and automatic report updates, or `brazil-project report <name>` to execute a report with its processing dependencies. Add `--from-saved` to use existing verified artifacts only. National results refresh marked sections in the maintained document; municipality results become complete scoped copies under `outputs/`. Authored explanations, captions and code are preserved.

[Commands, preservation, verification and script audit](report-integration.md) describe the integrated workflow. The compatibility command `.venv/bin/python code/scripts/render_reports.py` now refreshes saved results directly; no manual copying is required. Edit reports directly and use your editor's Markdown preview or GitHub to read them. Interactive maps remain local HTML or the existing website.

## Preservation

[The earlier consolidation ledger](evidence/markdown-consolidation.json) describes the historical QMD-to-script migration, not the current execution interface. [Current migration evidence](evidence/report-integration-migration.json) preserves exact pre-integration scripts/reports and maps their cells to Markdown. Original R/QMD references and prior HTML are untouched. Software execution checks do not establish new scientific parity.
