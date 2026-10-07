# Census indicators: 2010–2022 comparison

Compare demographic, household-service, housing, income and density indicators on connected common areas. Each spatial output contains one merged 2022 feature per common_id.

[Variable and dataset codebook](../../docs/codebook.md) · [Methods](../../docs/methods.md) · [All reports](../README.md#read-the-reports)

Refresh processing and this report with `brazil-project report ibge_census_temporal_comparison --config project.toml`. Add `--from-saved` to refresh existing verified artifacts only. Code is collapsed; tables and figures below are saved execution results.

## How to read this analysis

Counts are aggregated before ratios are calculated. Annual tables are outer joined: an absent year stays unavailable, never zero. Most count sums skip missing entries; specified combined components are coalesced to zero. Housing denominators and population-density totals stay missing if every contributing value is missing. Proportion calculations require positive denominators. Incomplete counts can bias ratios even when an estimate is available.

Annual ratio columns are fractions (0.10 = 10%). Percentage-point change is 100 × (2022 ratio − 2010 ratio); a change from 10% to 15% is +5 pp. It is not a 5% relative increase. Income and density use their own units and change rules. See the [variable codebook](../../docs/codebook.md) for every numerator, denominator, source code and exception.

## Inputs, coverage and processing status

Coverage is counted from final saved change columns. The original income missingness counter was recorded before those columns existed and is retained only in collapsed legacy metadata; it does not describe final income coverage. Technical fingerprints remain in run evidence.

<details>
<summary>Read saved processing summary</summary>

<!-- brazil:cell ibge_census_temporal_comparison_1 -->
```python
import matplotlib
matplotlib.use("Agg")  # Headless figures in the fresh report process.
import json
import pandas as pd
from brazil_project.reporting import show_chunk, table, markdown
processing_record = report_json("indicators")
coverage_rows = []
for name, metadata in processing_record.items():
    if not isinstance(metadata, dict) or "common_areas" not in metadata:
        continue
    change_column = ("income_change_brl" if name == "income" else
                     "population_density_change" if name == "population_density" else
                     name + "_ratio_change_pp")
    changes = pd.read_parquet(ctx.require(ctx.artifact("indicators", name + ".parquet")), columns=[change_column])
    if len(changes) != metadata["common_areas"]:
        raise RuntimeError("Coverage differs from processing record: " + name)
    coverage_rows.append({"Indicator": name.replace("_", " ").title(),
                          "Common areas": len(changes),
                          "Unavailable change": int(changes[change_column].isna().sum())})
table(pd.DataFrame(coverage_rows), "Availability is calculated from the final saved change columns, including income and density.")
markdown("<details>\n<summary>Original processing metadata (legacy income missingness counter is not final coverage)</summary>\n\n```json\n" + json.dumps(processing_record, indent=2) + "\n```\n\n</details>")
ctx._report_presented = {("indicators", "report")}
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_1 begin -->
Availability is calculated from the final saved change columns, including income and density.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Indicator</th>
      <th>Common areas</th>
      <th>Unavailable change</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Black</td>
      <td>287178</td>
      <td>3505</td>
    </tr>
    <tr>
      <td>Brown</td>
      <td>287178</td>
      <td>3505</td>
    </tr>
    <tr>
      <td>Black Brown</td>
      <td>287178</td>
      <td>3505</td>
    </tr>
    <tr>
      <td>Literacy</td>
      <td>285714</td>
      <td>5738</td>
    </tr>
    <tr>
      <td>Rudimentary Sanitation</td>
      <td>285714</td>
      <td>3821</td>
    </tr>
    <tr>
      <td>Water Network</td>
      <td>285714</td>
      <td>3821</td>
    </tr>
    <tr>
      <td>Waste Collection</td>
      <td>285714</td>
      <td>3821</td>
    </tr>
    <tr>
      <td>Sewer Septic</td>
      <td>285714</td>
      <td>3821</td>
    </tr>
    <tr>
      <td>Houses</td>
      <td>287178</td>
      <td>5285</td>
    </tr>
    <tr>
      <td>Village Condo</td>
      <td>287178</td>
      <td>5285</td>
    </tr>
    <tr>
      <td>Apartments</td>
      <td>287178</td>
      <td>5285</td>
    </tr>
    <tr>
      <td>Income</td>
      <td>287178</td>
      <td>7216</td>
    </tr>
    <tr>
      <td>Population Density</td>
      <td>287178</td>
      <td>2785</td>
    </tr>
  </tbody>
</table>

<details>
<summary>Original processing metadata (legacy income missingness counter is not final coverage)</summary>

```json
{
  "harmonisation_version": "8f67986ba3b1f50731be40dc11a183fdda6b8caecd893ed0d9ea5f83ddec1650",
  "spatial_unit": "common_id",
  "black": {
    "common_areas": 287178,
    "missing_change": 3505
  },
  "brown": {
    "common_areas": 287178,
    "missing_change": 3505
  },
  "black_brown": {
    "common_areas": 287178,
    "missing_change": 3505
  },
  "literacy": {
    "common_areas": 285714,
    "missing_change": 5738
  },
  "rudimentary_sanitation": {
    "common_areas": 285714,
    "missing_change": 3821
  },
  "water_network": {
    "common_areas": 285714,
    "missing_change": 3821
  },
  "waste_collection": {
    "common_areas": 285714,
    "missing_change": 3821
  },
  "sewer_septic": {
    "common_areas": 285714,
    "missing_change": 3821
  },
  "houses": {
    "common_areas": 287178,
    "missing_change": 5285
  },
  "village_condo": {
    "common_areas": 287178,
    "missing_change": 5285
  },
  "apartments": {
    "common_areas": 287178,
    "missing_change": 5285
  },
  "income": {
    "common_areas": 287178,
    "missing_change": 0
  },
  "population_density": {
    "common_areas": 287178
  },
  "generated_at": "2026-10-07T08:17:10.795067+00:00"
}
```

</details>
<!-- brazil:output ibge_census_temporal_comparison_1 end -->

<details>
<summary>Trace original step: Data Import</summary>

<!-- brazil:cell ibge_census_temporal_comparison_2 -->
```python
#| label: ibge_census_temporal_comparison_2
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 2)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_2 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output ibge_census_temporal_comparison_2 end -->

