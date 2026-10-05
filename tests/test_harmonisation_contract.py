"""Regression checks for complete geometry, contact rejection and mode switching."""
import json
from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from brazil_project.harmonisation.census import (correspondence, grouped_crosswalk, load_bundle,
    publish_bundle, run, source_correspondence, input_version)
from brazil_project.io import Context, WorkflowError
from brazil_project.indicators.temporal import run as indicators_run


def fixture_context(tmp_path, municipality='1111111'):
    cfg=tmp_path/'config.toml'
    cfg.write_text('''[project]
root="."
municipality="'''+municipality+'''"
[census]
tracts="tracts.gpkg"
baseline_lookup="lookup.gpkg"
baseline_geometry="base.gpkg"
baseline_group_sizes="sizes.csv"
tables="tables"
release="v0.5.0"
crs=5880
precision_grid=0.000001
recompute_harmonisation=false
''')
    ids10=['111111100000001','111111100000002']
    ids22=['111111100000001','222222200000001','111111100000002','111111100000003']
    old=gpd.GeoDataFrame({'code_tract':ids10},geometry=[box(0,0,2,1),box(10,0,11,1)],crs=5880)
    new=gpd.GeoDataFrame({'code_tract':ids22},geometry=[box(0,0,1,1),box(1,0,2,1),box(2,0,3,1),box(20,0,21,1)],crs=5880)
    # Use valid Brazilian projected coordinates for density/projection checks.
    from shapely.affinity import translate
    old.geometry = old.geometry.map(lambda geom: translate(geom, xoff=4300000, yoff=7800000))
    new.geometry = new.geometry.map(lambda geom: translate(geom, xoff=4300000, yoff=7800000))
    old.to_file(tmp_path/'tracts.gpkg',layer='2010');new.to_file(tmp_path/'tracts.gpkg',layer='2022')
    cross=pd.DataFrame({'id_2010':[ids10[0]]*3,'id_2022':ids22[:3],'common_id':['77']*3})
    attrs={'n_2010':1,'n_2022':3,'relationship':'2010_to_2022_split'}
    l10=cross.assign(**attrs);l22=cross[['id_2022','common_id']].assign(**attrs)
    for year,table in [(2010,l10),(2022,l22)]:
        gpd.GeoDataFrame(table,geometry=[None]*len(table),crs=5880).to_file(tmp_path/'lookup.gpkg',layer=str(year))
    baseline=new.rename(columns={'code_tract':'id_2022'}).merge(l22,on='id_2022',how='left')
    baseline.to_file(tmp_path/'base.gpkg')
    pd.DataFrame({'common_id':['77'],**{k:[v] for k,v in attrs.items()}}).to_csv(tmp_path/'sizes.csv',index=False)
    return Context(cfg)


def test_contacts_excluded_and_identifiers_stable_under_input_reordering():
    old=gpd.GeoDataFrame({'id_2010':['a','b']},geometry=[box(0,0,1,1),box(10,0,11,1)],crs=5880)
    new=gpd.GeoDataFrame({'id_2022':['x','touch','y']},geometry=[box(0,0,1,1),box(1,0,2,1),box(10,0,11,1)],crs=5880)
    cross,_,_,_,base=correspondence(old,new)
    assert 'touch' not in cross.id_2022.tolist()
    assert base.loc[base.id_2022=='touch','common_id'].isna().all()
    reordered=correspondence(old.iloc[::-1],new.iloc[::-1])[0]
    assert cross.set_index('id_2022').common_id.to_dict()==reordered.set_index('id_2022').common_id.to_dict()


