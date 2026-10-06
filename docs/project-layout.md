# Project Layout Simplification

Status: implemented and preservation verified
Last updated: 2026-10-06
Version: 0.2
Scope: Human navigation, content preservation and executable path updates

## Edit History

| Date | Version | Edited by | Reason |
| --- | --- | --- | --- |
| 2026-10-06 | 0.2 | Codex | Consolidated research reports into Markdown and preserved former QMD content. |

## Where things are

```text
brazil-project/
  project.toml          project inputs and settings
  code/                 Python package, scripts, R adapters, tests, small configuration
  data/                 source data, references, intermediates and preserved archive
  docs/                 methods, progress, tasks and audits in one flat folder
    assets/             reviewed figures
    evidence/           checks and migration manifests
  outputs/              generated figures, maps, tables, reports and software builds
  research/             Markdown reports and CS2Nordic conference documents
  website/              interactive map source
```

The visible working folders fall from **13 to six**. The root README gives a brief project description and folder overview. [The documentation index](index.md) groups flat documents by research topic; [progress](progress.md), [tasks](tasks.md) and [commands](workflow.md) are direct entries.

## Process and preservation

- Inventoried 1,147 files before changing paths; recorded sizes and SHA-256 checksums.
- Moved code/configuration/tests under `code/`; moved active reports to `research/reports/` and conference material to `research/cs2nordic/`. Original code, results, sessions and notes now live under `data/archive/`.
- Flattened authored documentation; machine-readable evidence is grouped under `docs/evidence/`. Consolidated **33 former folder READMEs verbatim** in [preserved folder notes](folder-notes.md).
- Removed **four zero-byte session files** and unused directories. No nonempty source dataset, research document or source note was deleted. Pre-edit authored files and changed generated contracts/container bytes are preserved in `data/archive/layout-before-2026-10-06.zip` for recovery. Generated Python bytecode and package metadata are rebuildable runtime artifacts.
- Updated Markdown/Quarto links, script discovery, package installation, R library paths, migration destinations and configuration defaults. Root `project.toml` replaces `config/project.toml`; CLI and package names are unchanged.
- Retired the original placeholder-document generator to `data/archive/project-tools/`; active code no longer creates directories merely while looking up inputs. Writers create only the directories their real outputs need.

The [move ledger](evidence/layout-moves.csv) records every inventoried file, its destination, original/current hashes and preservation location. Original migration paths have also been updated; source files in OneDrive remain untouched. Historical evidence JSON retains the paths/checksums of its original runs; use the ledger when locating those records.

## Verification and script audit

```bash
.venv/bin/python -m pytest -q
.venv/bin/python code/scripts/verify_reports.py
Rscript code/scripts/r/test_overview.R
.venv/bin/python code/scripts/migrate_files.py --verify-only
.venv/bin/python code/scripts/check_docs.py
.venv/bin/python code/scripts/verify_layout.py
```

- **Preservation:** all 1,147 inventory rows are accounted for. Relocated research files retain hashes; all 33 consolidated READMEs match their original text exactly. Original source/destination checks pass for all 344 migration records, including four explicitly accounted-for empty files.
- **Execution:** 59 tests pass; nine notebooks execute in fresh processes; the R/S2 reference check passes; editable package installation succeeds offline. The baseline location-QA verifier still confirms exact original attributes/WKB, complete partitions and investment coverage.
- **Paths and contracts:** moved script defaults, root discovery, imports, notebook links and R paths are checked. State diagnostics and the state-filter bundle were rerun from their new paths; counts and four GeoParquet hashes match the previous run. Historical evidence remains preserved rather than relabeled as a fresh result.
- **Audit fixes:** removed implicit directory creation from read-only path discovery and added a writer-only test; gave the R overview explicit output-directory creation; corrected a nested test path; isolated renv metadata/library/cache directories; updated migration destinations and zero-content accounting. Retired the placeholder generator so it cannot recreate the old layout in ordinary use.
- **Recovery and limits:** the move ledger verifies this dated layout snapshot; subsequent legitimate code/document edits can change its current hashes. Pre-edit recovery copies are local, outside Git. Dependency caches/bytecode are generated runtime artifacts, not immutable research inputs. The original archived source hierarchy is retained for provenance.

Existing analytical methods and numerical data are unchanged; restructuring does not publish a new website. Runtime caches stay hidden under `.cache/` and `.venv/`. New files/folders are created only when they have real contents.

Reports now live under `research/reports/` as Markdown only; their former executable cells live under `code/reports/`. [Preservation and workflow](report-previews.md) records the original QMD archive and code mapping.