<details>
<summary>Trace original step: Check Join Keys</summary>

<!-- brazil:cell ibge_census_temporal_comparison_3 -->
```python
#| label: ibge_census_temporal_comparison_3
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 3)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_3 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output ibge_census_temporal_comparison_3 end -->

## Black population share

Black count / total population, aggregated within each common area.

<details>
<summary>Read black population share</summary>

<!-- brazil:cell ibge_census_temporal_comparison_4 -->
```python
#| label: ibge_census_temporal_comparison_4
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 4)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_4 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>284393</td>
      <td>2785</td>
      <td>5.1447</td>
      <td>2.3006</td>
      <td>9.6000</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>284994</td>
      <td>2184</td>
      <td>7.8616</td>
      <td>4.1499</td>
      <td>12.9543</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>black_ratio_2010</th>
      <th>black_ratio_2022</th>
      <th>black_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.0664</td>
      <td>0.0938</td>
      <td>2.7394</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.0448</td>
      <td>0.0675</td>
      <td>2.2718</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.0700</td>
      <td>0.0915</td>
      <td>2.1494</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.1344</td>
      <td>0.0922</td>
      <td>-4.2162</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.0568</td>
      <td>0.1140</td>
      <td>5.7184</td>
    </tr>
  </tbody>
</table>

![Generated figure](assets/87fd225de925ddcca7439994bb37001ba17f46f2c1715def7842af5000559eb3.png)

Median and middle 50% of available common-area estimates; whiskers follow 1.5×IQR. Outliers are hidden in the figure and retained in the data. Annual availability can differ; this is descriptive, not a paired causal comparison.
<!-- brazil:output ibge_census_temporal_comparison_4 end -->

