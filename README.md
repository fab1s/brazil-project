# Brazil Research Project

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Brazil Research Project

This project organizes the existing Brazil census, infrastructure, land-value, and conference research into reproducible workflows. Python handles analysis, harmonisation, infrastructure processing, and charts. Isolated R adapters retain census acquisition and the geographic sf/S2 overview. The original OneDrive folder is unchanged.

Start with [agent instructions](AGENTS.md), the [documentation index](docs/index.md), and the [current progress report](docs/current/current-progress-report.md). The [migration plan](docs/current/migration-plan.md) distinguishes delivered behavior from remaining validation.

## Setup

The tested Python runtime is 3.9.6. Use a project environment and the exact dependency lock.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/brazil-project --help
```

For retained R workflows, install R matching `renv.lock`, then restore into the project library:

```sh
Rscript scripts/r/restore.R
```

## Run research

The copied inputs and imported local census cache are already available on this computer. Routine runs do not acquire remote data.

```sh
.venv/bin/brazil-project run all --config config/project.toml
.venv/bin/brazil-project run charts --municipality 3106200
.venv/bin/brazil-project verify-parity
.venv/bin/python -m pytest -q
```

The nine rendered [research reports](outputs/reports/notebooks/ibge_census_temporal_comparison.html) are available locally; see [render instructions](docs/technical/workflow.md#render-research-reports).

`all` attempts every research stage, records failures, and exits nonzero if any stage is blocked. The original property workflow requires a missing cadastral CSV, so the full run currently reports that blocker. Use [run commands](docs/technical/workflow.md) for focused work.

Default census correspondence uses the original archived lookups. Use `--recompute-harmonisation` explicitly for the Python geometric implementation. Municipality subsets retain complete comparison groups, including their tracts outside the selected municipality.

## Acquire inputs explicitly

```sh
.venv/bin/brazil-project import-cache /path/to/censobr/data_release_v0.5.0
.venv/bin/brazil-project run acquire-census
.venv/bin/brazil-project run acquire-ibama
.venv/bin/brazil-project run acquire-obrasgov
```

Infrastructure adapters cache requests and resume incomplete snapshots. A new harvest requires a new snapshot directory; never mix a fresh harvest into an existing snapshot.

## Project layout

- `src/brazil_project/` contains Python workflow components.
- `scripts/r/` contains retained adapters and independent reference validation.
- `config/` defines project-relative paths and translated category mappings.
- `notebooks/` preserves Quarto narrative and chunk order with Python artifact views.
- `data/` separates copied inputs, references, original results, and new intermediates.
- `outputs/` contains new figures, maps, and tables.
- `research/` contains manuscripts and conference material.
- `archive/` preserves original code, outputs, backups, and session files.
- `docs/` provides methods, provenance, migration, current state, and verification.

Copied data and generated outputs stay outside Git. The complete file manifest records every original file and checksum. No project-wide software or data license is inferred from the source material.
