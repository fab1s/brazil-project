# Executable Markdown Pipeline Integration

Status: implemented; software verified; land-value source limitation remains
Last updated: 2026-10-07
Version: 0.1
Scope: Processing, executable report cells, provenance and protected publication

Reports under `research/reports/` now contain marked Python cells and result sections. Existing report scripts and documents are preserved exactly in `data/archive/report-integration-before-2026-10-06.zip`; [migration evidence](evidence/report-integration-migration.json) records hashes and ordered cell IDs. Original datasets and analytical methods are unchanged. [Verification evidence](evidence/report-integration-verification.json) records run outcomes and published generation fingerprints.

## Commands and decisions

```bash
.venv/bin/brazil-project run obrasgov --config project.toml
.venv/bin/brazil-project report obrasgov_preprocessing --config project.toml
.venv/bin/brazil-project report obrasgov_preprocessing --from-saved --config project.toml
.venv/bin/brazil-project run indicators --municipality 3106200 --config project.toml
```

Obrasgov runs snapshot translation, location QA and screening figure, primary-state checking, approved map exclusions and comparison figure, then both reports. Individual stages remain available. Reports execute cells in fresh processes with the actual configuration and scope. National runs refresh canonical Markdown; scoped census/chart reports are complete copies under `outputs/reports/municipality_<code>/`. National-only requests reject municipality scope before writing.

Only marked outputs are replaced; explanations, captions and code remain authored content. Figures come from current output files and are saved byte-for-byte with content-derived names. Processing and reporting have separate outcomes. Failed stages block dependent reports while independent work continues.

## Verification and audit

The full analytical/integration suite passes 86 tests. The full national run completed eleven processing steps and refreshed eight reports; only land-value processing and its dependent automatic report were blocked by the known missing exact CSV. Explicit `report property_value --from-saved` refreshed the recorded exploratory workbook results with the missing-input notice. A fresh Belo Horizonte indicator run produced scoped reports without modifying national reports. The standalone Obrasgov command completed all five processing steps and both report publications with exit status zero. The compatibility saved-output refresh published all nine reports. 20 mapped artifact tables and the state-exclusion count table match processing outputs exactly; both current figure assets match their processing files byte-for-byte. The Markdown preview shows ten collapsed code sections, three tables and two reviewed figures. The installable wheel contains the runner and adapters. Source attributes, original geometry WKB, QA partition and investment coverage pass the national saved-output verification.

The renderer validates marker order and uniqueness before execution, stages results, locks report publication, checks source/configuration/code/input hashes and atomically replaces Markdown. Generation evidence is immutable; the completion pointer is published last and its output hash identifies interrupted publication. Stale locks from killed processes need explicit removal after confirming the owning process has exited. Standard output is recorded separately from ordered rich outputs.

Saved-output refresh requires producer records matching configuration, scope, implementation and observed processing inputs. Legacy artifacts without records need a processing run first. The land-value importer remains blocked when exact CSV inputs are absent; an explicitly requested saved-output report can display its recorded partial workbook results and limitations.

No live acquisition, website publication or new scientific validation is implied. Publication is atomic per report, not across the entire pipeline; successful independent reports may update while another fails. Review the current run evidence before declaring a full run complete.

## Script audit findings

- Fixed fresh-result figures that previously came from a static documentation image; report assets now copy the current processing output exactly.
- Removed default-config/session dependencies, generic missing-output fallbacks and hard-coded national result destinations. Report cells receive the pipeline context; scoped destinations are separate.
- Protected complete harmonisation bundles and their current pointer in report reads and producer evidence. Geometry and lookups cannot be mixed by loose-file existence.
- Fixed overview map lookup for integral tract IDs stored as REAL in the original GeoPackage. Text-only SQL casts added `.0` and silently skipped all four examples; the numeric identifier filter now generates the existing examples without changing their IDs or classifications. A GeoPackage-backed regression test exercises all four maps and both comparison years.
- Producer hashes reject stale saved results, and code/config/input/source checks reject changes during execution. Cell failures and interrupted Markdown replacement preserve the previous document; competing publication is rejected.

The remaining land-value input limitation and the publication recovery rules above are explicit. Passing software checks does not resolve scientific uncertainties already recorded in [research methods](methods.md).

## Reviewed code output

![Approved primary-state exclusions, before and after](assets/obrasgov-primary-state-filter.png)

Generated by `brazil-project run obrasgov --config project.toml`. The figure shows eligible points before and after the approved state exclusions; lines, polygons and previously quarantined locations are omitted. Coordinates are unchanged. The current output is copied byte-for-byte from `outputs/figures/obrasgov-location-qa/primary-state-filter.png`; SHA-256: `0ac43a2ef9a91c20ff6cfa1a4c7d98596a3834341b713641184dfe2f62279224`. Reports obtain their images from processing outputs, not this documentation copy.
