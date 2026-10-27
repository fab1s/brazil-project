# Obrasgov screened locations — codebook

Status: current  
Last updated: 2026-10-27  
Version: 1.0  
Scope: `final.gpkg`, the national map-location handoff

**Start with `map_components`.** It has 224,495 retained components (200,643 points and 23,852 lines) in EPSG:4674. One provider row can produce several components, and several rows can share a project ID. Count distinct `project_id` for projects; **do not sum investment over components**. `component_id` uniquely identifies a decomposed part; `source_row` is its original row position. `fid` is a GeoPackage row ID, and `geom` is the unchanged location geometry. The separate `excluded_primary_state` layer holds all 2,346 components entirely outside their reported primary state, including some that were already absent from the earlier eligible map. Source records were not deleted.

### Location screening fields

These fields were added by the pipeline; `TRUE` means a condition was flagged, not necessarily that the location was corrected. Most severe flags are `FALSE` in `map_components` because that layer is already screened.

| Field(s) | Meaning |
| --- | --- |
| `declared_state`, `declared_municipality`, `marine_signal`, `geometry_type` | Reported state/municipality, whether the project text suggests a marine activity, and the decomposed shape type. The municipality field is empty in this saved source; an administrative zero below does **not** establish a municipality match. |
| `missing_geometry`, `empty_geometry`, `invalid_geometry` | No geometry, an empty geometry, or a geometry that fails the shape-validity check. |
| `nonfinite_coordinates`, `out_of_range`, `equal_axes` | Any coordinate is nonfinite; outside world longitude/latitude limits; or has nearly equal longitude and latitude. `equal_axes` prompts review but does not automatically exclude a component. |
| `polygon_excluded`, `outside_screening_extent` | Polygon omitted from this map; or a point/line falls outside the screening window (80°W–25°W, 40°S–10°N), cannot be sampled, or has an unsupported shape. The window is **not** a Brazil boundary. |
| `sampling_capped`, `sample_count` | A line needed over 250 regularly spaced test points; original vertices are still tested. `sample_count` is the number of tested points, usually one for a point, not a project count. |
| `outside_brazil_samples`, `offshore_samples`, `far_offshore_samples`, `foreign_land_samples` | Counts of tested points outside mapped IBGE municipalities, offshore, more than 5 km from both mapped coast and territory while offshore, or on foreign land more than 1 km from Brazil. Reference coverage and coastline detail limit these tests. |
| `uf_mismatch_samples`, `municipality_mismatch_samples` | Tested points intersecting mapped administrative units that omit the reported code. Zero can mean there was no usable reported code or no mapped intersection. |
| `coast_distance_max_m`, `country_distance_max_m`, `intersected_municipalities` | Largest measured point-to-coast/territory distance in metres and `|`-separated intersected municipality codes. Distances are screening diagnostics, not access distances. |
| `location_status`, `reasons`, `map_eligible` | Initial screening class, `|`-separated flags, and eligibility **before** the primary-state rule. Eligible means usable for this derivative, not independently verified geocoding. |
| `primary_state_check`, `intersected_states` | Complete-geometry relation to the reported state (`fully_inside`, `partly_inside_or_boundary_contact`, `entirely_outside`, `not_assessable_geometry`, or `unknown_or_missing_primary_state`); mapped states are `|`-separated. |
| `primary_state_excluded`, `exclusion_reason`, `final_map_eligible` | Approved exclusion of `entirely_outside` components and final eligibility after both screens. Boundary/partial intersections remain subject to initial eligibility. |

### Provider fields and translations

All provider **field names** are English. `_original` retains the exact Portuguese source text; `_english` is a reviewed translation for controlled categories only.

| Original / English pair | Meaning; provider code if present |
| --- | --- |
| `strategic_project_original` / `strategic_project_english` | Whether reported as a strategic project. |
| `intervention_nature_original` / `intervention_nature_english` | Broad intervention nature; `intervention_nature_id` is its provider code. |
| `intervention_kind_original` / `intervention_kind_english` | Construction, renovation and other intervention kinds; `intervention_kind_id` is its code. |
| `project_status_original` / `project_status_english` | Reported project status, not independently checked completion. |
| `has_feasibility_study_original` / `has_feasibility_study_english` | Reported yes/no study indicator. |
| `policy_axis_original` / `policy_axis_english` | Reported policy axis; `policy_axis_id` is its code. |
| `project_type_original` / `project_type_english` | Broad sector/type; `project_type_id` is its code. |
| `project_subtype_original` / `project_subtype_english` | More specific type; `project_subtype_id` is its code. |

The `*_id` fields are provider codes, not translation keys to aggregate without checking the category text.

| Fields | Meaning |
| --- | --- |
| `investment_project_id`, `primary_state`, `postal_code`, `responsible_organisation_cnpj` | Provider identifiers and reported geography. `project_id` is a string copy of the source investment-project ID used in component QA. Preserve identifiers as identifiers. |
| `project_name_original`, `address_original`, `project_description_original`, `social_purpose_original`, `overall_goal_original`, `beneficiary_description_original`, `intervention_notes_original`, `responsible_organisation_original` | Original names or free-form Portuguese text. They were **not** machine translated; place and organisation names keep their original spelling. |
| `planned_start_date`, `planned_end_date`, `actual_start_date`, `actual_end_date`, `registration_date`, `registration_year` | Provider dates/year. Planned and actual dates describe different events; no new date correction is implied. |
| `planned_total_investment_brl`, `beneficiary_population`, `jobs_created` | Reported planned Brazilian-real amount, beneficiary count, and jobs count. These are source-row values repeated on components, not measured benefits or realised spending. |
| `bim_indicator`, `responsible_system` | Original BIM indicator and source-system label; neither is a location-quality assessment. |

The nonspatial `field_dictionary` maps provider field names to export names and any translated companion; `export_metadata` records source and code fingerprints. The [runnable notebook](build.ipynb) explains screening and the approved exclusion, with figures; [processing.py](processing.py) links the stage code. The retained coordinates were not inferred, corrected or reprojected.
