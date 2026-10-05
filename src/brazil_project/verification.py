"""Numerical comparisons against original stored results, without rewriting them."""
import numpy as np
import pandas as pd
import geopandas as gpd
from brazil_project.io import identifiers
from brazil_project.harmonisation.census import scope_where

BASELINES={'black':'black_change_sf','brown':'brown_sf','black_brown':'black_brown_sf','literacy':'literacy_change_sf',
 'rudimentary_sanitation':'rudimentary_sanitation_change_sf','water_network':'water_network_change_sf',
 'waste_collection':'waste_collection_change_sf','sewer_septic':'sewer_septic_change_sf','income':'income_change_sf',
 'houses':'houses_change_sf','village_condo':'village_condo_change_sf','apartments':'apartments_change_sf',
 'population_density':'population_density_change_sf'}

def compare_tables(actual,expected,key,rtol=1e-9,atol=1e-8):
    actual=actual.copy();expected=expected.copy()
    actual[key]=identifiers(actual[key]);expected[key]=identifiers(expected[key])
    # Duplicate base geometry rows are preserved by production; compare each unique attribute record.
    actual=actual.drop_duplicates();expected=expected.drop_duplicates()
    if actual[key].duplicated().any() or expected[key].duplicated().any():
        return {'passed':False,'error':'Conflicting values for duplicated comparison keys'}
    a=actual.set_index(key);b=expected.set_index(key)
    shared=a.index.intersection(b.index)
    columns=[c for c in a.columns.intersection(b.columns) if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])]
    failures={}
    for column in columns:
        av=a.loc[shared,column].to_numpy(dtype=float,na_value=np.nan)
        bv=b.loc[shared,column].to_numpy(dtype=float,na_value=np.nan)
        mismatch=~np.isclose(av,bv,rtol=rtol,atol=atol,equal_nan=True)
        if mismatch.any():
            delta=np.abs(av-bv);finite=delta[np.isfinite(delta)]
            failures[column]={'mismatches':int(mismatch.sum()),'maximum_absolute_difference':float(finite.max()) if len(finite) else None}
    missing_actual=len(b.index.difference(a.index));missing_expected=len(a.index.difference(b.index))
    return {'passed':not failures and missing_actual==0 and missing_expected==0 and bool(columns),
            'compared_rows':len(shared),'compared_columns':len(columns),'missing_actual':missing_actual,'missing_expected':missing_expected,'differences':failures,'rtol':rtol,'atol':atol}


def verify(ctx):
    results={}
    for name,filename in BASELINES.items():
        actual=ctx.table('indicators',name+'_sf').drop(columns='geometry')
        expected=gpd.read_file(ctx.root/'data/processed/ibge/Data'/(filename+'.gpkg'),ignore_geometry=True,where=scope_where(ctx,'id_2022'))
        for frame in (actual,expected):
            for column in ['id_2022','common_id']:
                if column in frame: frame[column]=identifiers(frame[column])
        columns=['id_2022']+[c for c in actual if c in expected and pd.api.types.is_numeric_dtype(actual[c]) and pd.api.types.is_numeric_dtype(expected[c])]
        results[name]=compare_tables(actual[columns],expected[columns],'id_2022',rtol=1e-8 if name=='population_density' else 1e-9,atol=1e-7 if name=='population_density' else 1e-8)
    return ctx.report('verification',{'passed':all(r['passed'] for r in results.values()),'reference':'original stored GeoPackage results','scope':ctx.municipality or 'Brazil','indicators':results})
