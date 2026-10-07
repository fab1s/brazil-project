# IBGE Dataset Overview

Executable research report. Refresh with `brazil-project report ibge_dataset_overview`. Code is collapsed below each explanation.

This code compares census tract boundaries from 2000, 2010, and 2022 in Belo Horizonte. It measures how much the areas overlap and classifies older tracts as stable, reshaped, split, or unmatched. It then visualizes examples of these changes and compares the share of the Black population in 2010 and 2022.


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_1 -->
```python
#| label: ibge_dataset_overview_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 1)
```

</details>

<!-- brazil:output ibge_dataset_overview_1 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_1 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_2 -->
```python
#| label: ibge_dataset_overview_2
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 2)
```

</details>

<!-- brazil:output ibge_dataset_overview_2 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_2 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_3 -->
```python
#| label: ibge_dataset_overview_3
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 3)
```

</details>

<!-- brazil:output ibge_dataset_overview_3 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_3 end -->

# Census Tract

## Overlap Analysis


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_4 -->
```python
#| label: ibge_dataset_overview_4
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 4)
```

</details>

<!-- brazil:output ibge_dataset_overview_4 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_4 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_5 -->
```python
#| label: ibge_dataset_overview_5
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 5)
```

</details>

<!-- brazil:output ibge_dataset_overview_5 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_5 end -->

### 2000 -\> 2010


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_6 -->
```python
#| label: ibge_dataset_overview_6
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 6)
```

</details>

<!-- brazil:output ibge_dataset_overview_6 begin -->

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>code_tract_2000</th>
      <th>n</th>
      <th>over5pct</th>
      <th>minimum</th>
      <th>maximum</th>
      <th>total</th>
      <th>change_type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>310620005620001</td>
      <td>9</td>
      <td>3</td>
      <td>0.000772</td>
      <td>0.982006</td>
      <td>2.102869</td>
      <td>split</td>
    </tr>
    <tr>
      <th>1</th>
      <td>310620005620002</td>
      <td>6</td>
      <td>2</td>
      <td>0.002036</td>
      <td>0.989558</td>
      <td>1.986710</td>
      <td>split</td>
    </tr>
    <tr>
      <th>2</th>
      <td>310620005620003</td>
      <td>7</td>
      <td>1</td>
      <td>0.000574</td>
      <td>0.972726</td>
      <td>0.991485</td>
      <td>stable</td>
    </tr>
    <tr>
      <th>3</th>
      <td>310620005620004</td>
      <td>5</td>
      <td>1</td>
      <td>0.001712</td>
      <td>0.996126</td>
      <td>1.006446</td>
      <td>stable</td>
    </tr>
    <tr>
      <th>4</th>
      <td>310620005620005</td>
      <td>8</td>
      <td>1</td>
      <td>0.000012</td>
      <td>0.987514</td>
      <td>1.012916</td>
      <td>stable</td>
    </tr>
    <tr>
      <th>5</th>
      <td>310620005620006</td>
      <td>6</td>
      <td>1</td>
      <td>0.000536</td>
      <td>0.994452</td>
      <td>1.021422</td>
      <td>stable</td>
    </tr>
    <tr>
      <th>6</th>
      <td>310620005620007</td>
      <td>3</td>
      <td>1</td>
      <td>0.004771</td>
      <td>0.989718</td>
      <td>1.000275</td>
      <td>stable</td>
    </tr>
    <tr>
      <th>7</th>
      <td>310620005620008</td>
      <td>3</td>
      <td>1</td>
      <td>0.000280</td>
      <td>0.952945</td>
      <td>0.960805</td>
      <td>stable</td>
    </tr>
    <tr>
      <th>8</th>
      <td>310620005620009</td>
      <td>4</td>
      <td>2</td>
      <td>0.007272</td>
      <td>0.998497</td>
      <td>1.953615</td>
      <td>split</td>
    </tr>
    <tr>
      <th>9</th>
      <td>310620005620010</td>
      <td>8</td>
      <td>3</td>
      <td>0.000295</td>
      <td>1.000000</td>
      <td>3.000249</td>
      <td>split</td>
    </tr>
    <tr>
      <th>10</th>
      <td>310620005620011</td>
      <td>3</td>
      <td>1</td>
      <td>0.001462</td>
      <td>0.895966</td>
      <td>0.902668</td>
      <td>reshaped</td>
    </tr>
    <tr>
      <th>11</th>
      <td>310620005620012</td>
      <td>9</td>
      <td>2</td>
      <td>0.000420</td>
      <td>0.998548</td>
      <td>2.049922</td>
      <td>split</td>
    </tr>
    <tr>
      <th>12</th>
      <td>310620005620013</td>
      <td>7</td>
      <td>2</td>
      <td>0.000006</td>
      <td>0.994177</td>
      <td>1.991003</td>
      <td>split</td>
    </tr>
    <tr>
      <th>13</th>
      <td>310620005620014</td>
      <td>10</td>
      <td>2</td>
      <td>0.000055</td>
      <td>0.996930</td>
      <td>2.081956</td>
      <td>split</td>
    </tr>
    <tr>
      <th>14</th>
      <td>310620005620015</td>
      <td>4</td>
      <td>2</td>
      <td>0.006853</td>
      <td>0.966465</td>
      <td>1.922558</td>
      <td>split</td>
    </tr>
    <tr>
      <th>15</th>
      <td>310620005620016</td>
      <td>4</td>
      <td>1</td>
      <td>0.000002</td>
      <td>0.971315</td>
      <td>0.975798</td>
      <td>stable</td>
    </tr>
    <tr>
      <th>16</th>
      <td>310620005620017</td>
      <td>5</td>
      <td>1</td>
      <td>0.001820</td>
      <td>0.977440</td>
      <td>1.023820</td>
      <td>stable</td>
    </tr>
    <tr>
      <th>17</th>
      <td>310620005620018</td>
      <td>7</td>
      <td>2</td>
      <td>0.000013</td>
      <td>0.981346</td>
      <td>1.966211</td>
      <td>split</td>
    </tr>
    <tr>
      <th>18</th>
      <td>310620005620019</td>
      <td>6</td>
      <td>2</td>
      <td>0.000889</td>
      <td>0.993017</td>
      <td>1.984615</td>
      <td>split</td>
    </tr>
    <tr>
      <th>19</th>
      <td>310620005620020</td>
      <td>5</td>
      <td>1</td>
      <td>0.000009</td>
      <td>0.945593</td>
      <td>0.955127</td>
      <td>reshaped</td>
    </tr>
  </tbody>
