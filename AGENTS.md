# Agent Working Instructions

Status: current
Last updated: 2026-10-06
Version: 0.6
Scope: Agent Working Instructions

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.6 | Codex | Required concise records, simple layout and Markdown reports with separate Python scripts. |
| 2026-10-05 | 0.3 | Codex | Recorded the harmonisation corrections and approved research assumptions. |

These rules apply to this independent research project. RISSI provided documentation patterns; its application architecture and deployment rules do not apply here.

## Read First

Before nontrivial work, read `README.md`, `docs/index.md`, `docs/progress.md`, `docs/tasks.md`, and `NOTICE.md`. Read the nearest folder README, `docs/methods.md`, and the relevant technical page before changing an analytical stage.

## Research Working Rules

- Keep changes scoped. Preserve unrelated user work and original files.
- Treat copied raw inputs and archived outputs as immutable. Write results into `data/intermediate/` and `outputs/`.
- Never modify the OneDrive source from a workflow, notebook, or validation script.
- Preserve variable codes, tract identifiers, years, CRS, aggregation rules, exclusions, and missing-data semantics during translation.
- Separate faithful translation from changes to research methods. Record methodological proposals and their consequences before implementing them.
- Do not silently resolve duplicate tract IDs, replace missing dated files, infer CRS, or fill absent years with zero.
- Keep complete connected comparison groups when selecting a municipality. Display geography may be narrower than aggregation geography.
- Distinguish implemented, numerically validated, exploratory, blocked, and unverified behavior.
- Do not invent hypotheses, findings, access rights, geography, ownership, or source licenses.
- Acquisition is explicit. Routine analysis must not download data or require an interactive RStudio session.
- Prefer Python. Retain R only for capabilities whose required equivalence has not been verified, and document each exception and exchange contract.
- Use `rg` before moving or renaming files and inspect consumers of shared stage artifacts.

## Code And Verification

Use the complete versioned harmonisation bundle. Never join lookup and geometry artifacts from different versions or use loose legacy geometry by file existence. Active analytical spatial outputs have one feature per `common_id`; original tract pieces are reference data.

Use existing patterns and clear functions. Add `WHY`, `INVARIANT`, `COMPATIBILITY`, or `CONTRACT` comments for non-obvious constraints; do not narrate basic syntax.

Run meaningful focused tests for changed behavior. For analytical changes, compare exact identifiers/counts, numeric tolerances, missingness, and geometry. A passing synthetic test does not establish national scientific parity. Compare chart tables separately from rendered figures. Never relabel a baseline mismatch as a passing result by relaxing tolerances without a documented explanation.

## Documentation Maintenance

After code, configuration, data flow, or structure changes, assess and update affected folder READMEs, methods, technical contracts, progress, tasks, and verification evidence. Document current state rather than conversational history.

Major Markdown documents use Status, Last updated, Version, and Scope, with a concise edit-history table near the top. The root README is a brief project description and is exempt from metadata and edit history; setup instructions belong in `docs/workflow.md`. Use one history row per date and sequential versions; update the same-day row rather than adding repeated entries. Original copied reference files are preserved verbatim.

Keep six visible working folders: `code/`, `data/`, `docs/`, `outputs/`, `research/`, and `website/`. Use the root `project.toml`. Create files and directories only when needed for real contents; no empty placeholders. Major working folders have one useful README; do not add repetitive READMEs to every subfolder. Keep documentation mostly flat and navigate through `docs/index.md`. Preserve original data/documents; when consolidating files, retain their complete contents and record the new location. Former folder READMEs are preserved in `docs/folder-notes.md`.

Research reports are maintained Markdown under `research/reports/`; executable report code lives under `code/reports/`. Keep one readable report per topic. Refresh scripts write review copies under `outputs/reports/` and never overwrite maintained narratives. Preserve prior QMD contents in the archive and Git history. Saved report snapshots are exempt from authored-document metadata.

## Process Records And Script Audits

For substantial processing work, maintain a concise Markdown process record as work proceeds. Record inputs and provenance, analytical decisions, commands, generated outputs, verification results and remaining uncertainty. Link it from current progress; do not leave the process only in chat or tool output.

Embed reviewed code-generated figures in the relevant Markdown as rendered images, with the generation command and a short caption stating what the output demonstrates and omits. Keep working artifacts under `outputs/`; copy only small reviewed documentation figures to `docs/assets/` so the Markdown renders in GitHub. Preserve the exact image bytes and record their checksum/provenance. Keep full datasets and bulk outputs outside Git.

After completing or materially changing a processing script, audit correctness, provenance, invariants, failure/recovery behavior, output contracts and reproducibility. Record findings, fixes and unresolved limitations in Markdown. Fix material implementation issues within scope and rerun relevant checks before declaring the work complete. Distinguish software verification from scientific validation.

## Data And Attribution

Do not commit full datasets, external caches, generated artifacts, session files, `.env`, or secrets. Preserve original source names, URLs, releases, licenses when supplied, and acquisition provenance. Maintain `NOTICE.md` when adapting external code or instructions. Do not assume copying a dataset grants publication permission.

## Handoffs

A completed task records affected stages, commands, inputs and scope, outputs, checks, remaining blockers, and current next steps. A future agent must be able to resume from repository documentation without reconstructing chat history.
