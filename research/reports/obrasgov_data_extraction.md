# Obrasgov inputs and acquisition

Explain how the saved infrastructure snapshot was assembled and what ordinary runs consume. Rendering this report does not download projects or rerun the original extraction sequence.

[Variable and dataset codebook](../../docs/codebook.md) · [Methods](../../docs/methods.md) · [All reports](../README.md#read-the-reports)

Refresh processing and this report with `brazil-project report obrasgov_data_extraction --config project.toml`. Add `--from-saved` to refresh existing verified artifacts only. Code is collapsed; tables and figures below are saved execution results.

## Processing code and pipeline

Execution order: `obrasgov-snapshot` → `obrasgov-location-qa` → `obrasgov-location-plot` → `obrasgov-primary-state-check` → `obrasgov-primary-state-filter`. The [cli.py → dispatch()](../../code/brazil_project/cli.py#L23) dispatcher calls these functions; [cli.py → expand()](../../code/brazil_project/cli.py#L58) resolves dependencies. The cells below read their saved outputs and present the results.

| Pipeline stage | Active processing source | Inputs | Saved outputs used by the process/report |
| --- | --- | --- | --- |
| `obrasgov-snapshot` | [projects.py → run()](../../code/brazil_project/infrastructure/projects.py#L47) | Configured snapshot or completed local acquisition; source=obrasgov | `obrasgov/projects.parquet; projects_clean.parquet; translated category counts` |
| `obrasgov-location-qa` | [location_qa.py → run()](../../code/brazil_project/infrastructure/location_qa.py#L218) | Preserved source snapshot from location_qa.source and pinned reference boundaries | `obrasgov-location-qa/component_audit.parquet; map, quarantine and review tables` |
| `obrasgov-location-plot` | [plot_location_qa.py → run()](../../code/scripts/plot_location_qa.py#L35) | Component audit and pinned municipal reference | `outputs/figures/obrasgov-location-qa/location-screening.png` |
| `obrasgov-primary-state-check` | [check_obras_primary_state.py → run()](../../code/scripts/check_obras_primary_state.py#L54) | Complete component geometry, uf_principal and IBGE state territory | `outputs/tables/obrasgov-primary-state/summary.json and component-level checks` |
| `obrasgov-primary-state-filter` | [filter_obras_primary_state.py → run()](../../code/scripts/filter_obras_primary_state.py#L103) | Completed QA and primary-state diagnostics | `obrasgov-primary-state-filter/map_components.parquet; exclusion audit and comparison figure` |

Paths without an `outputs/` prefix in this table are relative to `data/intermediate/`. Municipality runs use `data/intermediate/municipality_<code>/` and publish scoped report copies under `outputs/reports/`; national-only workflows reject municipality scope. See the [complete pipeline source guide](../../docs/pipeline-source.md) for dependencies, acquisition and the report publisher.

Live acquisition is separate: `brazil-project run acquire-obrasgov --config project.toml` invokes [infrastructure.py → run()](../../code/brazil_project/acquisition/infrastructure.py#L94). The historical extraction steps below describe provenance; ordinary report refresh does not call the API.

Explicit acquisition internals: [pages()](../../code/brazil_project/acquisition/infrastructure.py#L42) (pagination), [flatten_projects()](../../code/brazil_project/acquisition/infrastructure.py#L55) (nested records) and [enrich_projects()](../../code/brazil_project/acquisition/infrastructure.py#L70) (richer geometry). These functions are not called by ordinary snapshot report refresh.

## How to read this analysis

The original flow retrieves project records, expands nested attributes, obtains geometry metadata, requests richer geometry for eligible IDs and joins it to project records. The basic endpoint supplied point locations; a separate geometry endpoint supplied multidimensional geometry. Original R/Obrasgovr material is archived, and acquisition adapters and their remaining validation limits are documented separately.

Repeated IDs and multi-part geometry mean that source records, unique projects and geometry components are different units. The summary below checks the saved snapshot translation only; it does not verify the live API or certify geocoding. For current spatial checks and approved derivative exclusions, read [preprocessing](obrasgov_preprocessing.md).

## Inputs, coverage and processing status

This summary reads the current saved processing artifacts. Technical fingerprints are available in the collapsed provenance record.

Processing source: [projects.py → run()](../../code/brazil_project/infrastructure/projects.py#L47). Saved result: `data/intermediate/obrasgov/report.json`. Report display: [reporting.py → show_chunk()](../../code/brazil_project/reporting.py#L140).

<details>
<summary>Read saved processing summary</summary>

<!-- brazil:cell obrasgov_data_extraction_1 -->
```python
import matplotlib
matplotlib.use("Agg")  # Headless figures in the fresh report process.
#| label: obrasgov_data_extraction_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 1)
```

</details>

<!-- brazil:output obrasgov_data_extraction_1 begin -->
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Cleaning step</th>
      <th>Count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Input snapshot records</td>
      <td>134929</td>
    </tr>
    <tr>
      <td>Retained records</td>
      <td>133417</td>
    </tr>
    <tr>
      <td>Excluded from this derivative</td>
      <td>1512</td>
    </tr>
    <tr>
      <td>Archived retained-record count</td>
      <td>133417</td>
    </tr>
  </tbody>
</table>

Archived row-count agreement: **yes**. This checks counts only, not record identity or coordinate accuracy. Source: `copied_snapshot`.

<details>
<summary>Technical provenance and complete processing record</summary>

```json
{
  "records": 134929,
  "cleaned_records": 133417,
  "removed": 1512,
  "baseline_cleaned_records": 133417,
  "count_matches_baseline": true,
  "source": "copied_snapshot",
  "generated_at": "2026-10-26T14:29:25.709140+00:00"
}
```

</details>
<!-- brazil:output obrasgov_data_extraction_1 end -->

Processing source: [projects.py → run()](../../code/brazil_project/infrastructure/projects.py#L47). Saved result: `data/intermediate/obrasgov/report.json`. Report display: [reporting.py → show_chunk()](../../code/brazil_project/reporting.py#L140).

<details>
<summary>Trace original step: Unnamed 2</summary>

<!-- brazil:cell obrasgov_data_extraction_2 -->
```python
#| label: obrasgov_data_extraction_2
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 2)
```

</details>

<!-- brazil:output obrasgov_data_extraction_2 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output obrasgov_data_extraction_2 end -->

Processing source: [projects.py → run()](../../code/brazil_project/infrastructure/projects.py#L47). Saved result: `data/intermediate/obrasgov/report.json`. Report display: [reporting.py → show_chunk()](../../code/brazil_project/reporting.py#L140).

<details>
<summary>Trace original step: Unnamed 3</summary>

<!-- brazil:cell obrasgov_data_extraction_3 -->
```python
#| label: obrasgov_data_extraction_3
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 3)
```

</details>

<!-- brazil:output obrasgov_data_extraction_3 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output obrasgov_data_extraction_3 end -->

Processing source: [projects.py → run()](../../code/brazil_project/infrastructure/projects.py#L47). Saved result: `data/intermediate/obrasgov/report.json`. Report display: [reporting.py → show_chunk()](../../code/brazil_project/reporting.py#L140).

<details>
<summary>Trace original step: Geom Metadata</summary>

<!-- brazil:cell obrasgov_data_extraction_4 -->
```python
#| label: obrasgov_data_extraction_4
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 4)
```

</details>

<!-- brazil:output obrasgov_data_extraction_4 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output obrasgov_data_extraction_4 end -->

Processing source: [projects.py → run()](../../code/brazil_project/infrastructure/projects.py#L47). Saved result: `data/intermediate/obrasgov/report.json`. Report display: [reporting.py → show_chunk()](../../code/brazil_project/reporting.py#L140).

<details>
<summary>Trace original step: Geometry Enrichment</summary>

<!-- brazil:cell obrasgov_data_extraction_5 -->
```python
#| label: obrasgov_data_extraction_5
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 5)
```

</details>

<!-- brazil:output obrasgov_data_extraction_5 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output obrasgov_data_extraction_5 end -->

Processing source: [projects.py → run()](../../code/brazil_project/infrastructure/projects.py#L47). Saved result: `data/intermediate/obrasgov/report.json`. Report display: [reporting.py → show_chunk()](../../code/brazil_project/reporting.py#L140).

<details>
<summary>Trace original step: Enriched Geom Import</summary>

<!-- brazil:cell obrasgov_data_extraction_6 -->
```python
#| label: obrasgov_data_extraction_6
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 6)
```

</details>

<!-- brazil:output obrasgov_data_extraction_6 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output obrasgov_data_extraction_6 end -->

Processing source: [projects.py → run()](../../code/brazil_project/infrastructure/projects.py#L47). Saved result: `data/intermediate/obrasgov/report.json`. Report display: [reporting.py → show_chunk()](../../code/brazil_project/reporting.py#L140).

<details>
<summary>Trace original step: Unnamed 7</summary>

<!-- brazil:cell obrasgov_data_extraction_7 -->
```python
#| label: obrasgov_data_extraction_7
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 7)
```

</details>

<!-- brazil:output obrasgov_data_extraction_7 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output obrasgov_data_extraction_7 end -->

## Interpretation and limits

Outputs retain the original aggregation, missingness and exclusion rules. Available results do not establish national scientific validation. Read [verification and remaining limitations](../../docs/checks.md) before drawing research conclusions. Original codebooks and earlier report contents remain preserved in the project archive.