## Literacy among people aged 15+

Literate population aged 15+ / population aged 15+. The 2022 Pessoas table supplies its own denominator independently of the Basico join.

<details>
<summary>Read literacy among people aged 15+</summary>

<!-- brazil:cell ibge_census_temporal_comparison_5 -->
```python
#| label: ibge_census_temporal_comparison_5
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 5)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_5 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>281219</td>
      <td>4495</td>
      <td>93.8272</td>
      <td>85.7143</td>
      <td>97.3790</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>283112</td>
      <td>2602</td>
      <td>95.4496</td>
      <td>89.4751</td>
      <td>98.0603</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>literacy_ratio_2010</th>
      <th>literacy_ratio_2022</th>
      <th>literacy_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.9088</td>
      <td>0.9123</td>
      <td>0.3519</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.9600</td>
      <td>0.9729</td>
      <td>1.2868</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.9142</td>
      <td>0.9558</td>
      <td>4.1586</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.9502</td>
      <td>0.9655</td>
      <td>1.5345</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.9816</td>
      <td>0.9817</td>
      <td>0.0084</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_5 end -->

## Rudimentary sanitation

Selected rudimentary pit, ditch and water-body disposal counts / the original household denominator. This excludes the additional no-bathroom categories used in conference charts.

<details>
<summary>Read rudimentary sanitation</summary>

<!-- brazil:cell ibge_census_temporal_comparison_6 -->
```python
#| label: ibge_census_temporal_comparison_6
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 6)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_6 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>283550</td>
      <td>2164</td>
      <td>5.0633</td>
      <td>0.0000</td>
      <td>65.8254</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>283274</td>
      <td>2440</td>
      <td>1.8315</td>
      <td>0.0000</td>
      <td>50.0000</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>rudimentary_sanitation_ratio_2010</th>
      <th>rudimentary_sanitation_ratio_2022</th>
      <th>rudimentary_sanitation_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.9886</td>
      <td>0.9792</td>
      <td>-0.9470</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.9881</td>
      <td>0.0000</td>
      <td>-98.8095</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.0599</td>
      <td>0.0128</td>
      <td>-4.7108</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.9108</td>
      <td>0.8657</td>
      <td>-4.5057</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.5709</td>
      <td>0.0760</td>
      <td>-49.4836</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_6 end -->

## Water-network access

Water-network household counts / the original household denominator.

<details>
<summary>Read water-network access</summary>

<!-- brazil:cell ibge_census_temporal_comparison_7 -->
```python
#| label: ibge_census_temporal_comparison_7
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 7)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_7 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>283550</td>
      <td>2164</td>
      <td>97.1429</td>
      <td>27.4194</td>
      <td>100.0000</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>283274</td>
      <td>2440</td>
      <td>98.3051</td>
      <td>70.4142</td>
      <td>100.0000</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>water_network_ratio_2010</th>
      <th>water_network_ratio_2022</th>
      <th>water_network_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.2576</td>
      <td>0.2054</td>
      <td>-5.2219</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.6131</td>
      <td>0.9024</td>
      <td>28.9344</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.4036</td>
      <td>0.5064</td>
      <td>10.2748</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.7559</td>
      <td>0.8565</td>
      <td>10.0613</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.9004</td>
      <td>0.7681</td>
      <td>-13.2322</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_7 end -->

## Waste collection

Selected collection categories / the original household denominator. The combined 2022 components retain the original missing-component rule.

<details>
<summary>Read waste collection</summary>

<!-- brazil:cell ibge_census_temporal_comparison_8 -->
```python
#| label: ibge_census_temporal_comparison_8
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 8)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_8 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>283550</td>
      <td>2164</td>
      <td>99.5614</td>
      <td>48.7179</td>
      <td>100.0000</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>283274</td>
      <td>2440</td>
      <td>99.6575</td>
      <td>95.3642</td>
      <td>100.0000</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>waste_collection_ratio_2010</th>
      <th>waste_collection_ratio_2022</th>
      <th>waste_collection_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.9697</td>
      <td>0.9911</td>
      <td>2.1374</td>
    </tr>
    <tr>
      <td>10</td>
      <td>1.0000</td>
      <td>1.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.9948</td>
      <td>1.0000</td>
      <td>0.5208</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>1.0000</td>
      <td>1.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>1.0000</td>
      <td>0.9962</td>
      <td>-0.3802</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_8 end -->

