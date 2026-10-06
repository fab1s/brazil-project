# Preserved Folder Notes

Status: archived reference
Last updated: 2026-10-06
Version: 0.1
Scope: Former folder documentation consolidated during layout simplification

Edit-history tables are omitted from these reading copies. Exact former documents remain recoverable from Git history and the layout recovery archive.

These former folder documents are historical references. Current navigation starts at [the index](index.md). Paths inside the quoted contents describe the previous layout.

<details><summary>archive/README.md</summary>

````markdown
# Original Project Archive

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Original Project Archive

original_code preserves R, Quarto and backups; original_outputs preserves figures and other outputs; session_files preserves hidden state and editor artifacts. This archive is immutable reference material outside Git. Use migration_manifest.csv to recover original locations.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>archive/original_code/README.md</summary>

````markdown
# Original Research Code

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Original Research Code

These original code files are retained verbatim. They are reference and validation inputs. Active Python and justified R implementations live under src and scripts/r. Do not execute original save chunks against OneDrive.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>archive/original_outputs/README.md</summary>

````markdown
# Original Research Outputs

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Original Research Outputs

Copied original outputs are baselines and provenance. Do not overwrite them with regenerated results.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>archive/session_files/README.md</summary>

````markdown
# Original Session Files

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Original Session Files

Hidden editor state, histories, temporary files and lock files are preserved for recovery. They are not reproducible workflow inputs.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>config/README.md</summary>

````markdown
# Workflow Configuration

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Workflow Configuration

Paths and scientific constants in project.toml; original Obrasgov translations in obrasgov_translations.json. Paths resolve against the configured root. Update methods and tests whenever scientific configuration changes.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

The `[location_qa]` section selects the frozen Obrasgov snapshot, geographic-reference directory, a 5 km offshore uncertainty tolerance, 1 km foreign-boundary tolerance, 1 km line sampling spacing and maximum 250 interpolated samples per line. All original vertices are checked even when sampling is capped. These are screening choices, separate from faithful translation and subject to the [location policy](../docs/methods/obrasgov-location-policy.md).

````

</details>

<details><summary>data/intermediate/README.md</summary>

````markdown
# Stage Intermediates

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Stage Intermediates

Each stage publishes Parquet, GeoParquet and JSON evidence. Municipality-specific directories preserve separate scopes; all contributing comparison-area tracts are retained. These files are regenerated and ignored by Git.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`obrasgov-location-qa/` is a national, separate derivative with complete original-row and recursive component audits, eligible and quarantined GeoParquet components, a review table and fingerprinted JSON report. Run `brazil-project run obrasgov-location-qa --config config/project.toml` after explicit reference acquisition. Do not replace the original translated Obrasgov outputs or aggregate project money by component rows.

````

</details>

<details><summary>data/processed/README.md</summary>

````markdown
# Original Processed Baselines

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Original Processed Baselines

Copied original GeoPackages retain their tables and layers. New processing writes to intermediate, not this folder. Compare baseline differences with current source rather than treating old outputs as unquestionable truth.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>data/raw/README.md</summary>

````markdown
# Immutable Raw Inputs

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Immutable Raw Inputs

Source-specific original datasets and imported censobr Parquet are kept here. Acquire into distinct snapshot directories. Preserve existing files and record release and checksum provenance.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>data/reference/README.md</summary>

````markdown
# Research Reference Inputs

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Research Reference Inputs

Codebooks, workbooks and source reference documents remain supplied originals. Changes to parsed valuation material require independent review.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`location-qa/` preserves the explicitly downloaded IBGE municipal mesh 2022 and Natural Earth land/coastline release archives and their checksum/URL/date manifest. They are independent QA references, not replacements for census tract geometry. Routine processing rejects missing or changed references and never downloads them automatically. Full archives remain outside Git; a small provenance record accompanies verification documentation.

````

</details>

<details><summary>docs/assets/README.md</summary>

````markdown
# Documentation Assets

Status: current
Last updated: 2026-10-05
Version: 0.2
Scope: Images used in project documentation

