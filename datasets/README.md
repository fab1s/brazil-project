# Final map datasets

Status: current
Last updated: 2026-10-26
Version: 0.1
Scope: Four readable, executable dataset handoffs

Open a folder below, read its short README, then open `build.ipynb`. Each notebook explains and runs the existing processing path, shows a few checks, and writes a verified `final.gpkg` copy locally after a successful build. GitHub displays the saved notebook results; running it requires the [locked local environment](../docs/workflow.md) and the [restored source data](../data/README.md#recovering-local-baselines-on-another-machine).

| Dataset | Notebook | Local final file | Status |
| --- | --- | --- | --- |
| Census comparison areas | [census/build.ipynb](census/build.ipynb) | `census/final.gpkg` | Rebuilds harmonisation, indicators and the English-field GeoPackage. |
| Obrasgov locations | [obrasgov/build.ipynb](obrasgov/build.ipynb) | `obrasgov/final.gpkg` | Rebuilds the approved component-level map derivative. |
| IBAMA licensing | [ibama/build.ipynb](ibama/build.ipynb) | `ibama/final.gpkg` | Reruns translation, verifies baseline parity, then copies the baseline. |
| IBGE communities | [communities/build.ipynb](communities/build.ipynb) | `communities/final.gpkg` | Verifies and copies the preserved baseline without changing its geometry. |

Run all cells in a notebook to build its local output. Notebooks default to processing; `BRAZIL_NOTEBOOK_REBUILD=0` is only a read-only preview of already saved outputs. The preview figures committed to GitHub are labeled accordingly. No notebook automatically acquires new provider data or publishes the website.

`final.gpkg` is an ignored, self-contained local copy of the verified output. A collaborator can use that file after receiving its dataset folder; rerunning the notebook requires the full repository and restored local inputs. Full GeoPackages are not in GitHub, so include the local binaries when sharing folders. The [handoff table](../docs/collaborator-data-handoff.md) gives their contents and methods. Website tiles simplify or quantise geometry for display. A local identifier check finds all community IDs but only 8,492 of 8,494 IBAMA source IDs in the frozen tiles; full attribute and geometry equivalence remains unverified.