## Sewer or septic disposal

Selected sewer/septic disposal categories / the original household denominator. Categories follow the year-specific codes in the codebook.

<details>
<summary>Read sewer or septic disposal</summary>

<!-- brazil:cell ibge_census_temporal_comparison_9 -->
```python
#| label: ibge_census_temporal_comparison_9
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 9)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_9 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>283550</td>
      <td>2164</td>
      <td>78.4431</td>
      <td>2.8571</td>
      <td>99.5455</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>283274</td>
      <td>2440</td>
      <td>96.5636</td>
      <td>43.8849</td>
      <td>99.7135</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>sewer_septic_ratio_2010</th>
      <th>sewer_septic_ratio_2022</th>
      <th>sewer_septic_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.0038</td>
      <td>0.0179</td>
      <td>1.4069</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.0119</td>
      <td>0.9919</td>
      <td>97.9965</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.9349</td>
      <td>0.9872</td>
      <td>5.2316</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.0892</td>
      <td>0.1343</td>
      <td>4.5057</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.4291</td>
      <td>0.9240</td>
      <td>49.4836</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_9 end -->

## Brown population share

Brown count / total population. This retains the census category as supplied.

<details>
<summary>Read brown population share</summary>

<!-- brazil:cell ibge_census_temporal_comparison_10 -->
```python
#| label: ibge_census_temporal_comparison_10
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 10)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_10 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>284393</td>
      <td>2785</td>
      <td>42.8835</td>
      <td>20.9369</td>
      <td>58.4507</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>284994</td>
      <td>2184</td>
      <td>45.6022</td>
      <td>26.8477</td>
      <td>58.9233</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>brown_ratio_2010</th>
      <th>brown_ratio_2022</th>
      <th>brown_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.4703</td>
      <td>0.5539</td>
      <td>8.3565</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.4807</td>
      <td>0.5338</td>
      <td>5.3110</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.5266</td>
      <td>0.5491</td>
      <td>2.2420</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.5783</td>
      <td>0.6559</td>
      <td>7.7631</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.7005</td>
      <td>0.6425</td>
      <td>-5.8029</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_10 end -->

## Combined Black/Brown population share

Sum of Black and Brown counts / total population; missing component counts are coalesced to zero.

<details>
<summary>Read combined black/brown population share</summary>

