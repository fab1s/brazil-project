# Pipeline, Source Code and Report Connections

Status: current
Last updated: 2026-10-07
Version: 0.1
Scope: Active implementation links, stage dependencies and saved-output/report flow

## Follow a result back to its code

Reports explain the process, link the active processing function beside each executable section, and identify the saved artifacts. Numerical transformations live in the package; report cells read their outputs, perform presentation/coverage checks and produce reader-facing figures. Source links identify functions with GitHub line anchors, not only archived QMD filenames.

```mermaid
flowchart LR
    A[CLI command and project.toml] --> B[Resolve stage dependencies]
    B --> C[Active processing functions]
    C --> D[Saved datasets and producer evidence]
    D --> E[Executable Markdown report cells]
    E --> F[Protected report refresh and figure assets]
```

## Active stages

Paths in the output column are under `data/intermediate/` unless prefixed with `outputs/`. Supported municipality runs use a separate `municipality_<code>/` intermediate directory and report copies under `outputs/reports/`; the configured inputs and scope are passed through the runner.

| CLI stage | Active implementation | Reads | Produces |
| --- | --- | --- | --- |
| `overview` | [overview.py → run()](../code/brazil_project/harmonisation/overview.py#L9) | Configured tract GeoPackage; default municipality Belo Horizonte | `overview/intersections_2000_<year>.gpkg; change_summary_2000_<year>.parquet` |
| `census-exploration` | [census.py → run()](../code/brazil_project/visualisation/census.py#L15) | Original annual tracts and census counts for the six-municipality scope | `census-exploration/black_ratio_<year>.parquet; local HTML map and annual boxplots` |
| `harmonisation` | [census.py → run()](../code/brazil_project/harmonisation/census.py#L364) | Configured 2010/2022 tracts and original correspondence inputs | `harmonisation/current.json → bundles/<generation>/ lookups and merged geometry` |
| `indicators` | [temporal.py → run()](../code/brazil_project/indicators/temporal.py#L101) | Complete harmonisation bundle and year-specific census tables | `indicators/<indicator>.parquet; annual tables and spatial outputs` |
| `charts` | [charts.py → run()](../code/brazil_project/visualisation/charts.py#L108) | Lookups, household tables, racial shares and income from indicators | `charts/year_summary.parquet and chart populations; outputs/figures/<scope>/ conference charts` |
| `ibama` | [projects.py → run()](../code/brazil_project/infrastructure/projects.py#L47) | Configured snapshot or completed local acquisition; source=ibama | `ibama/licensed_projects.parquet; sector_counts.parquet; local HTML map` |
| `obrasgov-snapshot` | [projects.py → run()](../code/brazil_project/infrastructure/projects.py#L47) | Configured snapshot or completed local acquisition; source=obrasgov | `obrasgov/projects.parquet; projects_clean.parquet; translated category counts` |
| `obrasgov-location-qa` | [location_qa.py → run()](../code/brazil_project/infrastructure/location_qa.py#L218) | Preserved source snapshot from location_qa.source and pinned reference boundaries | `obrasgov-location-qa/component_audit.parquet; map, quarantine and review tables` |
| `obrasgov-location-plot` | [plot_location_qa.py → run()](../code/scripts/plot_location_qa.py#L35) | Component audit and pinned municipal reference | `outputs/figures/obrasgov-location-qa/location-screening.png` |
| `obrasgov-primary-state-check` | [check_obras_primary_state.py → run()](../code/scripts/check_obras_primary_state.py#L54) | Complete component geometry, uf_principal and IBGE state territory | `outputs/tables/obrasgov-primary-state/summary.json and component-level checks` |
| `obrasgov-primary-state-filter` | [filter_obras_primary_state.py → run()](../code/scripts/filter_obras_primary_state.py#L103) | Completed QA and primary-state diagnostics | `obrasgov-primary-state-filter/map_components.parquet; exclusion audit and comparison figure` |
| `land-value` | [property.py → run()](../code/brazil_project/land_value/property.py#L8) | Configured valuation workbook and exact dated zone/cadastral CSVs | `land-value/annex_*.parquet and zone geometry; processing blocks on absent exact CSV` |

`run obrasgov` expands to snapshot → location QA → screening figure → primary-state diagnostic → approved exclusion derivative. QA reads the preserved source snapshot, not `projects_clean.parquet`; the sequence combines independent faithful cleaning and later spatial screening. Both Obrasgov reports refresh after the complete flow succeeds.

`run indicators` resolves harmonisation first. `run charts` resolves harmonisation and indicators first. The overview retains an isolated [R sf/S2 adapter](../code/scripts/r/overview.R), using [spherical_intersections.R](../code/scripts/r/spherical_intersections.R). Land value remains blocked by its exact missing cadastral CSV; saved exploratory imports are not a completed analysis.

## Where reports enter the pipeline

- [cli.py → expand()](../code/brazil_project/cli.py#L55) orders dependencies; [cli.py → dispatch()](../code/brazil_project/cli.py#L22) selects the active processing function.
- [report_engine.py → render_report()](../code/brazil_project/report_engine.py#L176) checks producer provenance and executes a fresh report process; [report_engine.py → execute_cells()](../code/brazil_project/report_engine.py#L101) runs cells in order and stages their results.
- [reporting.py → show_chunk()](../code/brazil_project/reporting.py#L140) reads mapped saved artifacts; presentation functions in the same file format tables and figures. The report registry `REPORTS` in [report_engine.py](../code/brazil_project/report_engine.py) declares required stages.
- [Original chunk mappings](../code/config/report_chunks.json) preserve the archived R/QMD lineage. They are historical identities, not active Quarto execution. The explicit source links in the reports identify the current implementation.
- `report <name>` executes that report's processing dependencies and refreshes it. `report <name> --from-saved` verifies and reads saved artifacts without processing. Only marked output sections change; code, narrative and source links remain authored content. Missing required outputs fail. Report failures do not relabel completed processing as failed.

## Acquisition and publication are separate

Explicit `acquire-census` uses [census.py → run()](../code/brazil_project/acquisition/census.py#L42); `acquire-ibama` and `acquire-obrasgov` use [infrastructure.py → run()](../code/brazil_project/acquisition/infrastructure.py#L94). These stages do not run automatically when refreshing an extraction report. The original source inputs and archived code remain preserved.

Website build/publication follows its [own documented workflow](web-map.md); updating a processing report does not deploy here.now. Read [all reports](../research/README.md#read-the-reports), [methods](methods.md), [the variable codebook](codebook.md) and [commands](workflow.md) together when tracing a finding.

## Source-reference verification

This update adds authored links and explanations; cell code and saved result sections remain unchanged. Verify every relative file target and line anchor, preserve all 67 ordered cell IDs, and check that refresh preserves the authored links. The source-reference check validates every file target and Python function line anchor, all 67 preserved cell IDs/cell bodies and unchanged generated result sections. A fresh saved-output execution verifies authored source links survive publication. Results are recorded in [verification evidence](evidence/pipeline-source-verification.json) and [progress](progress.md). No processing implementation, input, numerical method or acquisition behavior changed.
