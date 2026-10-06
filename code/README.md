# Project Code

Status: current
Last updated: 2026-10-06
Version: 0.1
Scope: Project Code

## Edit History

| Date | Version | Edited by | Reason |
| --- | --- | --- | --- |
| 2026-10-06 | 0.1 | Codex | Simplified navigation and documented the consolidated layout. |

Everything executable lives here:

- `brazil_project/`: installable Python package; processing, analysis and CLI.
- `scripts/`: acquisition, export, auditing and verification commands; `scripts/r/` contains necessary R adapters.
- `tests/`: automated verification.
- `config/`: category translations and notebook chunk mappings.

The single project configuration is [project.toml](../project.toml). Dependencies are locked at the project root. Inputs are under `data/`; saved artifacts and outputs follow [workflow commands](../docs/workflow.md). Run commands from the project root:

```bash
.venv/bin/brazil-project run indicators --config project.toml
.venv/bin/python -m pytest -q
```

Create a directory only when real inputs or outputs need it. Preserve research methods and update [progress](../docs/progress.md) after material changes.
