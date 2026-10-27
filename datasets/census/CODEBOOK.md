# Census comparison areas — codebook

Status: current  
Last updated: 2026-10-27  
Version: 1.1

Scope: `census_comparison_areas_2010_2022.gpkg`, the national 2010–2022 census handoff

The `comparison_areas` layer contains 287,178 merged comparison areas, one per text `common_id`, in EPSG:5880. A common ID joins 2010 and 2022 tracts through their largest positive-area overlaps; it is an identifier, not a geographic rank. Text sorting places `1`, `10`, `100` before `2`. `tracts_2010` and `tracts_2022` count member tracts. `tract_relationship` is `1:1`, `2010_to_2022_split`, `2010_to_2022_merge`, or `many_to_many`. Geometry is the merged **2022** group footprint, not an intersection or a fixed-area reconstruction of both years. `fid` is only the GeoPackage row ID; `geom` holds the geometry.

| Fields in `comparison_areas` | Read them as |
| --- | --- |
| `black`, `brown`, `black_brown` | Black, Brown, and combined Black-or-Brown resident counts and shares. `*_population_<year>` is a count; `*_share_<year>` is a fraction, so 0.25 means 25%. |
| `literacy` | `literate_15plus_<year>` divided by `population_15plus_<year>`; residents aged at least 15. |
| `rudimentary_sanitation`, `water_network`, `waste_collection`, `sewer_septic`, `houses`, `village_condo`, `apartments` | Counts and fractions of **households**. `village_condo` means houses in villages/condominiums, not a verified gated-community measure. |
| `*_households_<year>`, `households_<year>`, `households_for_*_<year>` | Indicator numerator and its applicable household denominator. Denominators can differ because the input validity and missingness rules differ. |
| `*_population_<year>`, `population_for_race_2022`, `total_population_<year>` | Resident counts and applicable denominators. In particular, do not substitute `total_population_2022` for `population_for_race_2022`: their missingness differs. |
| `*_change_pp` | 2022 share minus 2010 share, **in percentage points**: 10% to 15% is +5. Missing when a required year is unavailable. |
| `population_density_<year>`, `area_km2_<year>` | People per km² and the saved area denominator. Area is measured using equal-area EPSG:6933; the delivered geometry remains EPSG:5880. `population_density_change_pct` is relative percentage change from a positive 2010 density. |
| `income_mean_brl_<year>` | Household-head-weighted mean income in July 2022 BRL. The 2010 mean uses the configured inflation adjustment; the two censuses retain their year-specific income definitions. `income_change_brl` is 2022 minus adjusted 2010; `income_change_pct` is relative percentage change. |
| `income_heads_used_*`, `income_tracts_used_*`, `income_tracts_missing_weights_*`, `income_inputs_complete_*` | Income coverage diagnostics. A saved mean can exist even when some tract inputs are missing; inspect the completeness flag. |

For shares, the numerator and denominator are summed within a complete common area before division. A denominator must be positive; `NULL` is unavailable, not zero. `rudimentary_sanitation` is the specified narrow source-code combination, not every form of inadequate sanitation. Some component-count rules differ between indicators, so an available value does not by itself prove all inputs were observed. The exact original-to-English mapping, **unit and definition for every exported field** are in the nonspatial `field_dictionary` table (`original_column`, `english_column`, `unit`, `description`).

The `overview` layer has 5,570 municipality **display summaries**, identified by `municipality_code`; its simplified boundaries are not the `comparison_areas` analysis geometry. Complete comparison groups crossing a municipality boundary can appear in multiple display summaries, so do not sum these rows as independent national areas. It uses the same indicator names where applicable. `export_metadata` records the export contract and input fingerprints. For the source codes, matching and calculations, see the [runnable notebook](build.ipynb) and its [processing code](processing.py).
