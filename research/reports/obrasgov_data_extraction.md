# Obrasgov.br Data

Executable research report. Refresh with `brazil-project report obrasgov_data_extraction`. Code is collapsed below each explanation.

## Data Extraction


<details>
<summary>Python code</summary>

<!-- brazil:cell obrasgov_data_extraction_1 -->
```python
#| label: obrasgov_data_extraction_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 1)
```

</details>

<!-- brazil:output obrasgov_data_extraction_1 begin -->
```text
{'records': 134929,
 'cleaned_records': 133417,
 'removed': 1512,
 'baseline_cleaned_records': 133417,
 'count_matches_baseline': True,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:10:12.235992+00:00'}
```
<!-- brazil:output obrasgov_data_extraction_1 end -->

First we retrieve all projects.


<details>
<summary>Python code</summary>

<!-- brazil:cell obrasgov_data_extraction_2 -->
```python
#| label: obrasgov_data_extraction_2
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 2)
```

</details>

<!-- brazil:output obrasgov_data_extraction_2 begin -->
```text
{'records': 134929,
 'cleaned_records': 133417,
 'removed': 1512,
 'baseline_cleaned_records': 133417,
 'count_matches_baseline': True,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:10:12.235992+00:00'}
```
<!-- brazil:output obrasgov_data_extraction_2 end -->

Then we transform the nested tables into columns.


<details>
<summary>Python code</summary>

<!-- brazil:cell obrasgov_data_extraction_3 -->
```python
#| label: obrasgov_data_extraction_3
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 3)
```

</details>

<!-- brazil:output obrasgov_data_extraction_3 begin -->
```text
{'records': 134929,
 'cleaned_records': 133417,
 'removed': 1512,
 'baseline_cleaned_records': 133417,
 'count_matches_baseline': True,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:10:12.235992+00:00'}
```
<!-- brazil:output obrasgov_data_extraction_3 end -->

The Obrasgov API only allows for the extraction of point geometries. In order to enrich the dataset with multidimensional geometries we have to resort to another endpoint. Using Obrasgovr we first extract the geo-data metadata to identify which geometries are potentially multidimensional.


<details>
<summary>Python code</summary>

<!-- brazil:cell obrasgov_data_extraction_4 -->
```python
#| label: obrasgov_data_extraction_4
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 4)
```

</details>

<!-- brazil:output obrasgov_data_extraction_4 begin -->
```text
{'records': 134929,
 'cleaned_records': 133417,
 'removed': 1512,
 'baseline_cleaned_records': 133417,
 'count_matches_baseline': True,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:10:12.235992+00:00'}
```
<!-- brazil:output obrasgov_data_extraction_4 end -->

With the filtered IDs, we extract the full geometries.


<details>
<summary>Python code</summary>

<!-- brazil:cell obrasgov_data_extraction_5 -->
```python
#| label: obrasgov_data_extraction_5
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 5)
```

</details>

<!-- brazil:output obrasgov_data_extraction_5 begin -->
```text
{'records': 134929,
 'cleaned_records': 133417,
 'removed': 1512,
 'baseline_cleaned_records': 133417,
 'count_matches_baseline': True,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:10:12.235992+00:00'}
```
<!-- brazil:output obrasgov_data_extraction_5 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell obrasgov_data_extraction_6 -->
```python
#| label: obrasgov_data_extraction_6
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 6)
```

</details>

<!-- brazil:output obrasgov_data_extraction_6 begin -->
```text
{'records': 134929,
 'cleaned_records': 133417,
 'removed': 1512,
 'baseline_cleaned_records': 133417,
 'count_matches_baseline': True,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:10:12.235992+00:00'}
```
<!-- brazil:output obrasgov_data_extraction_6 end -->

::: callout-note
- Metadata can be extracted for the individual geometries. For now, geometries were merged by project ID.
:::

We then join both tables and end up with the final data set for further manipulation.


<details>
<summary>Python code</summary>

<!-- brazil:cell obrasgov_data_extraction_7 -->
```python
#| label: obrasgov_data_extraction_7
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 7)
```

</details>

<!-- brazil:output obrasgov_data_extraction_7 begin -->
```text
{'records': 134929,
 'cleaned_records': 133417,
 'removed': 1512,
 'baseline_cleaned_records': 133417,
 'count_matches_baseline': True,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:10:12.235992+00:00'}
```
<!-- brazil:output obrasgov_data_extraction_7 end -->