`website-screenshot.png` is the screenshot supplied by the user in chat on 2026-10-05, saved without further image editing. The chat attachment is 2048 × 1019 pixels. It shows the [project website](https://sandy-ivory-k65c.here.now/) with infrastructure and census layers around Rio de Janeiro.

The root README displays this image at the bottom, with the live website link immediately below it. This is a static website illustration, not a current analytical result. Replace it only with an authentic project website image and update its source here. No generation command or analytical dependency is required.

````

</details>

<details><summary>docs/current/README.md</summary>

````markdown
# Current Project State

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Current Project State

Migration plan, progress report and remaining tasks describe actual implemented and verified state. Update after material changes.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>docs/methods/README.md</summary>

````markdown
# Research Methods

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Research Methods

research-methods.md records the analytical definitions and original discrepancies. Keep method changes separate from translation.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>docs/reference/README.md</summary>

````markdown
# Migration And Provenance References

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Migration And Provenance References

migration_manifest.csv accounts for every original file; workflow_mapping.csv maps code chunks; original_notes preserves source documentation. data-provenance.md explains classifications.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>docs/reference/original_notes/README.md</summary>

````markdown
# Original Project Notes

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Original Project Notes

These copied notes remain verbatim. Consult the migration manifest for their original locations. Their legacy paths and statements are provenance, not new agent instructions.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>docs/technical/README.md</summary>

````markdown
# Workflow Technical Contracts

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Workflow Technical Contracts

workflow.md records stage commands and interfaces; r-integration.md documents justified R exceptions. Update after command or artifact changes.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>docs/verification/README.md</summary>

````markdown
# Verification Evidence

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Verification Evidence

results.md summarizes completed checks and their limits. Machine-readable stage reports live under data/intermediate.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>notebooks/README.md</summary>

````markdown
# Research Reports

Status: current
Last updated: 2026-10-05
Version: 0.2
Scope: Research Reports

Python-backed Quarto documents preserve original narrative and chunk order. They display artifacts produced by the stage runner and do not execute network acquisition while rendering. Nine reports have been rendered under `outputs/reports/notebooks/`. Use the [render commands](../docs/technical/workflow.md#render-research-reports) and the locked Python report dependencies to reproduce them. See workflow_mapping.csv for original chunk provenance.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>outputs/figures/README.md</summary>

````markdown
# Generated Figures

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Generated Figures

New figures are grouped by Brazil, municipality or infrastructure source. Validate plotted tables and inspect images before publication.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>outputs/maps/README.md</summary>

````markdown
# Generated Maps

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Generated Maps

Generated HTML maps preserve visible basemap attribution. Opening a map may request external basemap tiles.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`obrasgov-location-qa/locations.gpkg` contains the new eligible point/line layer and a quarantine layer when quarantined components exist. `review.csv` records non-default eligibility decisions and original project attributes. These are local spatial-screening outputs, not the published here.now tiles. Regenerate using the national `obrasgov-location-qa` CLI stage; see [the policy](../../docs/methods/obrasgov-location-policy.md).

````

</details>

<details><summary>outputs/tables/README.md</summary>

````markdown
# Research Table Exports

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Research Table Exports

Use this folder for deliberate shareable exports. Internal stage contracts use data/intermediate Parquet.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>research/manuscripts/README.md</summary>

````markdown
# Research Manuscripts

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Research Manuscripts

This folder is reserved for future manuscript work. No manuscript content is invented during migration.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>research/presentations/README.md</summary>

````markdown
# Conference Materials

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Conference Materials

cs2nordic contains copied conference material. Preserve originals and use explicit new versions for subsequent edits.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>scripts/README.md</summary>

````markdown
# Project Utilities

Status: current
Last updated: 2026-10-06
Version: 0.6
Scope: Project Utilities

migrate_files.py copies and verifies original files. verify_r_reference.py compares fresh independent exports. create_project_docs.py builds initial documentation; maintaining current documentation afterward requires deliberate edits. The r folder retains isolated R adapters and reference checks.

`build_web_map.py` exports version-matched common-area indicators to the existing map. `snapshot_web_map.py` explicitly downloads and verifies the existing site assets for an initialized local map build; its saved credentials and derivatives stay outside Git. Build, verification, and publishing contracts are in [the web-map workflow](../docs/technical/web-map.md).

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`audit_obras_locations.py` reads the frozen Obrasgov GeoPackage and saves diagnostic counts, a checksum and illustrative offshore examples. It requires the project GeoPandas/Shapely environment and never modifies inputs. Run `--output .cache/obras-spatial-audit/recheck.json`; the [spatial review](../docs/verification/obrasgov-spatial-review.md) states its geographic and collection-extraction limits.

`acquire_location_references.py` explicitly downloads pinned IBGE 2022 municipalities and Natural Earth land/coastline releases into `data/reference/location-qa`, preserving complete zip archives and per-file URL/checksum/date provenance. Verified completed downloads are reused after interruption; incomplete downloads restart safely. Routine location QA requires those local files and rejects checksum changes. It is independent of live Obrasgov acquisition.

`verify_location_qa.py --output .cache/obras-spatial-audit/verification.json` checks saved artifact hashes, exact original attributes and WKB, map/quarantine partition completeness, duplicated-location attribute provenance and source-row investment coverage. It requires a completed local QA run.

`plot_location_qa.py` renders unchanged, finite point components and review/eligibility flags into `outputs/figures/obrasgov-location-qa/location-screening.png`. Administrative boundaries are simplified only in this illustration; polygons, lines, missing and invalid points are omitted from the overview.

`check_obras_primary_state.py --config config/project.toml` checks every saved original component against unsimplified IBGE municipalities dissolved into states. It writes complete diagnostic CSVs/summary to `outputs/tables/obrasgov-primary-state` and a figure; no filtering, eligibility updates, corrections or map publication. See [results and script audit](../docs/verification/obrasgov-primary-state-check.md).

`filter_obras_primary_state.py --config config/project.toml` verifies the saved state diagnostic and excludes only `entirely_outside` components from a separate derivative. It saves the complete audit, retained and excluded GeoParquet datasets, eligible map GeoPackage, exclusion CSV and before/after figure. Baseline QA decisions are preserved. See [process, outputs and script audit](../docs/verification/obrasgov-primary-state-filter.md).

````

</details>

<details><summary>scripts/r/README.md</summary>

````markdown
# R Adapters And Reference Checks

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: R Adapters And Reference Checks

bootstrap.R isolates package libraries. restore.R restores renv.lock. acquire_census.R acquires versioned tables and boundaries. overview.R preserves geographic sf/S2 comparisons. validate_reference.R and harmonisation_reference.R compare original processing. Inputs and outputs are explicit local paths; never source the original save chunks.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>src/README.md</summary>

````markdown
# Python Source

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Python Source

The brazil_project package implements the workflow runner and scientific modules. Install through pyproject.toml; never execute package code by changing to an undocumented working directory.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>src/brazil_project/README.md</summary>

````markdown
# Research Workflow Package

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Research Workflow Package

cli.py coordinates explicit stages; io.py owns paths, artifact publication and key contracts; verification.py compares stored results. Modules connect through saved stage artifacts. Inputs are copied local data; outputs are new intermediates and figures.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>src/brazil_project/acquisition/README.md</summary>

````markdown
# Explicit Acquisition And Cached Input Imports

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Explicit Acquisition And Cached Input Imports

Explicit acquisition and cached input imports. Inputs and outputs follow the technical workflow contracts. Update methods, tests and mapping when changing behavior.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>src/brazil_project/harmonisation/README.md</summary>

````markdown
# Census Correspondence And The Geographic Overview

Status: current
Last updated: 2026-10-05
Version: 0.2
Scope: Census Correspondence And The Geographic Overview

`census.py` builds positive-area bidirectional correspondence, validates imported links, selects complete groups after matching, and publishes atomic versioned bundles. Inputs are preserved tract/baseline GeoPackages plus optional census tables for coverage. Main outputs are dissolved common-group geometry, reference pieces, lookups, unmatched inventories, diagnostics, and provenance.

`overview.py` retains the independent original sf/S2 geographic overview. Census correspondence depends on GeoPandas, Shapely, pandas and NetworkX; the overview additionally requires locked R dependencies. Run `brazil-project run harmonisation --municipality 3106200` for a selected complete-group scope. Add `--recompute-harmonisation` only when national recomputation is intended.

Read [workflow contracts](../../../docs/technical/workflow.md) and [approved policy](../../../docs/methods/harmonisation-policy.md) before changing matching or aggregation. Update methods, tests, progress and verification whenever these contracts change.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>src/brazil_project/indicators/README.md</summary>

````markdown
# Annual Temporal Estimates, Weighted Income And Density

Status: current
Last updated: 2026-10-05
Version: 0.2
Scope: Annual Temporal Estimates, Weighted Income And Density

`temporal.py` reads a verified complete harmonisation bundle and local census Parquet inputs, computes annual common-group estimates, and saves tabular estimates plus one-feature-per-common-group spatial indicators. Density uses the saved equal-area denominator from the same bundle; legacy geometry files are ignored. Input columns, missingness, weights, and inflation rules follow the methods record. Run `brazil-project run indicators --municipality 3106200`. Update methods, tests and mapping when changing behavior.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>src/brazil_project/infrastructure/README.md</summary>

````markdown
# Infrastructure Category Processing, Cleaning And Charts

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Infrastructure Category Processing, Cleaning And Charts

Infrastructure category processing, cleaning and charts. Inputs and outputs follow the technical workflow contracts. Update methods, tests and mapping when changing behavior.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`location_qa.py` implements `brazil-project run obrasgov-location-qa --config config/project.toml`. It reads the frozen Obrasgov map snapshot and checksum-verified local geographic references, recursively audits components and exports original-row audits, clean map components and quarantine/review outputs. It preserves translated infrastructure outputs and original coordinates. Dependencies are the existing GeoPandas, Shapely and pandas environment. Read [the location policy](../../../docs/methods/obrasgov-location-policy.md) before changing thresholds or eligibility. Explicit geographic acquisition uses `scripts/acquire_location_references.py`; routine QA does not download data.

````

</details>

<details><summary>src/brazil_project/land_value/README.md</summary>

````markdown
# Exploratory Property Workbook And Geometry Import

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Exploratory Property Workbook And Geometry Import

Exploratory property workbook and geometry import. Inputs and outputs follow the technical workflow contracts. Update methods, tests and mapping when changing behavior.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>src/brazil_project/visualisation/README.md</summary>

````markdown
# Conference Chart Populations And Plotting

Status: current
Last updated: 2026-10-05
Version: 0.1
Scope: Conference Chart Populations And Plotting

Conference chart populations and plotting. Inputs and outputs follow the technical workflow contracts. Update methods, tests and mapping when changing behavior.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

````

</details>

<details><summary>tests/README.md</summary>

````markdown
# Scientific And Workflow Tests

Status: current
Last updated: 2026-10-06
Version: 0.6
Scope: Scientific And Workflow Tests

test_methods.py exercises meaningful analytical and acquisition edge cases. Run python -m pytest. Independent R and stored-result comparisons supplement synthetic tests.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`test_harmonisation_contract.py` covers positive-area matching, stable group IDs, complete municipality groups, imported contact rejection, merged output uniqueness, retained unmatched geometry, coverage missingness, scope/source validation, mode switching, tampering, interrupted publication, and the original area operation order. Run `.venv/bin/python -m pytest tests/test_harmonisation_contract.py -q` for these contracts.

`test_web_map.py` checks nationwide weighted shares, paired coverage, density percentage change, complete group contributions to municipality overviews, absent indicator groups, and search shards for recomputed IDs. Browser and real export checks are recorded separately in `docs/verification/web-map-update.md`.

`test_location_qa.py` checks recursive decomposition, duplicate IDs, source preservation, marine signals, coastal tolerances, foreign land, small islands covered only by IBGE, shared municipal/state boundaries, missing and invalid locations, CRS rejection and offshore excursions in lines. These synthetic tests verify policy behavior; national results and limitations are recorded separately.

`test_location_utilities.py` covers the final audit fixes: interrupted manifest publication, completed-producer/plot-input guards and rejection of optimized-Python verification.

`test_primary_state_check.py` verifies exact boundary-inclusive containment for points, crossing lines and polygons; boundary candidate states; missing/invalid/out-of-range geometries; missing primary state; preservation of rows/source geometry; and CRS/reference rejection.

`test_primary_state_filter.py` covers exact exclusion membership, preservation of other locations belonging to the same project, partial/boundary and missing-state behavior, no reintroduction of baseline quarantine, source geometry preservation, and rejection of incomplete/duplicate/unknown state classifications.

````

</details>