def test_imported_contacts_removed_complete_groups_merged_and_unmatched_retained(tmp_path):
    ctx=fixture_context(tmp_path)
    report=run(ctx);bundle,meta=load_bundle(ctx)
    assert report['rejected_edges']==1
    assert len(bundle['common_geometry_2022'])==1
    assert bundle['common_geometry_2022'].area.iloc[0]==2
    assert bundle['common_geometry_2022'].n_2022.iloc[0]==2
    assert len(bundle['comparison_geometry'])==4  # two matched pieces and two unmatched city tracts
    assert '222222200000001' in bundle['lookup_2022'].id_2022.tolist()
    assert bundle['base_geometry_2022'].id_2022.str.startswith('1111111').all()
    assert set(bundle['unmatched_2022'].tract_id)=={'111111100000002','111111100000003'}
    assert len(bundle['unmatched_geometry_2022'])==2
    assert report['population_coverage']['2022']['measures']['population']['status']=='source_unavailable'
    assert ctx.table('harmonisation','common_geometry_2022').common_id.nunique()==1


def test_recomputation_matches_globally_then_selects_complete_municipality_groups(tmp_path):
    ctx=fixture_context(tmp_path)
    ctx.config['census']['recompute_harmonisation']=True
    run(ctx);bundle,_=load_bundle(ctx)
    assert '222222200000001' in bundle['lookup_2022'].id_2022.tolist()
    assert bundle['common_geometry_2022'].area.iloc[0]==2
    assert len(bundle['common_geometry_2022'])==1


def test_mode_switch_replaces_all_artifacts_and_ignores_legacy_geometry(tmp_path):
    ctx=fixture_context(tmp_path)
    first=run(ctx);first_generation=first['generation']
    legacy=ctx.intermediate/'harmonisation'/'comparison_geometry.parquet'
    pd.DataFrame({'common_id':['wrong'],'area_km2':[999]}).to_parquet(legacy)
    ctx.config['census']['recompute_harmonisation']=True
    second=run(ctx);bundle,meta=load_bundle(ctx)
    assert meta['generation']!=first_generation
    assert meta['version']!=first['version']
    assert bundle['common_geometry_2022'].area.iloc[0]==2
    assert set(bundle['comparison_geometry'].common_id.dropna())==set(bundle['common_geometry_2022'].common_id)
    assert all(ctx.table('harmonisation',name).harmonisation_version.eq(meta['version']).all()
               for name in ['lookup_2010','lookup_2022','group_sizes','common_geometry_2022'])
    assert legacy.exists()  # old loose files cannot affect pointer-based consumers


def test_tampering_is_rejected_before_analytical_inputs_are_read(tmp_path):
    ctx=fixture_context(tmp_path);run(ctx)
    path=ctx.artifact('harmonisation','common_geometry_2022.parquet')
    path.write_bytes(path.read_bytes()+b'corruption')
    with pytest.raises(WorkflowError,match='artifact changed'):
        indicators_run(ctx)


def test_failed_bundle_publication_keeps_previous_complete_generation(tmp_path,monkeypatch):
    ctx=fixture_context(tmp_path);run(ctx)
    bundle,meta=load_bundle(ctx)
    pointer=(ctx.intermediate/'harmonisation/current.json').read_bytes()
    def fail(*args,**kwargs):raise RuntimeError('Interrupted write')
    monkeypatch.setattr(pd.DataFrame,'to_parquet',fail)
    with pytest.raises(RuntimeError,match='Interrupted write'):
        publish_bundle(ctx,bundle,meta)
    assert (ctx.intermediate/'harmonisation/current.json').read_bytes()==pointer
    assert load_bundle(ctx)[1]['generation']==meta['generation']


def test_coverage_reports_excluded_values_and_missingness(tmp_path):
    ctx=fixture_context(tmp_path)
    tables=tmp_path/'tables';tables.mkdir()
    for y,ds,cols in [(2010,'Pessoa',{'pessoa03_V001':[100,7]}),
                       (2010,'Domicilio',{'domicilio01_V002':[40,np.nan]}),
                       (2022,'Basico',{'V0001':[55,45,3,2]}),
                       (2022,'Domicilio',{'domicilio01_V00001':[20,20,1,1]})]:
        ids=['111111100000001','111111100000002'] if y==2010 else ['111111100000001','222222200000001','111111100000002','111111100000003']
        pd.DataFrame({'code_tract':ids,**cols}).to_parquet(tables/f'{y}_tracts_{ds}_v0.5.0.parquet')
    report=run(ctx)
    measures=report['population_coverage']['2022']['measures']
    assert measures['population']['matched_known_total']==100
    assert measures['population']['unmatched_known_total']==5
    assert measures['population']['unmatched_share_of_known_total']==5/105
    assert report['population_coverage']['2010']['measures']['households']['status']=='partial'