</table>


```text
{'artifact_rows': 2564,
 'path': 'data/intermediate/overview/change_summary_2000_2010.parquet'}
```
<!-- brazil:output ibge_dataset_overview_6 end -->

### 2000 -\> 2022


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_7 -->
```python
#| label: ibge_dataset_overview_7
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 7)
```

</details>

<!-- brazil:output ibge_dataset_overview_7 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_7 end -->

### Visualization - Change Types

**Split**


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_8 -->
```python
#| label: ibge_dataset_overview_8
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 8)
```

</details>

<!-- brazil:output ibge_dataset_overview_8 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```

Local interactive map (outside Git): `outputs/maps/overview/310620025610001.html`
<!-- brazil:output ibge_dataset_overview_8 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_9 -->
```python
#| label: ibge_dataset_overview_9
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 9)
```

</details>

<!-- brazil:output ibge_dataset_overview_9 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```

Local interactive map (outside Git): `outputs/maps/overview/310620005650306.html`
<!-- brazil:output ibge_dataset_overview_9 end -->

**Reshaped**


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_10 -->
```python
#| label: ibge_dataset_overview_10
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 10)
```

</details>

<!-- brazil:output ibge_dataset_overview_10 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```

Local interactive map (outside Git): `outputs/maps/overview/310620005620021.html`
<!-- brazil:output ibge_dataset_overview_10 end -->

**Stable**


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_11 -->
```python
#| label: ibge_dataset_overview_11
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 11)
```

</details>

<!-- brazil:output ibge_dataset_overview_11 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```

Local interactive map (outside Git): `outputs/maps/overview/310620005620008.html`
<!-- brazil:output ibge_dataset_overview_11 end -->

# Census Data

## Visualization - BH

### Black population ratio


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_12 -->
```python
#| label: ibge_dataset_overview_12
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 12)
```

</details>

<!-- brazil:output ibge_dataset_overview_12 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_12 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_13 -->
```python
#| label: ibge_dataset_overview_13
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 13)
```

</details>

<!-- brazil:output ibge_dataset_overview_13 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_13 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_dataset_overview_14 -->
```python
#| label: ibge_dataset_overview_14
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 14)
```

</details>

<!-- brazil:output ibge_dataset_overview_14 begin -->
```text
{'municipality': '3106200',
 'adapter': 'R sf/S2',
 'classification_counts': {'2010': {'split': 1323,
   'stable': 1017,
   'reshaped': 222,
   'unmatched': 2},
  '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
 'reason': 'preserve original geographic intersection and area semantics',
 'generated_at': '2026-10-07T07:01:58.874116+00:00'}
```
<!-- brazil:output ibge_dataset_overview_14 end -->
