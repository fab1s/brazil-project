# Obrasgov Preprocessing

Rendered preview · [Editable Quarto source](obrasgov_preprocessing.qmd) · Generated from saved local artifacts; full datasets stay outside Git.


This report follows the original import, translation and cleaning flow
using saved Python processing artifacts. Rendering does not download or
modify source datasets. The later location QA and approved primary-state
exclusions are documented separately below.

## Processing flow

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

|  | type_en | subtype_en | projects | share |
|----|----|----|----|----|
| 0 | Water Infrastructure, Ports, and Waterways | Dredging, Rock Removal, and Related Works | 25250 | 0.187413 |
| 1 | Education | Education | 14896 | 0.110563 |
| 2 | Urban Infrastructure and Mobility | Urban Development | 10957 | 0.081326 |
| 3 | Health | Basic Health Unit (UBS) | 9297 | 0.069005 |
| 4 | Urban Infrastructure and Mobility | Paving | 8407 | 0.062399 |
| 5 | Civil Defense | Response and Reconstruction | 5822 | 0.043213 |
| 6 | Development | Tourism | 5171 | 0.038381 |
| 7 | Administrative | Public-Building Works | 3534 | 0.026230 |
| 8 | Highways | Paving | 2978 | 0.022104 |
| 9 | Highways | Rural Roads | 2781 | 0.020641 |
| 10 | Development | Rural Roads | 2554 | 0.018957 |
| 11 | Sports | Urban Development | 2483 | 0.018430 |
| 12 | Education | Federal Higher-Education Institutions | 2374 | 0.017621 |
| 13 | Water Infrastructure, Ports, and Waterways | Water Supply | 2198 | 0.016314 |
| 14 | Social Assistance | Social Housing | 1956 | 0.014518 |

    {'artifact_rows': 15,
     'path': 'data/intermediate/obrasgov/type_subtype_counts.parquet'}

|  | type_en | subtype_en | projects | share |
|----|----|----|----|----|
| 0 | Water Infrastructure, Ports, and Waterways | Dredging, Rock Removal, and Related Works | 25250 | 0.187413 |
| 1 | Education | Education | 14896 | 0.110563 |
| 2 | Urban Infrastructure and Mobility | Urban Development | 10957 | 0.081326 |
| 3 | Health | Basic Health Unit (UBS) | 9297 | 0.069005 |
| 4 | Urban Infrastructure and Mobility | Paving | 8407 | 0.062399 |
| 5 | Civil Defense | Response and Reconstruction | 5822 | 0.043213 |
| 6 | Development | Tourism | 5171 | 0.038381 |
| 7 | Administrative | Public-Building Works | 3534 | 0.026230 |
| 8 | Highways | Paving | 2978 | 0.022104 |
| 9 | Highways | Rural Roads | 2781 | 0.020641 |
| 10 | Development | Rural Roads | 2554 | 0.018957 |
| 11 | Sports | Urban Development | 2483 | 0.018430 |
| 12 | Education | Federal Higher-Education Institutions | 2374 | 0.017621 |
| 13 | Water Infrastructure, Ports, and Waterways | Water Supply | 2198 | 0.016314 |
| 14 | Social Assistance | Social Housing | 1956 | 0.014518 |

    {'artifact_rows': 15,
     'path': 'data/intermediate/obrasgov/type_subtype_counts.parquet'}

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

## Location preprocessing and primary-state exclusions

The faithful snapshot translation above is separate from the later
spatial quality checks. Original records remain preserved. The approved
state filter excludes components entirely outside their reported primary
state, keeps partial/boundary intersections under the baseline policy,
and saves a complete exclusion audit. See the [processing and
verification record](../../docs/obrasgov-primary-state-filter.md).

|     | Result                                 | Count  |
|-----|----------------------------------------|--------|
| 0   | Components excluded by primary state   | 2346   |
| 1   | Map components before state exclusions | 226309 |
| 2   | Map components after state exclusions  | 224495 |

![Original eligible Obrasgov points before and after approved
primary-state
exclusions](assets/0ac43a2ef9a91c20.png)

Point-only illustration; lines, polygons and already quarantined
locations are omitted. Source coordinates are unchanged.
