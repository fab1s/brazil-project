# Obrasgov infrastructure locations

Status: current
Last updated: 2026-10-26
Version: 0.1
Scope: Approved national point/line map derivative

Read and run [build.ipynb](build.ipynb). Its [processing.py](processing.py) runs the same `brazil-project run obrasgov` pipeline as the research reports: snapshot translation, geometry-component QA, screening figure, complete-geometry primary-state check, and approved exclusion. No automatic acquisition or website publication occurs.

Inputs are the configured preserved Obrasgov snapshot and pinned IBGE/Natural Earth references. `final.gpkg` is a checked copy of `outputs/maps/obrasgov-primary-state-filter/locations.gpkg`. Its `map_components` layer holds retained points/lines; `excluded_primary_state` records the 2,346 entirely outside components. Original records, coordinates, investment totals and excluded geometry are preserved.

The [location policy](../../docs/obrasgov-location-policy.md) and [exclusion audit](../../docs/obrasgov-primary-state-filter.md) explain thresholds and why exclusions were made. Map eligibility is not proof of geocoding accuracy. The notebook's saved chart counts geometry components, not projects or money.
