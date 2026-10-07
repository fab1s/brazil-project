# IBGE Census - Data Extraction

Executable research report. Refresh with `brazil-project report ibge_census_data_extraction`. Code is collapsed below each explanation.


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_census_data_extraction_1 -->
```python
#| label: ibge_census_data_extraction_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 1)
```

</details>

<!-- brazil:output ibge_census_data_extraction_1 begin -->
```text
{'scope': ['Belo Horizonte',
  'Vespasiano',
  'São José da Lapa',
  'Confins',
  'Lagoa Santa',
  'Santa Luzia'],
 'annual': {'2010': {'map_tracts': 4380,
   'BH_summary': {'count': 3838.0,
    'mean': 0.0999245419310908,
    'std': 0.06755773466431246,
    'min': 0.0,
    '25%': 0.046556999343482515,
    '50%': 0.0932932161745721,
    '75%': 0.14093186567338092,
    'max': 0.52}},
  '2022': {'map_tracts': 6255,
   'BH_summary': {'count': 5025.0,
    'mean': 0.13449590373929912,
    'std': 0.08271013953960317,
    'min': 0.0,
    '25%': 0.068,
    '50%': 0.13030746705710103,
    '75%': 0.18814814814814815,
    'max': 0.8695652173913043}}},
 'metro_overlay': 'missing original Linha Verde shapefile; not substituted',
 'generated_at': '2026-10-07T07:02:02.555956+00:00'}
```
<!-- brazil:output ibge_census_data_extraction_1 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_census_data_extraction_2 -->
```python
#| label: ibge_census_data_extraction_2
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 2)
```

</details>

<!-- brazil:output ibge_census_data_extraction_2 begin -->
```text
{'scope': ['Belo Horizonte',
  'Vespasiano',
  'São José da Lapa',
  'Confins',
  'Lagoa Santa',
  'Santa Luzia'],
 'annual': {'2010': {'map_tracts': 4380,
   'BH_summary': {'count': 3838.0,
    'mean': 0.0999245419310908,
    'std': 0.06755773466431246,
    'min': 0.0,
    '25%': 0.046556999343482515,
    '50%': 0.0932932161745721,
    '75%': 0.14093186567338092,
    'max': 0.52}},
  '2022': {'map_tracts': 6255,
   'BH_summary': {'count': 5025.0,
    'mean': 0.13449590373929912,
    'std': 0.08271013953960317,
    'min': 0.0,
    '25%': 0.068,
    '50%': 0.13030746705710103,
    '75%': 0.18814814814814815,
    'max': 0.8695652173913043}}},
 'metro_overlay': 'missing original Linha Verde shapefile; not substituted',
 'generated_at': '2026-10-07T07:02:02.555956+00:00'}
```
<!-- brazil:output ibge_census_data_extraction_2 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_census_data_extraction_3 -->
```python
#| label: ibge_census_data_extraction_3
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 3)
```

</details>

<!-- brazil:output ibge_census_data_extraction_3 begin -->
```text
{'scope': ['Belo Horizonte',
  'Vespasiano',
  'São José da Lapa',
  'Confins',
  'Lagoa Santa',
  'Santa Luzia'],
 'annual': {'2010': {'map_tracts': 4380,
   'BH_summary': {'count': 3838.0,
    'mean': 0.0999245419310908,
    'std': 0.06755773466431246,
    'min': 0.0,
    '25%': 0.046556999343482515,
    '50%': 0.0932932161745721,
    '75%': 0.14093186567338092,
    'max': 0.52}},
  '2022': {'map_tracts': 6255,
   'BH_summary': {'count': 5025.0,
    'mean': 0.13449590373929912,
    'std': 0.08271013953960317,
    'min': 0.0,
    '25%': 0.068,
    '50%': 0.13030746705710103,
    '75%': 0.18814814814814815,
    'max': 0.8695652173913043}}},
 'metro_overlay': 'missing original Linha Verde shapefile; not substituted',
 'generated_at': '2026-10-07T07:02:02.555956+00:00'}
```
<!-- brazil:output ibge_census_data_extraction_3 end -->

