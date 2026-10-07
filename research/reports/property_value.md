# Exploratory land-value inputs

Inspect the available valuation annex workbook and zone input. The cadastral analysis is blocked by an exact dated input that is absent. No completed land-value estimate is claimed.

[Variable and dataset codebook](../../docs/codebook.md) · [Methods](../../docs/methods.md) · [All reports](../README.md#read-the-reports)

Refresh processing and this report with `brazil-project report property_value --config project.toml`. Add `--from-saved` to refresh existing verified artifacts only. Code is collapsed; tables and figures below are saved execution results.

## How to read this analysis

The original valuation workbook was parsed using AI and has not been independently authenticated against the legal reference. Annex tables retain their source headings and values. The required `20220601_regional_barreiro_cadastro_imobiliario.csv` is unavailable; another dated file is not substituted. Saved-output refresh can show the available exploratory imports, while a processing command reports the missing input as a failure.

## Inputs, coverage and processing status

This summary reads the current saved processing artifacts. Technical fingerprints are available in the collapsed provenance record.

<details>
<summary>Read saved processing summary</summary>

<!-- brazil:cell property_value_1 -->
```python
import matplotlib
matplotlib.use("Agg")  # Headless figures in the fresh report process.
#| label: property_value_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 1)
```

</details>

<!-- brazil:output property_value_1 begin -->
**Exploratory; cadastral processing incomplete.** Imported workbook sheets: Annex I, Annex II, Annex III, Annex IV, Annex V.

Required input unavailable: `data/raw/land_value/Belo Horizonte/Data/20220601_regional_barreiro_cadastro_imobiliario.csv`. No alternative date is substituted.

<details>
<summary>Technical provenance and complete processing record</summary>

```json
{
  "workbook_sheets": [
    "Annex I",
    "Annex II",
    "Annex III",
    "Annex IV",
    "Annex V"
  ],
  "status": "exploratory",
  "missing_exact_inputs": [
    "data/raw/land_value/Belo Horizonte/Data/20220601_regional_barreiro_cadastro_imobiliario.csv"
  ],
  "generated_at": "2026-10-07T08:21:26.511841+00:00"
}
```

</details>
<!-- brazil:output property_value_1 end -->

<details>
<summary>Trace original step: Unnamed 2</summary>

<!-- brazil:cell property_value_2 -->
```python
#| label: property_value_2
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 2)
```

</details>

<!-- brazil:output property_value_2 begin -->
<!-- Saved result already presented; original cell retained for traceability. -->
<!-- brazil:output property_value_2 end -->

## Imported valuation annex

This preview is a source table, not an estimate of observed market prices. See the original workbook for the full definitions and legal context.

<details>
<summary>Read exploratory Annex I</summary>

<!-- brazil:cell property_value_3 -->
```python
#| label: property_value_3
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 3)
```

</details>

<!-- brazil:output property_value_3 begin -->
1,524 saved rows; showing up to ten. See the codebook for column definitions.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>zona_homogenea</th>
      <th>zona_uso</th>
      <th>valor_m2_terreno</th>
      <th>ap</th>
      <th>ba</th>
      <th>ca</th>
      <th>lj</th>
      <th>vr</th>
      <th>gp</th>
      <th>sl</th>
      <th>vc</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>BA101</td>
      <td>ZAP</td>
      <td>108</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ1</td>
      <td>VR1</td>
      <td>GP1</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA101</td>
      <td>ZP1</td>
      <td>108</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ1</td>
      <td>VR1</td>
      <td>GP1</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA102</td>
      <td>ZAP</td>
      <td>108</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ1</td>
      <td>VR1</td>
      <td>GP1</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA103</td>
      <td>ZAP</td>
      <td>108</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ1</td>
      <td>VR1</td>
      <td>GP1</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA104</td>
      <td>ZAP</td>
      <td>324</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ2</td>
      <td>VR1</td>
      <td>GP2</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA105</td>
      <td>ZAP</td>
      <td>198</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ1</td>
      <td>VR1</td>
      <td>GP1</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA106</td>
      <td>ZAP</td>
      <td>108</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ1</td>
      <td>VR1</td>
      <td>GP1</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA107</td>
      <td>ZAP</td>
      <td>324</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ2</td>
      <td>VR1</td>
      <td>GP2</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA108</td>
      <td>ZAP</td>
      <td>108</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ1</td>
      <td>VR1</td>
      <td>GP1</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
    <tr>
      <td>BA109</td>
      <td>ZAP</td>
      <td>108</td>
      <td>AP1</td>
      <td>BA1</td>
      <td>CA1</td>
      <td>LJ1</td>
      <td>VR1</td>
      <td>GP1</td>
      <td>SL1</td>
      <td>VC1</td>
    </tr>
  </tbody>
</table>
<!-- brazil:output property_value_3 end -->

## Interpretation and limits

Outputs retain the original aggregation, missingness and exclusion rules. Available results do not establish national scientific validation. Read [verification and remaining limitations](../../docs/checks.md) before drawing research conclusions. Original codebooks and earlier report contents remain preserved in the project archive.
