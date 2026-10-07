# Conference charts: sanitation, racial composition and income

Compare inadequate sanitation across urban common areas. The first chart uses areas with eligible observations in both years; the income chart uses its own eligible 2022 population. These figures describe associations, not causal effects.

[Variable and dataset codebook](../../docs/codebook.md) · [Methods](../../docs/methods.md) · [All reports](../README.md#read-the-reports)

Refresh processing and this report with `brazil-project report brazil_poroject_charts --config project.toml`. Add `--from-saved` to refresh existing verified artifacts only. Code is collapsed; tables and figures below are saved execution results.

## How to read this analysis

The change chart sums eligible household counts within quintiles, giving household-weighted percentages. Q1 has the lowest and Q5 the highest 2022 Black/Brown share. Ties are ordered by common_id. The income figure shows the distribution of area-level sanitation percentages within income bands, rather than household-weighted averages.

Unlike the temporal rudimentary-sanitation indicator, these charts include households without a bathroom or toilet. A tract with any missing or invalid required component is excluded from both numerator and denominator. All contributing 2022 tracts must be urban. Income tertile cutoffs use all eligible urban 2022 areas before selecting Q1 and Q5; intervals are right closed. Hidden boxplot outliers remain in the source tables.

## Sanitation by racial composition and income

The table reports summed eligible household counts and percentages for the paired comparison population. Each generated figure retains its own population and exclusions.

<details>
<summary>Display conference tables and figures</summary>

<!-- brazil:cell brazil_poroject_charts_1 -->
```python
import matplotlib
matplotlib.use("Agg")  # Headless figures in the fresh report process.
#| label: brazil_poroject_charts_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
show_chunk(ctx, 'CS2Nordic/Brazil Poroject - Charts.qmd', 1)
```

</details>

<!-- brazil:output brazil_poroject_charts_1 begin -->
10 saved rows; showing up to ten. See the codebook for column definitions.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>year</th>
      <th>racial_quintile</th>
      <th>households</th>
      <th>inadequate_sanitation</th>
      <th>percentage</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>1</td>
      <td>7,481,178.0000</td>
      <td>249,492.0000</td>
      <td>3.3349</td>
    </tr>
    <tr>
      <td>2010</td>
      <td>2</td>
      <td>7,749,718.0000</td>
      <td>594,814.0000</td>
      <td>7.6753</td>
    </tr>
    <tr>
      <td>2010</td>
      <td>3</td>
      <td>7,701,575.0000</td>
      <td>1,180,648.0000</td>
      <td>15.3300</td>
    </tr>
    <tr>
      <td>2010</td>
      <td>4</td>
      <td>7,772,029.0000</td>
      <td>2,270,568.0000</td>
      <td>29.2146</td>
    </tr>
    <tr>
      <td>2010</td>
      <td>5</td>
      <td>7,962,930.0000</td>
      <td>3,414,868.0000</td>
      <td>42.8846</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>1</td>
      <td>8,031,367.0000</td>
      <td>263,168.0000</td>
      <td>3.2768</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>2</td>
      <td>8,556,830.0000</td>
      <td>385,678.0000</td>
      <td>4.5073</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>3</td>
      <td>8,442,688.0000</td>
      <td>668,547.0000</td>
      <td>7.9187</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>4</td>
      <td>8,453,915.0000</td>
      <td>1,458,583.0000</td>
      <td>17.2533</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>5</td>
      <td>8,479,892.0000</td>
      <td>2,422,264.0000</td>
      <td>28.5648</td>
    </tr>
  </tbody>
</table>

![Generated figure](assets/86b21d600174eb976d7e638e6318c13bfd97384eca6ac35d64f248e8611456d4.png)

Current conference output: `urban_inadequate_sanitation_2010_2022.png`. See the explanation above for populations, quintiles and exclusions.

![Generated figure](assets/ec96fc0e481e0128e031ce099fd4df76c47739f060533f3cb8cb716a6b6f5671.png)

Current conference output: `urban_inadequate_sanitation_income_boxplots_2022.png`. See the explanation above for populations, quintiles and exclusions.
<!-- brazil:output brazil_poroject_charts_1 end -->

## Interpretation and limits

Outputs retain the original aggregation, missingness and exclusion rules. Available results do not establish national scientific validation. Read [verification and remaining limitations](../../docs/checks.md) before drawing research conclusions. Original codebooks and earlier report contents remain preserved in the project archive.