<!-- brazil:cell ibge_census_temporal_comparison_11 -->
```python
#| label: ibge_census_temporal_comparison_11
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 11)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_11 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>284393</td>
      <td>2785</td>
      <td>51.4423</td>
      <td>25.7895</td>
      <td>68.6838</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>284994</td>
      <td>2184</td>
      <td>57.0926</td>
      <td>33.1933</td>
      <td>72.7407</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>black_brown_ratio_2010</th>
      <th>black_brown_ratio_2022</th>
      <th>black_brown_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.5367</td>
      <td>0.6476</td>
      <td>11.0959</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.5255</td>
      <td>0.6013</td>
      <td>7.5828</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.5967</td>
      <td>0.6406</td>
      <td>4.3915</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.7127</td>
      <td>0.7482</td>
      <td>3.5469</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.7574</td>
      <td>0.7565</td>
      <td>-0.0845</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_11 end -->

## Income in July 2022 reais

2010 tract mean = total income / positive recipients. Group means are weighted by household heads using only valid mean/weight pairs; incomplete coverage is reported but does not automatically block a mean. This corrects the former report’s stronger prose restriction to describe the existing implementation. The pipeline’s configured inflation factor converts 2010 nominal income to July 2022 reais. Absolute change is BRL; relative change requires positive 2010 income.

<details>
<summary>Read income in july 2022 reais</summary>

<!-- brazil:cell ibge_census_temporal_comparison_12 -->
```python
#| label: ibge_census_temporal_comparison_12
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 12)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_12 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>July 2022 BRL</td>
      <td>280906</td>
      <td>6272</td>
      <td>2,081.9171</td>
      <td>1,452.9446</td>
      <td>3,085.3132</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>July 2022 BRL</td>
      <td>283192</td>
      <td>3986</td>
      <td>2,181.2355</td>
      <td>1,545.6730</td>
      <td>3,138.0611</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>income_2010</th>
      <th>income_2022</th>
      <th>income_change_brl</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>2,169.0461</td>
      <td>2,453.0300</td>
      <td>283.9839</td>
    </tr>
    <tr>
      <td>10</td>
      <td>2,857.0370</td>
      <td>5,100.0700</td>
      <td>2,243.0330</td>
    </tr>
    <tr>
      <td>100</td>
      <td>2,289.7947</td>
      <td>2,464.9300</td>
      <td>175.1353</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>1,705.3463</td>
      <td>2,066.3300</td>
      <td>360.9837</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>2,407.1117</td>
      <td>2,337.0800</td>
      <td>-70.0317</td>
    </tr>
  </tbody>
</table>

![Generated figure](assets/8b9bd8d62bbdbdce20ec7bbbafb58f2cd9e39fdf3817476004bc9e3fac2f5c2f.png)

Median and middle 50% of available common-area estimates; whiskers follow 1.5×IQR. Outliers are hidden in the figure and retained in the data. Annual availability can differ; this is descriptive, not a paired causal comparison.
<!-- brazil:output ibge_census_temporal_comparison_12 end -->

## House dwelling share

House counts / the original household denominator. All-missing group denominators remain unavailable.

<details>
<summary>Read house dwelling share</summary>

<!-- brazil:cell ibge_census_temporal_comparison_13 -->
```python
#| label: ibge_census_temporal_comparison_13
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 13)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_13 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>283550</td>
      <td>3628</td>
      <td>99.2063</td>
      <td>85.0467</td>
      <td>100.0000</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>283274</td>
      <td>3904</td>
      <td>98.5714</td>
      <td>86.9110</td>
      <td>100.0000</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>houses_ratio_2010</th>
      <th>houses_ratio_2022</th>
      <th>houses_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>1.0000</td>
      <td>0.9970</td>
      <td>-0.2976</td>
    </tr>
    <tr>
      <td>10</td>
      <td>1.0000</td>
      <td>0.9837</td>
      <td>-1.6260</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.9323</td>
      <td>0.9258</td>
      <td>-0.6460</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.9718</td>
      <td>0.9907</td>
      <td>1.8910</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.9962</td>
      <td>0.9848</td>
      <td>-1.1378</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_13 end -->

## Village/condominium house share

Village or condominium house counts / the original household denominator. This is a dwelling type, not a neighbourhood classification.

<details>
<summary>Read village/condominium house share</summary>

<!-- brazil:cell ibge_census_temporal_comparison_14 -->
```python
#| label: ibge_census_temporal_comparison_14
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 14)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_14 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>283550</td>
      <td>3628</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.4115</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>283274</td>
      <td>3904</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.0000</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>village_condo_ratio_2010</th>
      <th>village_condo_ratio_2022</th>
      <th>village_condo_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.0026</td>
      <td>0.0358</td>
      <td>3.3201</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.0038</td>
      <td>0.0000</td>
      <td>-0.3831</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_14 end -->

## Apartment share

Apartment counts / the original household denominator. All-missing group denominators remain unavailable.

<details>
<summary>Read apartment share</summary>

