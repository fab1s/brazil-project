# Project Documentation

Status: current
Last updated: 2026-10-07
Version: 0.18
Scope: Project Documentation

Start with [progress](progress.md), [tasks](tasks.md), [methods](methods.md) and [commands](workflow.md).

[Pipeline stages and active source code](pipeline-source.md) · [Variable and dataset codebook](codebook.md) · [Readable-report process and audit](report-readability.md)

[Read the research reports](../research/README.md#read-the-reports) · [Executable Markdown and pipeline audit](report-integration.md)

## Research and workflow

[Harmonisation policy](harmonisation-policy.md) · [Obrasgov location policy](obrasgov-location-policy.md) · [R integration](r-integration.md) · [Website workflow](web-map.md) · [Provenance](provenance.md) · [Migration plan](migration-plan.md)

## Processing and audits

- **Government-data readiness:** [national quality report](../research/reports/gov_data_quality.md), [complete diagnostic annex](../research/reports/gov_data_quality_annex.md) and [processing record and script audit](gov-data-quality-process.md), covering locations, repeated coordinates, project attributes and census inputs before proximity modelling. The report separates Obrasgov and IBGE findings and refreshes with its annex from the same audit command.
- **Harmonisation:** [audit](harmonisation-audit.md), [repairs and checks](harmonisation-update.md).
- **Obrasgov:** [processing record and figure](obrasgov-location-qa-process.md), [location QA](obrasgov-location-qa.md), [script audit](obrasgov-location-qa-script-audit.md), [state check](obrasgov-primary-state-check.md), [approved exclusions and before/after figure](obrasgov-primary-state-filter.md), [initial screening](obrasgov-spatial-review.md).
- **Website:** [map checks](web-map-update.md), [screened Obrasgov publication](website-location-update.md).
- **Project:** [verification results](checks.md), [layout changes and preservation](project-layout.md).

`evidence/` holds machine-readable checks, migration manifests and chunk mappings. `assets/` holds reviewed figures embedded in these documents. [Former folder notes](folder-notes.md) collect former documentation without edit-history tables; original source notes are under `data/archive/original_notes/`. Current documents remain directly in this folder, organized through this index rather than extra directory layers.
