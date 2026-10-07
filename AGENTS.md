# Agent Working Instructions

Status: current
Last updated: 2026-10-07
Version: 0.13
Scope: Agent Working Instructions

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
- Quality audits flag concerns before changing data. Record the explicit as-of date, thresholds and denominators; distinguish finite/world-range coordinates from verified locations and saved indicator availability from observed input completeness. Do not infer provider-supported corrections from co-location or name/category signals.

## Code And Verification

Use the complete versioned harmonisation bundle. Never join lookup and geometry artifacts from different versions or use loose legacy geometry by file existence. Active analytical spatial outputs have one feature per `common_id`; original tract pieces are reference data.

Use existing patterns and clear functions. Add `WHY`, `INVARIANT`, `COMPATIBILITY`, or `CONTRACT` comments for non-obvious constraints; do not narrate basic syntax.

Run meaningful focused tests for changed behavior. For analytical changes, compare exact identifiers/counts, numeric tolerances, missingness, and geometry. A passing synthetic test does not establish national scientific parity. Compare chart tables separately from rendered figures. Never relabel a baseline mismatch as a passing result by relaxing tolerances without a documented explanation.

## Documentation Maintenance

After code, configuration, data flow, or structure changes, assess and update affected folder READMEs, methods, technical contracts, progress, tasks, and verification evidence. Document current state rather than conversational history.

Major Markdown documents use Status, Last updated, Version, and Scope. Do not add edit-history sections or tables; Git records changes. The root README is a brief project description and is exempt from metadata; setup instructions belong in `docs/workflow.md`. Original archived reference files are preserved verbatim.

Keep six visible working folders: `code/`, `data/`, `docs/`, `outputs/`, `research/`, and `website/`. Use the root `project.toml`. Create files and directories only when needed for real contents; no empty placeholders. Major working folders have one useful README; do not add repetitive READMEs to every subfolder. Keep documentation mostly flat and navigate through `docs/index.md`. Preserve original data/documents; when consolidating files, retain their complete contents and record the new location. Former folder READMEs are preserved in `docs/folder-notes.md`.

Research reports under `research/reports/` contain executable Python cells and paired generated-result sections. Keep one main report per topic; put extensive diagnostic detail in a linked executable annex when needed. Register annex relationships explicitly so the same command refreshes both, preserving source links, original explanations and cell IDs. Processing commands refresh affected reports automatically; change explanations, code and captions outside generated sections. The renderer replaces only marked outputs after validation, preserves authored content, passes the actual configuration/scope and isolates report processes. National reports remain intact during municipality runs. Separate report scripts are archived; reusable analysis stays in the Python package. Reports are exempt from authored-document metadata. Never bypass producer fingerprints or mix scopes; rerun processing when saved provenance differs. Preserve originals and prior report contents in the archive and Git history.

Reader-facing summaries start with an executive summary, use plain language and explain essential qualifications beside each finding. Keep processing instructions, source-code links, reproduction commands and detailed methods in the annex or technical documentation; do not add a separate how-to-read section to the main report. Supporting executable summary code may use a validated hidden HTML-comment cell; never place comment delimiters inside its Python source. Technical reports and annexes link each processing explanation to its active source file and function, CLI stage and saved artifact, separately identifying display code and archived provenance. Maintain `docs/pipeline-source.md` when stages, functions or source locations change. Label tables with units, denominators and missingness; distinguish source rows, distinct IDs and geometry components. Put full machine provenance in collapsed details, suppress repeated results without removing cell traceability, and caption figures with their population, exclusions and limits. Maintain `docs/codebook.md` alongside changed variables; preserve original provider codebooks. Presentation changes must retain processing rules and pass report-refresh and scope tests.

## Process Records And Script Audits

For substantial processing work, maintain a concise Markdown process record as work proceeds. Record inputs and provenance, analytical decisions, commands, generated outputs, verification results and remaining uncertainty. Link it from current progress; do not leave the process only in chat or tool output.

Embed reviewed code-generated figures in the relevant Markdown as rendered images, with the generation command and a short caption stating what the output demonstrates and omits. Keep working artifacts under `outputs/`; copy only small reviewed documentation figures to `docs/assets/` so the Markdown renders in GitHub. Preserve the exact image bytes and record their checksum/provenance. Keep full datasets and bulk outputs outside Git.

After completing or materially changing a processing script, audit correctness, provenance, invariants, failure/recovery behavior, output contracts and reproducibility. Record findings, fixes and unresolved limitations in Markdown. Fix material implementation issues within scope and rerun relevant checks before declaring the work complete. Distinguish software verification from scientific validation.

## Data And Attribution

Do not commit full datasets, external caches, generated artifacts, session files, `.env`, or secrets. Preserve original source names, URLs, releases, licenses when supplied, and acquisition provenance. Maintain `NOTICE.md` when adapting external code or instructions. Do not assume copying a dataset grants publication permission.

## Handoffs

A completed task records affected stages, commands, inputs and scope, outputs, checks, remaining blockers, and current next steps. A future agent must be able to resume from repository documentation without reconstructing chat history.
