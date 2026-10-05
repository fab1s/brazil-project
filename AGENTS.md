# Agent Working Instructions

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Agent Working Instructions

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

These rules apply to this independent research project. RISSI provided documentation patterns; its application architecture and deployment rules do not apply here.

## Read First

Before nontrivial work, read `README.md`, `docs/index.md`, `docs/current/current-progress-report.md`, `docs/current/todo.md`, and `NOTICE.md`. Read the nearest folder README, `docs/methods/research-methods.md`, and the relevant technical page before changing an analytical stage.

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

Use existing patterns and clear functions. Add `WHY`, `INVARIANT`, `COMPATIBILITY`, or `CONTRACT` comments for non-obvious constraints; do not narrate basic syntax.

Run meaningful focused tests for changed behavior. For analytical changes, compare exact identifiers/counts, numeric tolerances, missingness, and geometry. A passing synthetic test does not establish national scientific parity. Compare chart tables separately from rendered figures. Never relabel a baseline mismatch as a passing result by relaxing tolerances without a documented explanation.

## Documentation Maintenance

After code, configuration, data flow, or structure changes, assess and update affected folder READMEs, methods, technical contracts, progress, tasks, and verification evidence. Document current state rather than conversational history.

Major Markdown documents use Status, Last updated, Version, and Scope. Include a concise edit-history table near the top, except in the root README. Use one history row per date and sequential versions; update the same-day row rather than adding repeated entries. Original copied reference files are preserved verbatim.

Each major folder has a concise README with purpose, project connections, file responsibilities, workflows, inputs/outputs, dependencies, and update rules. `docs/` uses `index.md` as its entry point.

## Data And Attribution

Do not commit full datasets, external caches, generated artifacts, session files, `.env`, or secrets. Preserve original source names, URLs, releases, licenses when supplied, and acquisition provenance. Maintain `NOTICE.md` when adapting external code or instructions. Do not assume copying a dataset grants publication permission.

## Handoffs

A completed task records affected stages, commands, inputs and scope, outputs, checks, remaining blockers, and current next steps. A future agent must be able to resume from repository documentation without reconstructing chat history.
