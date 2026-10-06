# Historical initial-migration scaffold. It skips maintained files; read current methods and workflow contracts.
"""Build the project navigation and migration documentation."""
from pathlib import Path
import csv
import json
ROOT=Path(__file__).resolve().parents[1]
DATE='2026-10-05'

def write(path,title,body,status='current',scope=None):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): return  # Initial scaffolding must not overwrite maintained project documentation.
    header=f'# {title}\n\nStatus: {status}\nLast updated: {DATE}\nVersion: 0.1\nScope: {scope or title}\n'
    if path!='README.md':
        header+='\n## Edit History\n\n| Date | Version | Edited by | Reason |\n| ---- | ------- | --------- | ------ |\n| 2026-10-05 | 0.1 | Codex | Established the independent research project. |\n'
    p.write_text(header+'\n'+body.strip()+'\n')

write('README.md','Brazil Research Project', '''This project organizes the existing Brazil census, infrastructure, land-value, and conference research into reproducible workflows. Python handles analysis, harmonisation, infrastructure processing, and charts. Isolated R adapters retain census acquisition and the geographic sf/S2 overview. The original OneDrive folder is unchanged.

Start with [agent instructions](AGENTS.md), the [documentation index](docs/index.md), and the [current progress report](docs/current/current-progress-report.md). The [migration plan](docs/current/migration-plan.md) distinguishes delivered behavior from remaining validation.

## Setup

The tested Python runtime is 3.9.6. Use a project environment and the exact dependency lock.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/brazil-project --help
```

For retained R workflows, install R matching `renv.lock`, then restore into the project library:

```sh
Rscript scripts/r/restore.R
```

## Run research

The copied inputs and imported local census cache are already available on this computer. Routine runs do not acquire remote data.

```sh
.venv/bin/brazil-project run all --config config/project.toml
.venv/bin/brazil-project run charts --municipality 3106200
.venv/bin/brazil-project verify-parity
.venv/bin/python -m pytest -q
```

`all` attempts every research stage, records failures, and exits nonzero if any stage is blocked. The original property workflow requires a missing cadastral CSV, so the full run currently reports that blocker. Use [run commands](docs/technical/workflow.md) for focused work.

Default census correspondence uses the original archived lookups. Use `--recompute-harmonisation` explicitly for the Python geometric implementation. Municipality subsets retain complete comparison groups, including their tracts outside the selected municipality.

## Acquire inputs explicitly

```sh
.venv/bin/brazil-project import-cache /path/to/censobr/data_release_v0.5.0
.venv/bin/brazil-project run acquire-census
.venv/bin/brazil-project run acquire-ibama
.venv/bin/brazil-project run acquire-obrasgov
```

Infrastructure adapters cache requests and resume incomplete snapshots. A new harvest requires a new snapshot directory; never mix a fresh harvest into an existing snapshot.

## Project layout

- `src/brazil_project/` contains Python workflow components.
- `scripts/r/` contains retained adapters and independent reference validation.
- `config/` defines project-relative paths and translated category mappings.
- `notebooks/` preserves Quarto narrative and chunk order with Python artifact views.
- `data/` separates copied inputs, references, original results, and new intermediates.
- `outputs/` contains new figures, maps, and tables.
- `research/` contains manuscripts and conference material.
- `archive/` preserves original code, outputs, backups, and session files.
- `docs/` provides methods, provenance, migration, current state, and verification.

Copied data and generated outputs stay outside Git. The complete file manifest records every original file and checksum. No project-wide software or data license is inferred from the source material.''')
write('AGENTS.md','Agent Working Instructions','''These rules apply to this independent research project. RISSI provided documentation patterns; its application architecture and deployment rules do not apply here.

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

A completed task records affected stages, commands, inputs and scope, outputs, checks, remaining blockers, and current next steps. A future agent must be able to resume from repository documentation without reconstructing chat history.''')
write('NOTICE.md','Sources And Attribution','''The original research material was copied from the user's Brazil Project folder in OneDrive. It includes IBGE census data and boundaries, IBAMA environmental licensing geometries, Obrasgov infrastructure records, Belo Horizonte property references, and CS2Nordic research material. Original license and attribution documents are retained where present. This notice does not grant redistribution rights.

Documentation and agent-rule patterns were adapted from the user's RISSI repository, specifically its root AGENTS.md. Brazil remains an independent research project; no RISSI application code, operational defaults, or deployment infrastructure was copied.

Python processing was translated from the user's original R and Quarto workflows. `archive/original_code/` and `docs/reference/workflow_mapping.csv` preserve their provenance.

Retained R packages include censobr, geobr, and sf/S2. Python uses pandas, GeoPandas, Shapely, NetworkX, PyArrow, requests, matplotlib, openpyxl, and Folium. Their own licenses remain applicable. Dependency versions are recorded in the Python and R locks.

Generated interactive maps retain the selected basemap's visible attribution. External basemap tiles may require network access when viewing a map; producing the analysis does not download original research data by default.''')
write('docs/index.md','Research Project Documentation','''This index is the starting point for maintaining the project and understanding the processing flow.

- [Current progress](current/current-progress-report.md)
- [Remaining tasks](current/todo.md)
- [Migration plan](current/migration-plan.md)
- [Research methods](methods/research-methods.md)
- [Workflow and commands](technical/workflow.md)
- [R integration](technical/r-integration.md)
- [Data provenance](reference/data-provenance.md)
- [Verification results](verification/results.md)
- [Source file migration manifest](reference/migration_manifest.csv)
- [Original workflow chunk mapping](reference/workflow_mapping.csv)

Folder READMEs explain local responsibilities. Methods explain scientific definitions. Verification records state what has actually been checked.''')
write('docs/current/migration-plan.md','Brazil Project Migration Plan','''## Implemented project organization

The complete original folder is copied locally, classified, and checksum verified. Research documents are separated from executable code; original scripts, Quarto notebooks, backups, outputs, and session files remain recoverable. Duplicate contents are recorded and conflicting files are never overwritten silently.

The migration manifest accounts for all 344 original files totaling 12,175,700,758 bytes. It records 78 additional files sharing already-seen content checksums. Existing GeoPackages remain original baselines; new results use independent intermediates.

## Workflow migration

The Python runner exposes explicit acquisition, overview, harmonisation, indicators, infrastructure, land-value, and chart stages. Acquisition does not run as a dependency of routine analysis. Failed stages are recorded and return a nonzero result.

Census and boundary acquisition remain isolated R adapters. The exploratory geographic overview retains sf/S2 to preserve spherical intersection behavior. Python performs projected correspondence, annual indicators, income, population density, infrastructure processing, and conference chart calculations.

The original workflow ordering and narrative are retained through Python-backed Quarto views. Each original executable chunk is mapped to its implementation and artifact contract. Original R code remains available for independent reference validation.

## Validation strategy

Compare copies against original SHA256 checksums. Validate synthetic edge cases, complete common-area membership, original stored outputs, fresh R reference calculations, chart populations, cutoffs, and rendered figures. Store reference mismatches as evidence instead of changing the original files.

Python correspondence recomputation is explicit; routine runs continue using the original crosswalk while national recomputation parity remains unverified.

## Completion boundaries

All existing research areas are represented. The property notebook's workbook and available geometry imports are implemented, but its exact cadastral CSV is missing from the original folder. Fresh infrastructure downloads are implemented with resumable caches and tested response handling; live external endpoint equivalence is not claimed without a recorded acquisition run.

Published research methods are not corrected as part of restructuring. Data defects and differences between current source code and stored results are documented for scientific review.''')
write('docs/methods/research-methods.md','Research Processing Methods','''## Census correspondence

The original method transforms 2010 and 2022 tracts to EPSG:5880, sets precision at 1e6, and makes geometry valid. Each year selects its largest overlap in the other year. The union of both directional match sets forms an undirected graph; connected components define common comparison areas. Relations are classified as one to one, split, merge, or many to many.

The display base preserves prepared 2022 tract geometries. It is not dissolved or split for indicator display. Component numbers are labels; membership is the invariant. Imported correspondence remains the default while recomputation parity is verified separately.

The original national base contains 4,681 duplicate IDs among 472,778 rows. These rows remain present. Aggregation deduplicates each tract-to-common-area key before summing, preventing those display duplicates from multiplying counts.

## Annual proportions

Black, Brown, combined Black/Brown, literacy, rudimentary sanitation, water network, waste collection, sewer/septic, houses, village/condominium houses, and apartment indicators retain their original census variable mappings in the Python implementation.

Combined temporal counts coalesce specified missing components to zero. Most temporal aggregations ignore missing count entries; housing denominators remain missing when every denominator is missing. Ratios require positive denominators. Annual estimates are joined with an outer join; an absent year is not replaced by zero. Changes in proportions are differences and percentage-point values are those differences multiplied by 100.

Literacy uses the 2022 Pessoas table's own tract population, independently of whether the Basico table contains that tract. This distinction was verified against the original R implementation.

## Income

2010 income uses V020 household heads, V021 recipients, and V022 total income. Its tract mean is total income divided by valid positive recipients. The 2022 inputs use V06001 heads and V06004 mean income.

The implemented original aggregation weights valid tract means by household heads. Numerator and denominator use exactly the same eligible pairs. Missing weights and means are reported; incomplete coverage does not itself block the mean. Nominal 2010 results are multiplied by 6645.74 / 3200.06 to express July 2022 reais.

The original prose claims stronger restrictions on multi-tract means than its code actually imposes. The migration preserves the code and records the discrepancy rather than changing the method.

## Population density

Counts retain missing totals when every contributing value is missing. Component polygons are repaired, transformed to equal-area EPSG:6933, and dissolved to measure common-area km2. Density equals population divided by area. Absolute change is people per km2; relative change is the percentage change from a positive 2010 density.

The stored original population_density_change column repeats percentage changes rather than the absolute difference used by current source code. Both stored outputs and current source are retained. Fresh R reference validation determines translation parity.

## Conference sanitation charts

Unlike temporal rudimentary sanitation, conference inadequate sanitation includes no bathroom or toilet and excludes a tract from both numerator and denominator when any required component is missing or invalid. A group's 2022 component tracts must all be urban.

The change chart requires eligible data in both years. Racial-composition quintiles use paired 2022 areas, ordered by share then common_id, with larger ntile buckets first. The income chart independently uses all eligible urban 2022 areas; income tertile cutoffs are calculated before selecting the lowest and highest racial quintiles. Income intervals are right closed.

## Infrastructure and land value

IBAMA merges licensed point, line, and polygon records and translates sectors. Obrasgov expands taxonomy, sums planned investments, combines project pins, enriches available multidimensional geometries, translates categories, and removes empty or out-of-range geometries before repairing retained geometries.

Property processing remains exploratory. Its valuation workbook was parsed using AI in the original project and has not been independently authenticated. Exact dated inputs are required; no alternate date is substituted.

## Geographic overview

The original exploratory 2000-to-2010/2022 comparison is limited to Belo Horizonte. It classifies older tracts using overlap fractions of newer tracts: greater than 5 percent establishes a substantial match; a single match over 95 percent is stable. The sf/S2 adapter retains original geographic topology and area semantics.''')
write('docs/technical/workflow.md','Workflow Commands And Artifacts','''## Stage commands

Run commands from the project root using `.venv/bin/brazil-project`.

| Stage | Inputs | Outputs | Acquisition |
| --- | --- | --- | --- |
| overview | Original tract GeoPackage | Spherical intersections and comparison summaries | No |
| harmonisation | Original tracts or baseline lookup and geometry | Crosswalk lookups, group sizes, base geometry | No |
| indicators | Census Parquet and lookups | Annual common-area estimates and spatial indicator tables | No |
| ibama | Copied or acquired licensed projects | Sector translations and interactive map | No |
| obrasgov | Copied or acquired project records | Category counts, charts, cleaned geometry | No |
| land-value | Exact dated CSVs and valuation workbook | Annex tables and property geometries | No |
| charts | Saved census, indicators, and lookups | Conference populations, summaries, and PNGs | No |
| acquire-census | censobr and geobr sources | Versioned Parquet and tract GeoPackage | Explicit |
| acquire-ibama | PAMGIA FeatureServer layers | Cached responses and licensed-project GeoParquet | Explicit |
| acquire-obrasgov | Project and geometry APIs | Cached pages, enrichment provenance, project GeoParquet | Explicit |

```sh
.venv/bin/brazil-project run harmonisation
.venv/bin/brazil-project run indicators
.venv/bin/brazil-project run charts
.venv/bin/brazil-project run obrasgov
.venv/bin/brazil-project run land-value
.venv/bin/brazil-project run all
```

Indicators run harmonisation first; charts run both dependencies. `all` attempts remaining independent stages after failures, records evidence, and exits nonzero when incomplete. Acquisition is never implicit.

## Configuration and subsets

`config/project.toml` resolves paths relative to its project root. The national scope is the default. `--municipality 3106200` selects Belo Horizonte display tracts, retains every contributing tract in their common areas, and writes independent subset intermediates under `data/intermediate/municipality_3106200/`.

The overview retains its original Belo Horizonte scope when no municipality override is supplied. Correspondence recomputation uses the explicitly requested tract selection; its reference check must use the same selection.

## Artifact contracts

Tables use Parquet and spatial artifacts use GeoParquet. Identifiers are normalized to strings without float suffixes. Lookup keys must be unique after deduplicating repeated tract-to-group records. Original display duplicate geometry rows are preserved and reported.

Every stage writes a JSON report. Routine output publication uses temporary files and atomic replacement. Missing inputs produce actionable errors rather than empty results. National and municipality artifacts do not overwrite one another.

## Repeatability and verification

```sh
python3 scripts/migrate_files.py --verify-only
.venv/bin/python -m pytest -q
.venv/bin/brazil-project verify-parity
Rscript scripts/r/validate_reference.R "$PWD" 3106200
.venv/bin/python scripts/verify_r_reference.py --municipality 3106200
```

The first parity command compares stored original outputs and may intentionally report known source/baseline differences. Fresh R reference validation checks current original calculations separately. Reference validation reads archived code and local inputs only; it never sources the original save chunk or writes to OneDrive.''')
write('docs/technical/r-integration.md','Retained R Components','''## Retained capabilities

| Component | Reason | Exchange | Replacement condition |
| --- | --- | --- | --- |
| Census and boundary acquisition | Preserve censobr/geobr source and release behavior | Parquet and GeoPackage | Verified Python acquisition reproduces the required data and metadata |
| Geographic dataset overview | Original sf/S2 spherical intersections are not established as equivalent in the Python stack | GeoPackage and CSV | Verified equivalent geographic topology and area |
| Independent reference validation | Compare translations to the original implementation | CSV and GeoPackage | Remains a reference tool while migration parity is maintained |

Projected harmonisation, annual processing, infrastructure adapters, and charts run in Python.

## Runtime and dependency isolation

`renv.lock` records R 4.6.0 and package versions. `scripts/r/bootstrap.R` selects project-local libraries, caches, and sandbox paths. `scripts/r/restore.R` restores dependencies. The local installation was hydrated from existing matching installed packages; fresh machines restore from the lock.

Adapters are invoked through Rscript with explicit project, input, output, and scope arguments. They do not depend on an RStudio workspace. The Python runner checks exit status and expected files. Missing runtimes and packages return actionable setup errors.

## Data boundary

Census Parquet requires code_tract with unique nonmissing values and original variable columns. Tract GeoPackages retain original layer names. No data frame is exchanged through an implicit global session between stages. Every retained R component writes inside the local project.

## Reference checks

`validate_reference.R` reconstructs the original temporal processing in a fresh process, excludes original acquisition and save chunks, and writes isolated common-area and chart tables. Municipality references include complete comparison groups. `harmonisation_reference.R` evaluates the original projected correspondence for an explicit test scope.

Network acquisition and dependency restore are separate from ordinary analysis. Infrastructure live endpoints remain subject to provider availability; a cached-input run does not verify a new external acquisition.''')
write('docs/reference/data-provenance.md','Data Provenance And Migration','''## Original project

Source folder: `/Users/fa4850sc/Library/CloudStorage/OneDrive-LundUniversity/Brazil Project`.

Every original file has a row in migration_manifest.csv with original relative path, destination, byte count, SHA256, classification, duplicate-content reference, and copy status. Existing duplicated contents are retained with their paths; no scientific consolidation was assumed. Copy verification reads original and copied files and compares both against the recorded hash.

All 344 files were copied and checksum verified. The original bytes total 12,175,700,758. No source file was edited or removed.

## Additional local inputs

Eight existing censobr v0.5.0 Parquet inputs were imported from the user's local R cache. Their full source paths and checksums are recorded in `data/raw/ibge/census/provenance.json`. They were not downloaded during migration. The optional R adapter retains censobr acquisition for future input recovery.

## Data classifications

Raw contains original source tables and boundaries. Reference contains codebooks, inflation workbooks, valuation references, and supplied PDFs. Processed contains copied original outputs used as baselines. Intermediate contains new reproducible stage artifacts. Archive contains original code, outputs, backups, and session files.

Original notes remain verbatim under `docs/reference/original_notes/`. Files that describe legacy working directories should be interpreted with the migration manifest rather than edited retroactively.

## Source limitations

The 2022 display base has duplicate tract IDs. The cadastral CSV referenced by the property notebook is absent. A parsed valuation workbook is an exploratory input rather than an authenticated legal interpretation. Source package caching and live provider access may have restrictions recorded in the original notes.''')
# Evidence is finalized after verification; this initial state is explicit.
write('docs/current/current-progress-report.md','Current Project Progress','''The complete original file collection is copied, organized, and checksum verified. The Python package and CLI are installed locally. Python dependencies and retained R dependencies are locked.

Python annual indicators and conference chart populations are implemented, and national outputs have been generated. Infrastructure snapshot processing is implemented; Obrasgov retains 133,417 records after cleaning, matching the original snapshot. IBAMA includes 8,494 records with translated sectors. Land-value annex imports and the available zone geometry are implemented; the exact cadastral input remains missing.

Verification is being finalized in [results](../verification/results.md). Known stored-output discrepancies remain visible and are compared independently to current R source calculations. National crosswalk recomputation and live external harvest parity are not declared validated.''',status='implemented with validation in progress')
write('docs/current/todo.md','Remaining Research Tasks','''- Supply the exact `20220601_regional_barreiro_cadastro_imobiliario.csv` referenced by the property notebook, or approve a separate dated-input methodological change.
- Review original duplicate tract IDs and decide scientifically whether an independently versioned correction is warranted.
- Review the original stored density absolute-change discrepancy and the income prose/code discrepancy separately from translation.
- Verify full national correspondence recomputation before replacing the original default crosswalk.
- Record live IBAMA and Obrasgov acquisition comparisons against provider snapshots when acquisition is requested.
- Render the Python-backed Quarto reports after installing Quarto and its Python reporting dependencies. Local table/figure generation remains available without Quarto.
- Do not mark scientific or publication review complete merely because software tests pass.''')
write('docs/verification/results.md','Verification Results','''## File integrity

All 344 original files were copied and SHA256 verified. The verification utility also rereads the OneDrive originals and confirms their recorded content hashes.

## Implemented checks

Focused tests cover projected correspondence, relations, unmatched tracts and ties, geometry preservation, count missingness, zero denominators, duplicate keys, weighted income, chart sanitation exclusions, ntile grouping, request resumption, wrong pages, fingerprints, and nested infrastructure records.

Independent evidence includes original stored-output comparisons and fresh R reference calculations. JSON reports under `data/intermediate/` record exact scopes, numerical tolerances, differences, and outcomes. Final results are updated after the latest checks.

## Limits

Missing property input prevents that exploratory workflow from completing. New live infrastructure downloads were not performed. Quarto HTML rendering requires a separately installed Quarto runtime. Archived results are preserved even when they differ from current code.''',status='validation in progress')
folders={
'config':('Workflow Configuration','Paths and scientific constants in project.toml; original Obrasgov translations in obrasgov_translations.json. Paths resolve against the configured root. Update methods and tests whenever scientific configuration changes.'),
'src':('Python Source','The brazil_project package implements the workflow runner and scientific modules. Install through pyproject.toml; never execute package code by changing to an undocumented working directory.'),
'src/brazil_project':('Research Workflow Package','cli.py coordinates explicit stages; io.py owns paths, artifact publication and key contracts; verification.py compares stored results. Modules connect through saved stage artifacts. Inputs are copied local data; outputs are new intermediates and figures.'),
'scripts':('Project Utilities','migrate_files.py copies and verifies original files. verify_r_reference.py compares fresh independent exports. create_project_docs.py builds initial documentation; maintaining current documentation afterward requires deliberate edits. The r folder retains isolated R adapters and reference checks.'),
'scripts/r':('R Adapters And Reference Checks','bootstrap.R isolates package libraries. restore.R restores renv.lock. acquire_census.R acquires versioned tables and boundaries. overview.R preserves geographic sf/S2 comparisons. validate_reference.R and harmonisation_reference.R compare original processing. Inputs and outputs are explicit local paths; never source the original save chunks.'),
'notebooks':('Research Reports','Python-backed Quarto documents preserve original narrative and chunk order. They display artifacts produced by the stage runner and do not execute network acquisition while rendering. Install Quarto and the reports optional Python dependencies to render. See workflow_mapping.csv for original chunk provenance.'),
'data':('Research Data','raw contains immutable original inputs; processed contains original result baselines; reference contains supplied codebooks and workbooks; intermediate contains generated stage results. Full datasets remain outside Git. Provenance is documented under docs/reference.'),
'outputs':('Generated Research Outputs','figures contains new PNGs; maps contains attributed interactive HTML; tables contains exports where requested. Outputs are reproducible and ignored by Git. Preserve original outputs under archive/original_outputs.'),
'research':('Research Materials','manuscripts holds paper material; presentations/cs2nordic holds copied conference documents and presentations. These documents remain original research artifacts; restructuring does not certify their findings.'),
'research/manuscripts':('Research Manuscripts','This folder is reserved for future manuscript work. No manuscript content is invented during migration.'),
'research/presentations':('Conference Materials','cs2nordic contains copied conference material. Preserve originals and use explicit new versions for subsequent edits.'),
'archive':('Original Project Archive','original_code preserves R, Quarto and backups; original_outputs preserves figures and other outputs; session_files preserves hidden state and editor artifacts. This archive is immutable reference material outside Git. Use migration_manifest.csv to recover original locations.'),
'archive/original_code':('Original Research Code','These original code files are retained verbatim. They are reference and validation inputs. Active Python and justified R implementations live under src and scripts/r. Do not execute original save chunks against OneDrive.'),
'archive/original_outputs':('Original Research Outputs','Copied original outputs are baselines and provenance. Do not overwrite them with regenerated results.'),
'archive/session_files':('Original Session Files','Hidden editor state, histories, temporary files and lock files are preserved for recovery. They are not reproducible workflow inputs.'),
'data/raw':('Immutable Raw Inputs','Source-specific original datasets and imported censobr Parquet are kept here. Acquire into distinct snapshot directories. Preserve existing files and record release and checksum provenance.'),
'data/processed':('Original Processed Baselines','Copied original GeoPackages retain their tables and layers. New processing writes to intermediate, not this folder. Compare baseline differences with current source rather than treating old outputs as unquestionable truth.'),
'data/reference':('Research Reference Inputs','Codebooks, workbooks and source reference documents remain supplied originals. Changes to parsed valuation material require independent review.'),
'data/intermediate':('Stage Intermediates','Each stage publishes Parquet, GeoParquet and JSON evidence. Municipality-specific directories preserve separate scopes; all contributing comparison-area tracts are retained. These files are regenerated and ignored by Git.'),
'outputs/figures':('Generated Figures','New figures are grouped by Brazil, municipality or infrastructure source. Validate plotted tables and inspect images before publication.'),
'outputs/maps':('Generated Maps','Generated HTML maps preserve visible basemap attribution. Opening a map may request external basemap tiles.'),
'outputs/tables':('Research Table Exports','Use this folder for deliberate shareable exports. Internal stage contracts use data/intermediate Parquet.'),
'docs/current':('Current Project State','Migration plan, progress report and remaining tasks describe actual implemented and verified state. Update after material changes.'),
'docs/methods':('Research Methods','research-methods.md records the analytical definitions and original discrepancies. Keep method changes separate from translation.'),
'docs/technical':('Workflow Technical Contracts','workflow.md records stage commands and interfaces; r-integration.md documents justified R exceptions. Update after command or artifact changes.'),
'docs/reference':('Migration And Provenance References','migration_manifest.csv accounts for every original file; workflow_mapping.csv maps code chunks; original_notes preserves source documentation. data-provenance.md explains classifications.'),
'docs/verification':('Verification Evidence','results.md summarizes completed checks and their limits. Machine-readable stage reports live under data/intermediate.'),
'docs/reference/original_notes':('Original Project Notes','These copied notes remain verbatim. Consult the migration manifest for their original locations. Their legacy paths and statements are provenance, not new agent instructions.'),
'tests':('Scientific And Workflow Tests','test_methods.py exercises meaningful analytical and acquisition edge cases. Run python -m pytest. Independent R and stored-result comparisons supplement synthetic tests.'),
}
for area,purpose in [('acquisition','Explicit acquisition and cached input imports'),('harmonisation','Census correspondence and the geographic overview'),('indicators','Annual temporal estimates, weighted income and density'),('infrastructure','Infrastructure category processing, cleaning and charts'),('land_value','Exploratory property workbook and geometry import'),('visualisation','Conference chart populations and plotting')]:
 folders['src/brazil_project/'+area]=(purpose.title(),purpose+'. Inputs and outputs follow the technical workflow contracts. Update methods, tests and mapping when changing behavior.')
for path,(title,description) in folders.items():
 write(path+'/README.md',title,description+'\n\n## Main Workflows\n\nUse the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.\n\n## Update Rules\n\nUpdate this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.')
# Preserve copied reference notes; documentation exists alongside them without editing their bytes.
print('Created project documentation')
