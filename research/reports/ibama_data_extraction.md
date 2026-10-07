# IBAMA - Data Extraction

Executable research report. Refresh with `brazil-project report ibama_data_extraction`. Code is collapsed below each explanation.


<details>
<summary>Python code</summary>

<!-- brazil:cell ibama_data_extraction_1 -->
```python
#| label: ibama_data_extraction_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 1)
```

</details>

<!-- brazil:output ibama_data_extraction_1 begin -->
```text
{'records': 8494,
 'unknown_sectors': 0,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:05:40.860588+00:00'}
```
<!-- brazil:output ibama_data_extraction_1 end -->

We will extract three layers separately containing point, line and polygon geometries from the [PAMGIA](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO) endpoint:

- tb_empreendimento_repr_p

- tb_empreendimento_repr_l

- tb_empreendimento_repr_a


<details>
<summary>Python code</summary>

<!-- brazil:cell ibama_data_extraction_2 -->
```python
#| label: ibama_data_extraction_2
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 2)
```

</details>

<!-- brazil:output ibama_data_extraction_2 begin -->
```text
{'records': 8494,
 'unknown_sectors': 0,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:05:40.860588+00:00'}
```
<!-- brazil:output ibama_data_extraction_2 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibama_data_extraction_3 -->
```python
#| label: ibama_data_extraction_3
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 3)
```

</details>

<!-- brazil:output ibama_data_extraction_3 begin -->

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tp_sector_en</th>
      <th>projects</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Energy</td>
      <td>2013</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Mining</td>
      <td>420</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Nuclear/Radioactive</td>
      <td>25</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Oil and Gas</td>
      <td>219</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Other</td>
      <td>512</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Transportation</td>
      <td>5233</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Water Resources</td>
      <td>72</td>
    </tr>
  </tbody>
</table>


```text
{'artifact_rows': 7, 'path': 'data/intermediate/ibama/sector_counts.parquet'}
```
<!-- brazil:output ibama_data_extraction_3 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibama_data_extraction_4 -->
```python
#| label: ibama_data_extraction_4
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 4)
```

</details>

<!-- brazil:output ibama_data_extraction_4 begin -->
```text
{'records': 8494,
 'unknown_sectors': 0,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:05:40.860588+00:00'}
```

Local interactive map (outside Git): `outputs/maps/ibama.html`
<!-- brazil:output ibama_data_extraction_4 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibama_data_extraction_5 -->
```python
#| label: ibama_data_extraction_5
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 5)
```

</details>

<!-- brazil:output ibama_data_extraction_5 begin -->
```text
{'records': 8494,
 'unknown_sectors': 0,
 'source': 'copied_snapshot',
 'generated_at': '2026-10-07T07:05:40.860588+00:00'}
```
<!-- brazil:output ibama_data_extraction_5 end -->