<!-- brazil:cell ibge_census_temporal_comparison_15 -->
```python
#| label: ibge_census_temporal_comparison_15
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 15)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_15 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>%</td>
      <td>283550</td>
      <td>3628</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>6.3559</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>%</td>
      <td>283274</td>
      <td>3904</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>7.2626</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>apartments_ratio_2010</th>
      <th>apartments_ratio_2022</th>
      <th>apartments_ratio_change_pp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>100</td>
      <td>0.0651</td>
      <td>0.0384</td>
      <td>-2.6741</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>0.0282</td>
      <td>0.0000</td>
      <td>-2.8169</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>0.0000</td>
      <td>0.0114</td>
      <td>1.1407</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output ibge_census_temporal_comparison_15 end -->

## Population density

Population / saved common-area km². Area is computed from merged geometry in equal-area EPSG:6933. Absolute change is people/km²; percentage change requires positive 2010 density. The archived stored absolute-change column differs from current source code; see the verification record.

<details>
<summary>Read population density</summary>

<!-- brazil:cell ibge_census_temporal_comparison_16 -->
```python
#| label: ibge_census_temporal_comparison_16
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 16)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_16 begin -->
Unweighted distribution across common areas. These are not national population-weighted estimates.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Year</th>
      <th>Unit</th>
      <th>Available areas</th>
      <th>Unavailable areas</th>
      <th>Median across areas</th>
      <th>25th percentile</th>
      <th>75th percentile</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2010</td>
      <td>people/km²</td>
      <td>284393</td>
      <td>2785</td>
      <td>3,868.5947</td>
      <td>378.3721</td>
      <td>10,116.5252</td>
    </tr>
    <tr>
      <td>2022</td>
      <td>people/km²</td>
      <td>287178</td>
      <td>0</td>
      <td>3,747.5155</td>
      <td>408.3483</td>
      <td>9,242.8121</td>
    </tr>
  </tbody>
</table>

First five saved common areas (a data preview, not a representative sample). Annual ratios in this preview are fractions; change is percentage points for proportion indicators.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>common_id</th>
      <th>population_density_2010</th>
      <th>population_density_2022</th>
      <th>population_density_change</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>1,590.8013</td>
      <td>1,718.5839</td>
      <td>127.7826</td>
    </tr>
    <tr>
      <td>10</td>
      <td>2,676.5464</td>
      <td>1,695.3278</td>
      <td>-981.2187</td>
    </tr>
    <tr>
      <td>100</td>
      <td>6,054.9662</td>
      <td>4,884.5237</td>
      <td>-1,170.4425</td>
    </tr>
    <tr>
      <td>1000</td>
      <td>12,051.4383</td>
      <td>10,149.3617</td>
      <td>-1,902.0766</td>
    </tr>
    <tr>
      <td>10000</td>
      <td>7,657.3950</td>
      <td>7,046.4772</td>
      <td>-610.9179</td>
    </tr>
  </tbody>
</table>

![Generated figure](assets/7c9149518b581a1f0abec5fcf81206b221a0e4838cff23d83b6107ed7976883f.png)

Median and middle 50% of available common-area estimates; whiskers follow 1.5×IQR. Outliers are hidden in the figure and retained in the data. Annual availability can differ; this is descriptive, not a paired causal comparison.
<!-- brazil:output ibge_census_temporal_comparison_16 end -->

<details>
<summary>Trace original step: Save</summary>

<!-- brazil:cell ibge_census_temporal_comparison_17 -->
```python
#| label: ibge_census_temporal_comparison_17
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd', 17)
```

</details>

<!-- brazil:output ibge_census_temporal_comparison_17 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output ibge_census_temporal_comparison_17 end -->

## Interpretation and limits

Outputs retain the original aggregation, missingness and exclusion rules. Available results do not establish national scientific validation. Read [verification and remaining limitations](../../docs/checks.md) before drawing research conclusions. Original codebooks and earlier report contents remain preserved in the project archive.
