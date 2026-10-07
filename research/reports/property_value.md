# Property value

Executable research report. Refresh with `brazil-project report property_value`. Code is collapsed below each explanation.


<details>
<summary>Python code</summary>

<!-- brazil:cell property_value_1 -->
```python
#| label: property_value_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 1)
```

</details>

<!-- brazil:output property_value_1 begin -->
```text
{'workbook_sheets': ['Annex I',
  'Annex II',
  'Annex III',
  'Annex IV',
  'Annex V'],
 'status': 'exploratory',
 'missing_exact_inputs': ['data/raw/land_value/Belo Horizonte/Data/20220601_regional_barreiro_cadastro_imobiliario.csv'],
 'generated_at': '2026-10-07T07:08:54.423137+00:00'}
```
<!-- brazil:output property_value_1 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell property_value_2 -->
```python
#| label: property_value_2
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 2)
```

</details>

<!-- brazil:output property_value_2 begin -->
```text
{'workbook_sheets': ['Annex I',
  'Annex II',
  'Annex III',
  'Annex IV',
  'Annex V'],
 'status': 'exploratory',
 'missing_exact_inputs': ['data/raw/land_value/Belo Horizonte/Data/20220601_regional_barreiro_cadastro_imobiliario.csv'],
 'generated_at': '2026-10-07T07:08:54.423137+00:00'}
```
<!-- brazil:output property_value_2 end -->


<details>
<summary>Python code</summary>

<!-- brazil:cell property_value_3 -->
```python
#| label: property_value_3
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 3)
```

</details>

<!-- brazil:output property_value_3 begin -->

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
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
      <th>0</th>
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
      <th>1</th>
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
      <th>2</th>
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
      <th>3</th>
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
      <th>4</th>
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
      <th>5</th>
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
      <th>6</th>
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
      <th>7</th>
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
      <th>8</th>
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
      <th>9</th>
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
    <tr>
      <th>10</th>
      <td>BA110</td>
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
      <th>11</th>
      <td>BA110</td>
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
      <th>12</th>
      <td>BA111</td>
      <td>ZP1</td>
      <td>99</td>
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
      <th>13</th>
      <td>BA112</td>
      <td>ZAP</td>
      <td>81</td>
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
      <th>14</th>
      <td>BA112</td>
      <td>ZEIS1</td>
      <td>54</td>
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
      <th>15</th>
      <td>BA113</td>
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
      <th>16</th>
      <td>BA114</td>
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
      <th>17</th>
      <td>BA114</td>
      <td>ZEIS1</td>
      <td>54</td>
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
      <th>18</th>
      <td>BA114</td>
      <td>ZEIS2</td>
      <td>90</td>
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
      <th>19</th>
      <td>BA114</td>
      <td>ZP1</td>
      <td>63</td>
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


```text
{'artifact_rows': 1524, 'path': 'data/intermediate/land-value/annex_i.parquet'}
```
<!-- brazil:output property_value_3 end -->
