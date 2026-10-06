"""Verify saved location derivatives against original rows and the run contract."""
import json
from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint


def verify(ctx):
    if not __debug__:
        raise WorkflowError('Verification cannot run with optimized Python (-O): assertion checks would be disabled.')
    stage='obrasgov-location-qa'
    report=json.loads(ctx.require(ctx.artifact(stage,'report.json')).read_text())
    assert report['status']=='completed'
    source=ctx.path('location_qa','source')
    assert fingerprint(source)==report['contract']['source_sha256']
    for name,digest in report['output_fingerprints'].items():
        assert fingerprint(ctx.artifact(stage,name+'.parquet'))==digest,name
    original=gpd.read_parquet(source) if source.suffix=='.parquet' else gpd.read_file(source)
    saved=ctx.geo(stage,'source_audit')
    assert len(saved)==len(original)==report['source_records']
    pd.testing.assert_frame_equal(pd.DataFrame(saved[original.columns.drop('geometry')]),pd.DataFrame(original.drop(columns='geometry')))
    assert np.array_equal(shapely.to_wkb(saved.geometry.array),shapely.to_wkb(original.geometry.array))
    components=ctx.geo(stage,'component_audit');clean=ctx.geo(stage,'map_components');quarantine=ctx.geo(stage,'quarantined_components')
    assert components.component_id.is_unique
    assert set(components.source_row)==set(saved.source_row)
    assert set(clean.component_id)==set(components.loc[components.map_eligible,'component_id'])
    assert set(quarantine.component_id)==set(components.loc[components.location_status.str.startswith('quarantined_'),'component_id'])
    assert not set(clean.component_id)&set(quarantine.component_id)
    assert len(clean)+len(quarantine)+int(components.polygon_excluded.sum())==len(components)
    indexed=components.set_index('component_id')
    for frame in (clean,quarantine):
        assert np.array_equal(shapely.to_wkb(frame.geometry.array),shapely.to_wkb(indexed.loc[frame.component_id].geometry.array))
        for column in original.columns.drop('geometry'):
            pd.testing.assert_series_equal(frame[column].reset_index(drop=True),saved.iloc[frame.source_row][column].reset_index(drop=True),check_names=False)
    assert clean.geom_type.isin(['Point','LineString']).all()
    coverage=report['investment_by_source_row_coverage']
    assert sum(v['source_rows'] for v in coverage.values())==len(original)
    assert sum(v['missing_investment_rows'] for v in coverage.values())==int(pd.to_numeric(original.vl_investimento_previsto_total,errors='coerce').isna().sum())
    total=float(pd.to_numeric(original.vl_investimento_previsto_total,errors='coerce').sum())
    assert np.isclose(sum(v['known_investment_brl'] or 0 for v in coverage.values()),total,rtol=1e-12)
    layers=gpd.list_layers(ctx.root/'outputs/maps/obrasgov-location-qa/locations.gpkg').name.tolist()
    assert 'map_components' in layers
    exchange=gpd.read_file(ctx.root/'outputs/maps/obrasgov-location-qa/locations.gpkg',layer='map_components')
    assert len(exchange)==len(clean) and set(exchange.component_id)==set(clean.component_id)
    assert exchange.crs.to_epsg()==4674
    clean_index=clean.set_index('component_id')
    assert np.array_equal(shapely.to_wkb(exchange.geometry.array),shapely.to_wkb(clean_index.loc[exchange.component_id].geometry.array))
    if len(quarantine):
        held=gpd.read_file(ctx.root/'outputs/maps/obrasgov-location-qa/locations.gpkg',layer='quarantined_components')
        assert len(held)==len(quarantine) and set(held.component_id)==set(quarantine.component_id)
    return {'passed':True,'source_rows_and_attributes_exact':True,'original_geometry_wkb_exact':True,'map_and_quarantine_geometry_wkb_exact':True,
            'component_partition_complete':True,'gpkg_map_geometry_wkb_exact':True,'gpkg_quarantine_membership_exact':True,'project_investment_coverage_preserved':True,'investment_total_brl':total,
            'investment_relative_tolerance':1e-12,'gpkg_layers':layers,'source_records':len(saved),'map_components':len(clean),'quarantined_components':len(quarantine)}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',default='config/project.toml');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=verify(Context(a.config));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
