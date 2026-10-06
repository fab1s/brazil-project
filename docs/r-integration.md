# Retained R Components

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Retained R Components

## Retained capabilities

| Component | Reason | Exchange | Replacement condition |
| --- | --- | --- | --- |
| Census and boundary acquisition | Preserve censobr/geobr source and release behavior | Parquet and GeoPackage | Verified Python acquisition reproduces the required data and metadata |
| Geographic dataset overview | Original sf/S2 spherical intersections are not established as equivalent in the Python stack | GeoPackage and CSV | Verified equivalent geographic topology and area |
| Independent reference validation | Compare translations to the original implementation | CSV and GeoPackage | Remains a reference tool while migration parity is maintained |

Projected harmonisation, annual processing, infrastructure adapters, and charts run in Python.

## Runtime and dependency isolation

`renv.lock` records R 4.6.0 and package versions. `code/scripts/r/bootstrap.R` selects project-local libraries, caches, and sandbox paths. `code/scripts/r/restore.R` restores dependencies. The local installation was hydrated from existing matching installed packages; fresh machines restore from the lock.

Adapters are invoked through Rscript with explicit project, input, output, and scope arguments. They do not depend on an RStudio workspace. The Python runner checks exit status and expected files. Missing runtimes and packages return actionable setup errors.

## Data boundary

Census Parquet requires code_tract with unique nonmissing values and original variable columns. Tract GeoPackages retain original layer names. No data frame is exchanged through an implicit global session between stages. Every retained R component writes inside the local project.

## Reference checks

`validate_reference.R` reconstructs the original temporal processing in a fresh process, excludes original acquisition and save chunks, and writes isolated common-area and chart tables. Municipality references include complete comparison groups. `harmonisation_reference.R` evaluates the original projected correspondence for an explicit test scope.

Network acquisition and dependency restore are separate from ordinary analysis. Infrastructure live endpoints remain subject to provider availability; a cached-input run does not verify a new external acquisition.

The spherical overview uses indexed S2 candidate pairs and by-element semi-open intersections. A focused R test confirms the same attributes and areas as sf's original all-pairs operation, while avoiding its quadratic spherical dispatch. This changes execution cost, not the geographic method.
