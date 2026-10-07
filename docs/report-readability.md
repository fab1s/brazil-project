# Readable Executable Research Reports

Status: implemented; software verified; scientific and input limitations remain
Last updated: 2026-10-07
Version: 0.1
Scope: Nine Markdown reports, shared presentation helpers and variable codebook

## Inputs and preservation

All nine pre-edit reports and the previous presentation helper are preserved byte-for-byte in `data/archive/reports-before-readability-20261007.zip`; [preservation evidence](evidence/report-readability-preservation.json) records hashes. Original provider codebooks and analytical methods remain unchanged. Existing website work is outside this task.

## Presentation changes

Reports now explain purpose, inputs, scope, calculations, units and limitations before results. Executable cells retain their IDs and order, with descriptive collapsed labels. Repeated legacy cells keep traceability without printing the same result again. Complete processing dictionaries remain available in collapsed provenance sections. Summaries distinguish source rows, projects, geometry components and common areas.

The [codebook](codebook.md) documents all 13 indicators, exact source mappings, denominators, missingness, inflation and chart-specific rules. The income explanation now describes the original implemented head-weighted calculation; the formerly stronger prose is preserved in the archive, not applied as a methodological change. Original QMD source names inside calls are provenance keys, not interactive Quarto execution.

Figures use current saved processing artifacts. Added evidence includes a schematic of relationship types, a real reference-versus-merged common-area example, four real 2000 tract examples, descriptive distributions for race/income/density, licensing sectors, Obrasgov categories and the existing annual exploratory boxplots. Existing screening, exclusions and conference figures remain current. Captions distinguish schematic from real geometry, counts from distinct IDs, availability from completeness, and software checks from scientific validation.

## Commands and verification

```bash
.venv/bin/python -m pytest code/tests/test_report_readability.py code/tests/test_report_previews.py code/tests/test_report_pipeline.py -q
.venv/bin/brazil-project run all --config project.toml
.venv/bin/brazil-project report property_value --from-saved --config project.toml
.venv/bin/brazil-project run indicators --municipality 3106200 --config project.toml
```

Processing is rerun because the pipeline correctly rejects saved producers made with different code fingerprints. Report refresh continues to validate producer records, scope, file hashes, cell markers and atomic publication. National reports remain unchanged during municipality refresh. The missing exact cadastral CSV remains an explicit processing blocker; no substitute is introduced.

## Script audit

The shared presentation helper reads saved artifacts and never acquires data. It checks the harmonisation generation and uses the complete validated bundle for geometry examples. Added figures retain exact PNG bytes through the existing report asset publisher. Presentation percent conversion applies only to descriptive summaries; stored ratios and preview values remain unchanged. Tables preserve identifier strings and expose unavailable values. Repeated-output suppression is local to the report context. An explicit saved-data check found 3,838 usable/unique 2010 Belo Horizonte tract observations and 5,025 usable observations from 5,024 distinct IDs in 2022; the original exploratory row weighting is preserved and explained rather than silently deduplicated. Figures outside the preserved Belo Horizonte example scope are omitted with an explicit notice.

The complete suite passes **100 tests**. All nine saved-output reports execute in fresh processes, retaining all 67 cell IDs and their order; refresh preserves authored narrative and code. All 13 indicator summary tables were independently compared with saved numerical artifacts. The reports contain 18 current generated figures; all images load in offline browser previews of nine reports and the codebook. Screening and exclusion report assets match current processing PNG bytes exactly. A fresh scoped Belo Horizonte indicator run leaves all nine national reports byte-identical.

The first full processing run completed all eleven available steps; the exact cadastral CSV remains the sole processing blocker. Fresh figure workers exposed a macOS interactive-backend issue; every report now selects the headless Agg backend before plotting, and a fresh-worker regression test covers it. No processing rules or producer checks were relaxed. All nine reports refreshed successfully after that fix. Detailed evidence is in [verification](evidence/report-readability-verification.json). The standalone `run obrasgov` command exits successfully after all five processing steps and both automatic report updates. It reproduces 2,346 state exclusions and 224,495 final eligible map components. Final producer, report-generation, figure, scoped-run and browser records are linked in the verification evidence. Repeat saved-output execution succeeds without acquisition.

The audit also found that the legacy income missing-change counter (zero) precedes final change columns; 7,216 national income changes are actually unavailable. Report availability now reads final saved change columns for all 13 indicators, retaining the original metadata with a legacy label. A regression test prevents that counter from being mistaken for coverage. The underlying income calculation and missingness are unchanged. Scientific limitations remain in [methods](methods.md) and [verification](checks.md).
