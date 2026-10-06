# IBGE Census - Census tract harmonisation

Rendered preview · [Editable Quarto source](ibge_census_tract_harmonisation.qmd) · Generated from saved local artifacts; full datasets stay outside Git.


This code links 2010 and 2022 census tracts based on their largest
spatial overlap in both directions, creating a correspondence table
(crosswalk). It identifies whether areas stayed the same, were split,
merged, or changed in a more complex way. The original tract pieces
remain unchanged as reference geometry. The active analytical layer
merges complete 2022 groups by `common_id`, and matching now excludes
line/point-only contacts. See the [approved
policy](../../docs/harmonisation-policy.md) for complete-group
selection, unmatched coverage, and the boundary-change assumption.

    {'version': '8f67986ba3b1f50731be40dc11a183fdda6b8caecd893ed0d9ea5f83ddec1650',
     'source_version': '84700cdc61d0b76baf8512431fc55a7f3e9a8044b682a6fc51987b53ea1a49bd',
     'policy': 'positive-area-common-geometry-v1',
     'mode': 'validated_original_correspondence',
     'scope': 'Brazil',
     'source_contract': {'policy': 'positive-area-common-geometry-v1',
      'mode': 'validated_original_correspondence',
      'inputs': {'tracts': '15ce7a4882dd3f8798223e3c1697fa3f32164793acac884da026c75b56549a3c',
       'baseline_lookup': '42d1354a5ed84047f4df28781aecd1970c0dd7e09c630c960c1a1139cb098c9b',
       'baseline_geometry': 'ae961e48f488a18ae94cb3ece85162bab4f039daa9b87b3c029ac9e579edae57',
       'baseline_group_sizes': '17175bc7b75c44465cceecd87184fcbc413daedb5aaabb01cbd8efdc4bf721a1'},
      'crs': 5880,
      'precision_grid': 1e-06},
     'population_coverage': {'2010': {'matched_tract_ids': 316558,
       'unmatched_tract_ids': 16,
       'measures': {'population': {'status': 'partial',
         'matched_known_total': 190755712.0,
         'unmatched_known_total': 87.0,
         'matched_missing_values': 6448,
         'unmatched_missing_values': 12,
         'unmatched_share_of_known_total': 4.560804990258776e-07},
        'households': {'status': 'partial',
         'matched_known_total': 58862521.0,
         'unmatched_known_total': 40.0,
         'matched_missing_values': 7264,
         'unmatched_missing_values': 12,
         'unmatched_share_of_known_total': 6.795490940327928e-07}}},
      '2022': {'matched_tract_ids': 468073,
       'unmatched_tract_ids': 24,
       'measures': {'population': {'status': 'complete',
         'matched_known_total': 203080475.0,
         'unmatched_known_total': 281.0,
         'matched_missing_values': 0,
         'unmatched_missing_values': 0,
         'unmatched_share_of_known_total': 1.3836860051870204e-06},
        'households': {'status': 'partial',
         'matched_known_total': 72438873.0,
         'unmatched_known_total': 80.0,
         'matched_missing_values': 17988,
         'unmatched_missing_values': 21,
         'unmatched_share_of_known_total': 1.1043781927659832e-06}}}},
     'assumption': 'Boundary differences are assumed not to materially change the inhabited population; not independently verified.',
     'generation': '4d8e6abf520341809668db82f8c56e71',
     'tracts_2022': 472778,
     'groups': 287178,
     'duplicate_base_ids': 4681,
     'common_geometry_features': 287178,
     'rejected_edges': 0,
     'unmatched': {'2010': 16, '2022': 24},
     'footprint_difference_above_10pct': 131222,
     'generated_at': '2026-10-05T12:41:49.113426+00:00'}

    {'version': '8f67986ba3b1f50731be40dc11a183fdda6b8caecd893ed0d9ea5f83ddec1650',
     'source_version': '84700cdc61d0b76baf8512431fc55a7f3e9a8044b682a6fc51987b53ea1a49bd',
     'policy': 'positive-area-common-geometry-v1',
     'mode': 'validated_original_correspondence',
     'scope': 'Brazil',
     'source_contract': {'policy': 'positive-area-common-geometry-v1',
      'mode': 'validated_original_correspondence',
      'inputs': {'tracts': '15ce7a4882dd3f8798223e3c1697fa3f32164793acac884da026c75b56549a3c',
       'baseline_lookup': '42d1354a5ed84047f4df28781aecd1970c0dd7e09c630c960c1a1139cb098c9b',
       'baseline_geometry': 'ae961e48f488a18ae94cb3ece85162bab4f039daa9b87b3c029ac9e579edae57',
       'baseline_group_sizes': '17175bc7b75c44465cceecd87184fcbc413daedb5aaabb01cbd8efdc4bf721a1'},
      'crs': 5880,
      'precision_grid': 1e-06},
     'population_coverage': {'2010': {'matched_tract_ids': 316558,
       'unmatched_tract_ids': 16,
       'measures': {'population': {'status': 'partial',
         'matched_known_total': 190755712.0,
         'unmatched_known_total': 87.0,
         'matched_missing_values': 6448,
         'unmatched_missing_values': 12,
         'unmatched_share_of_known_total': 4.560804990258776e-07},
        'households': {'status': 'partial',
         'matched_known_total': 58862521.0,
         'unmatched_known_total': 40.0,
         'matched_missing_values': 7264,
         'unmatched_missing_values': 12,
         'unmatched_share_of_known_total': 6.795490940327928e-07}}},
      '2022': {'matched_tract_ids': 468073,
       'unmatched_tract_ids': 24,
       'measures': {'population': {'status': 'complete',
         'matched_known_total': 203080475.0,
         'unmatched_known_total': 281.0,
         'matched_missing_values': 0,
         'unmatched_missing_values': 0,
         'unmatched_share_of_known_total': 1.3836860051870204e-06},
        'households': {'status': 'partial',
         'matched_known_total': 72438873.0,
         'unmatched_known_total': 80.0,
         'matched_missing_values': 17988,
         'unmatched_missing_values': 21,
         'unmatched_share_of_known_total': 1.1043781927659832e-06}}}},
     'assumption': 'Boundary differences are assumed not to materially change the inhabited population; not independently verified.',
     'generation': '4d8e6abf520341809668db82f8c56e71',
     'tracts_2022': 472778,
     'groups': 287178,
     'duplicate_base_ids': 4681,
     'common_geometry_features': 287178,
     'rejected_edges': 0,
     'unmatched': {'2010': 16, '2022': 24},
     'footprint_difference_above_10pct': 131222,
     'generated_at': '2026-10-05T12:41:49.113426+00:00'}