def test_unknown_municipality_fails_without_publishing_empty_results(tmp_path):
    ctx=fixture_context(tmp_path,municipality='9999999')
    with pytest.raises(WorkflowError,match='No 2022 source tracts'):
        run(ctx)
    assert not (ctx.intermediate/'harmonisation/current.json').exists()


def test_saved_area_uses_original_project_then_union_order():
    from brazil_project.harmonisation.census import dissolved_common_geometry
    base=gpd.GeoDataFrame({'common_id':['g','g']},geometry=[box(4300000,7800000,4350000,7850000),box(4340000,7800000,4400000,7850000)],crs=5880)
    sizes=pd.DataFrame({'common_id':['g'],'n_2010':[1],'n_2022':[2],'relationship':['2010_to_2022_split']})
    result=dissolved_common_geometry(base,sizes)
    expected=base.to_crs(6933).dissolve(by='common_id').area.iloc[0]/1e6
    assert result.area_km2.iloc[0]==expected


def test_changed_sources_and_wrong_scope_are_rejected(tmp_path):
    ctx=fixture_context(tmp_path);run(ctx)
    ctx.municipality='2222222'
    with pytest.raises(WorkflowError,match='scope, mode, or source'):
        load_bundle(ctx)
    ctx.municipality='1111111'
    path=ctx.path('census','baseline_group_sizes')
    path.write_text(path.read_text()+'\n')
    with pytest.raises(WorkflowError,match='scope, mode, or source'):
        load_bundle(ctx)


def test_conflicting_imported_group_metadata_is_rejected(tmp_path):
    ctx=fixture_context(tmp_path)
    sizes=pd.read_csv(ctx.path('census','baseline_group_sizes'))
    sizes.loc[0,'n_2022']=99
    sizes.to_csv(ctx.path('census','baseline_group_sizes'),index=False)
    with pytest.raises(WorkflowError,match='Imported group counts'):
        run(ctx)


def test_geometry_parts_have_distinct_ids_and_are_not_discarded(tmp_path):
    from brazil_project.harmonisation.census import attach_base,dissolved_common_geometry
    pieces=gpd.GeoDataFrame({'id_2022':['a','a']},geometry=[box(4300000,7800000,4300001,7800001),box(4300002,7800000,4300003,7800001)],crs=5880)
    lookup=pd.DataFrame({'id_2022':['a'],'common_id':['g'],'n_2010':[1],'n_2022':[1],'relationship':['1:1']})
    base=attach_base(pieces,lookup)
    assert base.part_id.is_unique and len(base)==2
    merged=dissolved_common_geometry(base,lookup.drop(columns='id_2022'))
    assert len(merged)==1 and merged.geometry.iloc[0].geom_type=='MultiPolygon'
    assert merged.area.iloc[0]==2


def test_all_rejected_contacts_preserve_unmatched_geometry_without_forcing_groups(tmp_path):
    from shapely.affinity import translate
    ctx=fixture_context(tmp_path)
    old=gpd.read_file(ctx.path('census','tracts'),layer='2010')
    old.geometry=old.geometry.map(lambda geom:translate(geom,xoff=-2))
    old.to_file(ctx.path('census','tracts'),layer='2010')
    report=run(ctx);bundle,_=load_bundle(ctx)
    assert report['groups']==0 and report['rejected_edges']==3
    assert len(bundle['unmatched_geometry_2022'])==4
    assert bundle['lookup_2022'].empty and bundle['common_geometry_2022'].empty
