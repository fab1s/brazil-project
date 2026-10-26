# Pipeline, Source Code and Report Connections

Status: current
Last updated: 2026-10-26
Version: 0.7
Scope: Active implementation links, stage dependencies and saved-output/report flow

## Follow a result back to its code

The [dataset notebooks](../datasets/README.md) are a readable entry point over these active stages. Their adjacent `processing.py` files call the existing CLI or map functions and verify the final local GeoPackages; they do not replace the package's analytical implementations. The census notebook runs `indicators` and prepares the same map fields and geometries before the English-field export. Obrasgov runs the existing combined command. IBAMA verifies its active translation against the preserved baseline. Communities verifies an unchanged baseline copy. The [notebook process record](dataset-notebook-handoff.md) distinguishes fresh builds from saved-output previews.

Technical reports and annexes explain the process, link active processing functions beside executable sections and identify saved artifacts. Reader-facing summaries focus on findings, with these details in their annex. Numerical transformations live in the package; report cells read their outputs, perform presentation/coverage checks and produce reader-facing figures. Source links identify functions with GitHub line anchors, not only archived QMD filenames.

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
| `gov-data-quality` | [gov_quality.py → run()](../code/brazil_project/infrastructure/gov_quality.py#L289) | Verified frozen Obrasgov source, complete QA/state-filter lineage, national harmonisation bundle and saved/raw census variables | `gov-data-quality/*.parquet; report.json; outputs/figures/gov-data-quality/*.png` |
| `land-value` | [property.py → run()](../code/brazil_project/land_value/property.py#L8) | Configured valuation workbook and exact dated zone/cadastral CSVs | `land-value/annex_*.parquet and zone geometry; processing blocks on absent exact CSV` |

`run obrasgov` expands to snapshot → location QA → screening figure → primary-state diagnostic → approved exclusion derivative. QA reads the preserved source snapshot, not `projects_clean.parquet`; the sequence combines independent faithful cleaning and later spatial screening. Both Obrasgov reports refresh after the complete flow succeeds.

`run indicators` resolves harmonisation first. `run charts` resolves harmonisation and indicators first. The overview retains an isolated [R sf/S2 adapter](../code/scripts/r/overview.R), using [spherical_intersections.R](../code/scripts/r/spherical_intersections.R). Land value remains blocked by its exact missing cadastral CSV; saved exploratory imports are not a completed analysis.

`run gov-data-quality` runs the independent national diagnostic once and refreshes its [detailed annex](../research/reports/gov_data_quality_annex.md) followed by the [concise summary](../research/reports/gov_data_quality.md). It verifies saved upstream bytes and relevant policy/code contracts without automatically recomputing upstream stages. [Attribute audit](../code/brazil_project/infrastructure/gov_quality_attributes.py) and [census audit](../code/brazil_project/infrastructure/gov_quality_census.py) functions produce the diagnostics; an explicit as-of date and coordinate-sharing threshold come from `project.toml`. No acquisition, new exclusions, coordinate correction or models run. See [execution and final script audit](gov-data-quality-process.md).

## Where reports enter the pipeline

- [cli.py → expand()](../code/brazil_project/cli.py#L58) orders dependencies; [cli.py → dispatch()](../code/brazil_project/cli.py#L23) selects the active processing function.
- [report_engine.py → render_report()](../code/brazil_project/report_engine.py#L198) checks producer provenance and executes a fresh report process; [report_engine.py → execute_cells()](../code/brazil_project/report_engine.py#L123) runs cells in order and stages their results.
- [reporting.py → show_chunk()](../code/brazil_project/reporting.py#L140) reads mapped saved artifacts; presentation functions in the same file format tables and figures. The report registry `REPORTS` in [report_engine.py](../code/brazil_project/report_engine.py) declares required stages.
- [Original chunk mappings](../code/config/report_chunks.json) preserve the archived R/QMD lineage. They are historical identities, not active Quarto execution. The explicit source links in the reports identify the current implementation.
- `report <name>` executes that report's processing dependencies and refreshes it. `report <name> --from-saved` verifies and reads saved artifacts without processing. Only marked output sections change; code, narrative and source links remain authored content. Missing required outputs fail. Report failures do not relabel completed processing as failed. Explicit report–annex relationships are expanded and deduplicated by `expand_reports()`; `report gov_data_quality` refreshes its annex first, including with `--from-saved`. If the annex fails, the main report is left intact. Each document retains atomic publication and source-edit protection.

## Acquisition and publication are separate

Explicit `acquire-census` uses [census.py → run()](../code/brazil_project/acquisition/census.py#L42); `acquire-ibama` and `acquire-obrasgov` use [infrastructure.py → run()](../code/brazil_project/acquisition/infrastructure.py#L94). These stages do not run automatically when refreshing an extraction report. The original source inputs and archived code remain preserved.

Website build/publication follows its [own documented workflow](web-map.md); updating a processing report does not deploy here.now. Read [all reports](../research/README.md#read-the-reports), [methods](methods.md), [the variable codebook](codebook.md) and [commands](workflow.md) together when tracing a finding.

The national GIS copy follows [build_web_map.py → main()](../code/scripts/build_web_map.py) with `--gpkg-only`, calls the original [measure_fields()](../code/scripts/build_web_map.py) calculation and the [concise field exporter](../code/scripts/export_social_gpkg.py), and writes `outputs/maps/social-clean/social.gpkg` plus the requested user copy. Its embedded long `field_dictionary` links original field codes to English names. The [process record](social-gpkg-export.md) documents the exact saved input contracts and verification.

## Source-reference verification

The original nine reports retain their 67 ordered cell IDs and preserved lineage. The national quality annex preserves seven diagnostic cells; its executive summary adds one hidden presentation cell. Hidden cells use one HTML comment (`brazil:cell` plus raw Python and a closing comment), with the usual paired output markers. They receive the same ordering, compilation, source-edit and publication checks; embedded HTML comment delimiters are rejected. The main report displays findings only, with technical source links in the annex. Validate relative targets and function line anchors when code moves; protected refresh preserves authored links. Earlier source-link evidence is retained in [verification evidence](evidence/pipeline-source-verification.json); the new stage records its own [processing, publication and audit checks](gov-data-quality-process.md).