### Black population ratio


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_census_data_extraction_4 -->
```python
#| label: ibge_census_data_extraction_4
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 4)
```

</details>

<!-- brazil:output ibge_census_data_extraction_4 begin -->
```text
{'scope': ['Belo Horizonte',
  'Vespasiano',
  'São José da Lapa',
  'Confins',
  'Lagoa Santa',
  'Santa Luzia'],
 'annual': {'2010': {'map_tracts': 4380,
   'BH_summary': {'count': 3838.0,
    'mean': 0.0999245419310908,
    'std': 0.06755773466431246,
    'min': 0.0,
    '25%': 0.046556999343482515,
    '50%': 0.0932932161745721,
    '75%': 0.14093186567338092,
    'max': 0.52}},
  '2022': {'map_tracts': 6255,
   'BH_summary': {'count': 5025.0,
    'mean': 0.13449590373929912,
    'std': 0.08271013953960317,
    'min': 0.0,
    '25%': 0.068,
    '50%': 0.13030746705710103,
    '75%': 0.18814814814814815,
    'max': 0.8695652173913043}}},
 'metro_overlay': 'missing original Linha Verde shapefile; not substituted',
 'generated_at': '2026-10-07T07:02:02.555956+00:00'}
```
<!-- brazil:output ibge_census_data_extraction_4 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_census_data_extraction_5 -->
```python
#| label: ibge_census_data_extraction_5
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 5)
```

</details>

<!-- brazil:output ibge_census_data_extraction_5 begin -->
```text
{'scope': ['Belo Horizonte',
  'Vespasiano',
  'São José da Lapa',
  'Confins',
  'Lagoa Santa',
  'Santa Luzia'],
 'annual': {'2010': {'map_tracts': 4380,
   'BH_summary': {'count': 3838.0,
    'mean': 0.0999245419310908,
    'std': 0.06755773466431246,
    'min': 0.0,
    '25%': 0.046556999343482515,
    '50%': 0.0932932161745721,
    '75%': 0.14093186567338092,
    'max': 0.52}},
  '2022': {'map_tracts': 6255,
   'BH_summary': {'count': 5025.0,
    'mean': 0.13449590373929912,
    'std': 0.08271013953960317,
    'min': 0.0,
    '25%': 0.068,
    '50%': 0.13030746705710103,
    '75%': 0.18814814814814815,
    'max': 0.8695652173913043}}},
 'metro_overlay': 'missing original Linha Verde shapefile; not substituted',
 'generated_at': '2026-10-07T07:02:02.555956+00:00'}
```
<!-- brazil:output ibge_census_data_extraction_5 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell ibge_census_data_extraction_6 -->
```python
#| label: ibge_census_data_extraction_6
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 6)
```

</details>

<!-- brazil:output ibge_census_data_extraction_6 begin -->
```text
{'scope': ['Belo Horizonte',
  'Vespasiano',
  'São José da Lapa',
  'Confins',
  'Lagoa Santa',
  'Santa Luzia'],
 'annual': {'2010': {'map_tracts': 4380,
   'BH_summary': {'count': 3838.0,
    'mean': 0.0999245419310908,
    'std': 0.06755773466431246,
    'min': 0.0,
    '25%': 0.046556999343482515,
    '50%': 0.0932932161745721,
    '75%': 0.14093186567338092,
    'max': 0.52}},
  '2022': {'map_tracts': 6255,
   'BH_summary': {'count': 5025.0,
    'mean': 0.13449590373929912,
    'std': 0.08271013953960317,
    'min': 0.0,
    '25%': 0.068,
    '50%': 0.13030746705710103,
    '75%': 0.18814814814814815,
    'max': 0.8695652173913043}}},
 'metro_overlay': 'missing original Linha Verde shapefile; not substituted',
 'generated_at': '2026-10-07T07:02:02.555956+00:00'}
```

Local interactive map (outside Git): `outputs/maps/black_ratio_2010_2022.html`
<!-- brazil:output ibge_census_data_extraction_6 end -->
