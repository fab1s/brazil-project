# Workflow Commands And Artifacts

Status: current
Last updated: 2026-10-05
Version: 0.3
Scope: Workflow Commands And Artifacts

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.3 | Codex | Established the workflow, verified reports, and consolidated setup instructions here. |

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


## Stage commands

Run commands from the project root using `.venv/bin/brazil-project`.

| Stage | Inputs | Outputs | Acquisition |
| --- | --- | --- | --- |
| overview | Original tract GeoPackage | Spherical intersections and comparison summaries | No |
| census-exploration | Raw census and boundary snapshots | Original regional race maps and boxplots | No |
| harmonisation | Original tracts or baseline lookup and geometry | Crosswalk lookups, group sizes, base geometry | No |
| indicators | Census Parquet and lookups | Annual common-area estimates and spatial indicator tables | No |
| ibama | Copied or acquired licensed projects | Sector translations and interactive map | No |
| obrasgov | Copied or acquired project records | Category counts, charts, cleaned geometry | No |
| land-value | Exact dated CSVs and valuation workbook | Annex tables and property geometries | No |
| charts | Saved census, indicators, and lookups | Conference populations, summaries, and PNGs | No |
| acquire-census | censobr and geobr sources | Versioned Parquet and tract GeoPackage | Explicit |
| acquire-ibama | PAMGIA FeatureServer layers | Cached responses and licensed-project GeoParquet | Explicit |
| acquire-obrasgov | Project and geometry APIs | Cached pages, enrichment provenance, project GeoParquet | Explicit |

```sh
.venv/bin/brazil-project run harmonisation
.venv/bin/brazil-project run indicators
.venv/bin/brazil-project run charts
.venv/bin/brazil-project run obrasgov
.venv/bin/brazil-project run land-value
.venv/bin/brazil-project run all
```

Indicators run harmonisation first; charts run both dependencies. `all` attempts remaining independent stages after failures, records evidence, and exits nonzero when incomplete. Acquisition is never implicit.

## Configuration and subsets

`config/project.toml` resolves paths relative to its project root. The national scope is the default. `--municipality 3106200` selects Belo Horizonte display tracts, retains every contributing tract in their common areas, and writes independent subset intermediates under `data/intermediate/municipality_3106200/`.

The overview retains its original Belo Horizonte scope when no municipality override is supplied. Correspondence recomputation uses the explicitly requested tract selection; its reference check must use the same selection.

## Artifact contracts

Tables use Parquet and spatial artifacts use GeoParquet. Identifiers are normalized to strings without float suffixes. Lookup keys must be unique after deduplicating repeated tract-to-group records. Original display duplicate geometry rows are preserved and reported.

Every stage writes a JSON report. Routine output publication uses temporary files and atomic replacement. Missing inputs produce actionable errors rather than empty results. National and municipality artifacts do not overwrite one another.

## Repeatability and verification

```sh
python3 scripts/migrate_files.py --verify-only
.venv/bin/python -m pytest -q
.venv/bin/brazil-project verify-parity
Rscript scripts/r/validate_reference.R "$PWD" 3106200
.venv/bin/python scripts/verify_r_reference.py --municipality 3106200
```

The first parity command compares stored original outputs and may intentionally report known source/baseline differences. Fresh R reference validation checks current original calculations separately. Reference validation reads archived code and local inputs only; it never sources the original save chunk or writes to OneDrive.

Infrastructure snapshot directories are configurable through ibama_snapshot and obrasgov_snapshot. Successful request caches are immutable; start a new configured snapshot for a new harvest. A failed acquisition does not make partial new results available to analysis.

## Render research reports

After generating the stage artifacts, use an installed Quarto runtime or the tested local portable runtime:

```sh
QUARTO_PYTHON="$PWD/.venv/bin/python" .cache/quarto/bin/quarto render
# On another machine with Quarto installed:
QUARTO_PYTHON="$PWD/.venv/bin/python" quarto render
```

The Python report dependencies are included in `requirements.lock`. HTML outputs are under `outputs/reports/notebooks/`. Rendering reads saved artifacts, preserves explicit missing-input notices, and does not acquire data. The portable runtime is machine-local and excluded from Git.
