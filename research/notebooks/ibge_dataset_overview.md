# IBGE Dataset Overview

Rendered preview · [Editable Quarto source](ibge_dataset_overview.qmd) · Generated from saved local artifacts; full datasets stay outside Git.


This code compares census tract boundaries from 2000, 2010, and 2022 in
Belo Horizonte. It measures how much the areas overlap and classifies
older tracts as stable, reshaped, split, or unmatched. It then
visualizes examples of these changes and compares the share of the Black
population in 2010 and 2022.

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

# Census Tract

## Overlap Analysis

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

### 2000 -\> 2010

|     | code_tract_2000 | n   | over5pct | minimum  | maximum  | total    | change_type |
|-----|-----------------|-----|----------|----------|----------|----------|-------------|
| 0   | 310620005620001 | 9   | 3        | 0.000772 | 0.982006 | 2.102869 | split       |
| 1   | 310620005620002 | 6   | 2        | 0.002036 | 0.989558 | 1.986710 | split       |
| 2   | 310620005620003 | 7   | 1        | 0.000574 | 0.972726 | 0.991485 | stable      |
| 3   | 310620005620004 | 5   | 1        | 0.001712 | 0.996126 | 1.006446 | stable      |
| 4   | 310620005620005 | 8   | 1        | 0.000012 | 0.987514 | 1.012916 | stable      |
| 5   | 310620005620006 | 6   | 1        | 0.000536 | 0.994452 | 1.021422 | stable      |
| 6   | 310620005620007 | 3   | 1        | 0.004771 | 0.989718 | 1.000275 | stable      |
| 7   | 310620005620008 | 3   | 1        | 0.000280 | 0.952945 | 0.960805 | stable      |
| 8   | 310620005620009 | 4   | 2        | 0.007272 | 0.998497 | 1.953615 | split       |
| 9   | 310620005620010 | 8   | 3        | 0.000295 | 1.000000 | 3.000249 | split       |
| 10  | 310620005620011 | 3   | 1        | 0.001462 | 0.895966 | 0.902668 | reshaped    |
| 11  | 310620005620012 | 9   | 2        | 0.000420 | 0.998548 | 2.049922 | split       |
| 12  | 310620005620013 | 7   | 2        | 0.000006 | 0.994177 | 1.991003 | split       |
| 13  | 310620005620014 | 10  | 2        | 0.000055 | 0.996930 | 2.081956 | split       |
| 14  | 310620005620015 | 4   | 2        | 0.006853 | 0.966465 | 1.922558 | split       |
| 15  | 310620005620016 | 4   | 1        | 0.000002 | 0.971315 | 0.975798 | stable      |
| 16  | 310620005620017 | 5   | 1        | 0.001820 | 0.977440 | 1.023820 | stable      |
| 17  | 310620005620018 | 7   | 2        | 0.000013 | 0.981346 | 1.966211 | split       |
| 18  | 310620005620019 | 6   | 2        | 0.000889 | 0.993017 | 1.984615 | split       |
| 19  | 310620005620020 | 5   | 1        | 0.000009 | 0.945593 | 0.955127 | reshaped    |

    {'artifact_rows': 2564,
     'path': 'data/intermediate/overview/change_summary_2000_2010.parquet'}

### 2000 -\> 2022

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

### Visualization - Change Types

**Split**

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

**Reshaped**

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

**Stable**

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

# Census Data

## Visualization - BH

### Black population ratio

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}

    {'municipality': '3106200',
     'adapter': 'R sf/S2',
     'classification_counts': {'2010': {'split': 1323,
       'stable': 1017,
       'reshaped': 222,
       'unmatched': 2},
      '2022': {'split': 1897, 'stable': 491, 'reshaped': 164, 'unmatched': 11}},
     'reason': 'preserve original geographic intersection and area semantics',
     'generated_at': '2026-10-05T10:21:37.157635+00:00'}