![Original census tract harmonization flow chart](assets/0838f6bd9fdf9632.png)

|  | common_id | n_2010 | n_2022 | relationship | area_km2 | footprint_difference_fraction | area_2010_km2 | area_2022_projected_km2 | harmonisation_version |
|----|----|----|----|----|----|----|----|----|----|
| 0 | 1 | 1 | 1 | 1:1 | 0.539979 | 0.071359 | 0.534356 | 0.545054 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 1 | 10 | 1 | 1 | 1:1 | 0.183445 | 0.157143 | 0.194150 | 0.185165 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 2 | 100 | 1 | 1 | 1:1 | 0.217012 | 0.137256 | 0.210305 | 0.219653 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 3 | 1000 | 1 | 1 | 1:1 | 0.067295 | 0.133822 | 0.066169 | 0.068263 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 4 | 10000 | 1 | 1 | 1:1 | 0.119492 | 0.023133 | 0.118183 | 0.120067 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 5 | 100000 | 2 | 3 | many_to_many | 91.040011 | 0.028448 | 93.046892 | 91.987685 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 6 | 100001 | 1 | 1 | 1:1 | 0.056755 | 0.373679 | 0.059133 | 0.057344 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 7 | 100002 | 1 | 1 | 1:1 | 0.090660 | 0.402873 | 0.094015 | 0.091602 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 8 | 100003 | 1 | 1 | 1:1 | 0.085019 | 0.418140 | 0.099104 | 0.085902 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 9 | 100004 | 1 | 1 | 1:1 | 0.105918 | 0.230998 | 0.107598 | 0.107016 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 10 | 100005 | 1 | 1 | 1:1 | 0.087685 | 0.299505 | 0.085229 | 0.088597 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 11 | 100006 | 1 | 1 | 1:1 | 0.079447 | 0.401304 | 0.078223 | 0.080273 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 12 | 100007 | 1 | 1 | 1:1 | 0.051121 | 0.469180 | 0.050756 | 0.051652 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 13 | 100008 | 1 | 1 | 1:1 | 0.448989 | 0.172298 | 0.488978 | 0.453659 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 14 | 100009 | 1 | 1 | 1:1 | 0.098064 | 0.338957 | 0.098907 | 0.099082 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 15 | 10001 | 1 | 1 | 1:1 | 0.071374 | 0.101103 | 0.076234 | 0.071717 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 16 | 100010 | 1 | 1 | 1:1 | 0.156026 | 0.250150 | 0.156728 | 0.157645 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 17 | 100011 | 1 | 1 | 1:1 | 0.045247 | 0.364494 | 0.046667 | 0.045716 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 18 | 100012 | 1 | 3 | 2010_to_2022_split | 2.000736 | 0.178445 | 1.830004 | 2.021359 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |
| 19 | 100013 | 1 | 1 | 1:1 | 0.165580 | 0.214994 | 0.167169 | 0.167286 | 8f67986ba3b1f50731be40dc11a183fdda6b8caecd893e... |

    {'artifact_rows': 287178,
     'path': 'data/intermediate/harmonisation/bundles/4d8e6abf520341809668db82f8c56e71/common_geometry_2022.parquet'}

Be aware that the base geometry layer has not been unioned by common ID.
2010 tracts that were split share a common ID but still follow the 2022
tract boundaries.
