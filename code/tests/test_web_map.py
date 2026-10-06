"""Independent checks of public-map weighting and available-year coverage."""
import runpy
import pandas as pd
import pytest

web = runpy.run_path('code/scripts/build_web_map.py')


def test_summary_uses_counts_and_paired_coverage():
    frame = pd.DataFrame({'black_2010':[0.1,0.8,None], 'black_2022':[0.2,None,0.3],
                          'black_n2010':[10,80,None], 'black_d2010':[100,100,None],
                          'black_n2022':[20,None,90], 'black_d2022':[100,None,300]})
    summary = web['aggregate'](frame,'black')
    assert summary['annual'][0]['percent'] == 45
    assert summary['annual'][1]['percent'] == 27.5
    assert summary['paired'][0]['areas'] == 1
    assert summary['changePP'] == 10


def test_density_summary_uses_total_area_and_percentage_change():
    frame = pd.DataFrame({'population_density_2010':[10,20], 'population_density_2022':[20,10],
                          'population_density_n2010':[10,60], 'population_density_d2010':[1,3],
                          'population_density_n2022':[20,30], 'population_density_d2022':[1,3]})
    summary = web['aggregate'](frame,'population_density')
    assert summary['annual'][0]['percent'] == 17.5
    assert summary['annual'][1]['percent'] == 12.5
    assert summary['changePP'] == pytest.approx(100*(50/70-1))


def test_municipality_overview_counts_a_shared_complete_group_once():
    metrics = pd.DataFrame({'common_id':['a','b'],'geometry':[None,None]})
    for key in web['INDICATORS']:
        for year in (2010,2022):
            metrics[f'{key}_{year}'] = [0.1,0.5]
            metrics[f'{key}_n{year}'] = [10,100]
            metrics[f'{key}_d{year}'] = [100,200]
    members = pd.DataFrame({'common_id':['a','a','b'],'code_muni':['3106200','3304557','3106200']})
    result = web['overview_metrics'](metrics,members).set_index('code_muni')
    assert result.loc['3106200','black_n2010'] == 110
    assert result.loc['3106200','black_2010'] == pytest.approx(110/300)
    assert result.loc['3304557','black_n2010'] == 10


def test_export_preserves_groups_absent_from_an_indicator_as_unavailable():
    import geopandas as gpd
    from shapely.geometry import box
    from types import SimpleNamespace
    common = gpd.GeoDataFrame({'common_id':['a','b'],'n_2010':[1,1],'n_2022':[1,1],'relationship':['1:1','1:1']},geometry=[box(0,0,1,1),box(1,0,2,1)],crs=5880)
    tables = {}
    for key, (_, _, denominator, numerator) in web['INDICATORS'].items():
        row = {'common_id':'a'}
        for year in (2010,2022):
            if key == 'population_density':
                row.update({f'{key}_{year}':5,'area_km2':2,f'pop_{year}':10})
            else:
                row.update({f'{key}_ratio_{year}':0.5,f'{denominator}_{year}':20,f'{numerator}_{year}':10})
        row[f'{key}_change_pct' if key=='population_density' else f'{key}_ratio_change_pp']=0
        tables[key]=pd.DataFrame([row])
    row={'common_id':'a','income_change_pct':0,'income_change_brl':0}
    for year in (2010,2022):
        row.update({f'income_{year}':100,f'heads_used_{year}':2,f'n_used_{year}':1,f'missing_weights_{year}':0,f'complete_{year}':True,f'n_{year}_y':1})
    tables['income']=pd.DataFrame([row])
    result=web['measure_fields'](SimpleNamespace(table=lambda stage,key:tables[key]),common).set_index('common_id')
    assert len(result)==2
    assert result.loc['a','black_2010']==0.5
    assert pd.isna(result.loc['b','literacy_2010'])
    assert pd.isna(result.loc['b','literacy_n2010'])
    assert pd.isna(result.loc['b','income_2022'])


def test_recomputed_member_hash_ids_have_distinct_search_shards():
    assert web['common_shard']('287178') == '28'
    assert web['common_shard']('g_ab0123456789012345678901') == 'g-ab'
    with pytest.raises(Exception,match='Unsupported common-area identifier'):
        web['common_shard']('../bad')
