# IBAMA licensed projects — codebook

Status: current  
Last updated: 2026-10-27  
Version: 1.0  
Scope: `ibama_licensed_projects.gpkg`, the preserved licensing-record handoff

The `licensed_projects_st` layer contains 8,494 spatial **source records** in EPSG:4674. A record represents an IBAMA licensing entry or its mapped element, not proof that a project is operating or that an environmental impact occurred. `record_id` is the unique source object ID; names and case numbers may recur. `fid` is the GeoPackage row ID, and `geom` is the preserved point, line or polygon geometry.

| Field(s) | Meaning |
| --- | --- |
| `element_type_original`, `element_type_english` | Source geometry-element category and its reviewed English translation (for example, road segment or port area). |
| `sector_original`, `sector_english` | Source sector and English label. |
| `project_type_original`, `project_type_english` | Source licensing typology and English label. |
| `licenses_original`, `licenses_english` | Source licence-history string and a copy with **licence-type labels** translated. Licence numbers and dates are retained as supplied; an empty string means no licence text in this field, not a verified absence of permits. |
| `project_name_original`, `developer_name_original` | Supplied project and developer names. Proper names remain in their original wording. |
| `sei_case_number`, `sei_project_name_original` | Supplied SEI case reference and combined case/name text. Treat the reference as an identifier. |
| `issued_licenses_url` | Provider link supplied with the record, not an independently checked current licence status. |

`_original` columns keep provider text. The English companions cover **categories and licence labels only**; project names are not translated. Missing values remain missing. The nonspatial `field_dictionary` maps the 11 original provider columns to these export columns; `export_metadata` records source and translation fingerprints. For acquisition context and exact export checks, see the [runnable notebook](build.ipynb) and [processing.py](processing.py). The geometry and every original value were verified against the preserved source.
