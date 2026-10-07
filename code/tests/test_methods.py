import json
import numpy as np
import pandas as pd
import geopandas as gpd
import pytest
from shapely.geometry import box
from brazil_project.io import WorkflowError, identifiers
from brazil_project.harmonisation.census import correspondence
from brazil_project.indicators.temporal import aggregate, safe_ratio, income_aggregate
from brazil_project.visualisation.charts import sanitation, ntile, populations
from brazil_project.acquisition.infrastructure import pages, cached_json, flatten_projects
from brazil_project.infrastructure.projects import clean_obrasgov
from brazil_project.verification import compare_tables


def geos(ids,geometries,year):
    return gpd.GeoDataFrame({f'id_{year}':ids},geometry=geometries,crs=5880)

@pytest.mark.parametrize('old,new,label',[
    ([box(0,0,2,2)],[box(0,0,2,2)],'1:1'),
    ([box(0,0,2,2)],[box(0,0,1,2),box(1,0,2,2)],'2010_to_2022_split'),
    ([box(0,0,1,2),box(1,0,2,2)],[box(0,0,2,2)],'2010_to_2022_merge'),
    ([box(0,0,2,1),box(0,1,2,2)],[box(0,0,1,2),box(1,0,2,2)],'many_to_many')])
def test_relationships_and_unchanged_geometry(old,new,label):
    a=geos([str(i) for i in range(len(old))],old,2010)
    b=geos([str(i) for i in range(len(new))],new,2022)
    _,_,_,groups,base=correspondence(a,b)
    assert groups.relationship.tolist()==[label]
    assert base.geometry.to_wkb().tolist()==b.geometry.to_wkb().tolist()
    assert len(base)==len(b)


def test_unmatched_and_tie_use_input_order():
    a=geos(['first','second'],[box(0,0,1,2),box(1,0,2,2)],2010)
    b=geos(['matched','unmatched'],[box(0,0,2,2),box(10,10,11,11)],2022)
    cross,_,_,_,base=correspondence(a,b)
    assert cross.iloc[0].id_2010=='first'
    assert pd.isna(base.loc[base.id_2022=='unmatched','common_id']).all()


def test_missing_counts_and_duplicate_keys():
    data=pd.DataFrame({'id_2010':['a','b'],'den':[np.nan,np.nan],'num':[np.nan,np.nan]})
    lookup=pd.DataFrame({'id_2010':['a','b'],'common_id':['g','g']})
    totals=aggregate(data,lookup,2010,['den'])
    assert pd.isna(totals.den.iloc[0]) and totals.num.iloc[0]==0
    with pytest.raises(WorkflowError): aggregate(pd.concat([data,data]),lookup,2010)
    assert np.isnan(safe_ratio(pd.Series([1]),pd.Series([0])).iloc[0])


def test_income_uses_same_contributing_pairs_and_reports_coverage():
    data=pd.DataFrame({'id_2010':['a','b','c'],'heads':[2,4,np.nan],'mean_income':[100,np.nan,900]})
    lookup=pd.DataFrame({'id_2010':['a','b','c'],'common_id':['g','g','g']})
    out=income_aggregate(data,lookup,2010).iloc[0]
    assert out.income_2010==100 and out.heads_used_2010==2
    assert out.missing_weights_2010==1 and out.missing_means_2010==1
    assert not out.complete_2010


def test_sanitation_excludes_denominator_when_any_component_missing():
    data=pd.DataFrame({'code_tract':['a','b'],'domicilio01_V002':[100,100],
                       'domicilio01_V019':[5,np.nan],'domicilio01_V020':[0,0],
                       'domicilio01_V021':[0,0],'domicilio01_V023':[2,2]})
    lookup=pd.DataFrame({'id_2010':['a','b'],'common_id':['g','g']})
    out=sanitation(data,lookup,2010).iloc[0]
    assert out.households==100 and out.inadequate_sanitation==7


def test_ntile_ties_and_larger_groups_first():
    data=pd.DataFrame({'common_id':list('abcdefgh'),'value':[1]*8})
    out=ntile(data,'value',5)
    assert out.racial_quintile.tolist()==[1,1,2,2,3,3,4,5]


def test_cleaning_preserves_empty_invalid_flags_before_repair():
    frame=gpd.GeoDataFrame({'id':[1,2,3]},geometry=[box(-50,-20,-49,-19),box(200,0,201,1),None],crs=4674)
    cleaned=clean_obrasgov(frame)
    assert 1 in cleaned.id.tolist() and 2 not in cleaned.id.tolist()


def test_identifiers_do_not_gain_float_suffixes():
    assert identifiers(pd.Series([310620005670833.,np.nan])).tolist()==['310620005670833',pd.NA]


def test_parity_detects_numeric_and_missing_differences():
    expected=pd.DataFrame({'id':['a','b'],'value':[1,np.nan]})
    assert compare_tables(expected,expected,'id')['passed']
    actual=expected.copy();actual.loc[1,'value']=0
    assert not compare_tables(actual,expected,'id')['passed']

class Response:
    def __init__(self,payload): self.payload=payload
    def raise_for_status(self): pass
    def json(self): return self.payload

class Client:
    def __init__(self): self.calls=[]
    def get(self,url,params=None,timeout=None):
        self.calls.append(params)
        return Response({'data':[{'id':params['pagina']}],'page_number':params['pagina'],'total_pages':2})


def test_page_resume_and_request_fingerprint(tmp_path):
    client=Client()
    assert len(pages(client,tmp_path,'example'))==2
    assert len(client.calls)==2
    assert len(pages(client,tmp_path,'example'))==2
    assert len(client.calls)==2
    with pytest.raises(WorkflowError): cached_json(client,tmp_path/'example_000001.json','changed',{'pagina':1})


def test_wrong_page_never_silently_duplicates(tmp_path):
    class Wrong(Client):
        def get(self,*args,**kwargs): return Response({'data':[],'page_number':7,'total_pages':2})
    with pytest.raises(WorkflowError): pages(Wrong(),tmp_path,'projects')


def test_nested_projects_keep_empty_taxonomy_and_sum_investment():
    frame=flatten_projects([{'id_projeto_investimento':'x','eixos_tipos':[],
                             'investimentos_previstos':[{'vl_investimento_previsto':2},{'vl_investimento_previsto':None}],
                             'pins':[{'pin':'POINT (-50 -20)'}]}])
    assert len(frame)==1 and frame.vl_investimento_previsto_total.iloc[0]==2
    assert frame.geometry.iloc[0].geoms[0].x==-50


def test_original_duplicate_display_geometries_remain_present():
    a=geos(['a'],[box(0,0,2,2)],2010)
    b=geos(['b','b'],[box(0,0,2,2),box(0,0,2,2)],2022)
    _,_,_,_,base=correspondence(a,b)
    assert len(base)==2 and base.id_2022.tolist()==['b','b']


def test_all_continues_independent_stages_but_blocks_failed_dependencies(tmp_path,monkeypatch):
    from brazil_project import cli
    config=tmp_path/'project.toml'
    config.write_text('[project]\nroot="."\n[census]\nrecompute_harmonisation=false\n')
    executed=[]
    def dispatch(ctx,stage):
        executed.append(stage)
        if stage=='indicators':raise WorkflowError('Missing scientific input')
        return {'stage':stage}
    monkeypatch.setattr(cli,'dispatch',dispatch)
    assert cli.main(['run','all','--config',str(config)])==1
    assert 'obrasgov-snapshot' in executed and 'land-value' in executed
    assert 'charts' not in executed
    report=json.loads((tmp_path/'data/intermediate/runs/report.json').read_text())
    assert next(r for r in report['stages'] if r['stage']=='charts')['status']=='blocked'
    assert len(list((tmp_path/'data/intermediate/runs/history').glob('*.json')))>=1


def test_outer_year_estimates_do_not_fill_absent_years_with_zero():
    older=pd.DataFrame({'common_id':['a'],'ratio_2010':[.5]})
    newer=pd.DataFrame({'common_id':['b'],'ratio_2022':[.8]})
    compared=older.merge(newer,on='common_id',how='outer',validate='one_to_one')
    assert (compared.ratio_2022-compared.ratio_2010).isna().all()


def test_overview_map_lookup_handles_original_real_tract_ids(tmp_path, monkeypatch):
    """Exercise the map-producing path with the source's REAL identifier storage."""
    from types import SimpleNamespace
    from brazil_project.harmonisation import overview
    from brazil_project.io import Context
    import subprocess
    import shutil
    codes=['310620025610001','310620005650306','310620005620021','310620005620008']
    raw=tmp_path/'tracts.gpkg'
    geometries=[box(-44+i*.01,-20,-43.999+i*.01,-19.999) for i in range(4)]
    tracts=gpd.GeoDataFrame({'code_tract':[float(v) for v in codes]},geometry=geometries,crs=4326)
    for layer in ('2000_urban','2010','2022'): tracts.to_file(raw,layer=layer,driver='GPKG')
    config=tmp_path/'project.toml'
    config.write_text('[project]\nroot="."\n[census]\ntracts="tracts.gpkg"\n')
    ctx=Context(config);out=ctx.artifact('overview','report.json').parent;out.mkdir(parents=True)
    for year in (2010,2022):
        pd.DataFrame({'code_tract_2000':codes,'change_type':['stable']*4}).to_csv(out/f'change_summary_2000_{year}.csv',index=False)
        intersections=gpd.GeoDataFrame({'code_tract_2000':[float(v) for v in codes],'code_tract_new':[float(v) for v in codes],'overlap_pct':[1.]*4},geometry=geometries,crs=4326)
        intersections.to_file(out/f'intersections_2000_{year}.gpkg',driver='GPKG')
    original_which=shutil.which;original_run=subprocess.run
    monkeypatch.setattr(shutil,'which',lambda name: 'Rscript' if name=='Rscript' else original_which(name))
    monkeypatch.setattr(subprocess,'run',lambda command,*a,**kw: SimpleNamespace(returncode=0) if isinstance(command,list) and command[0]=='Rscript' else original_run(command,*a,**kw))
    overview.run(ctx)
    for code in codes:
        html=(tmp_path/'outputs/maps/overview'/f'{code}.html').read_text()
        assert '2000 tract' in html and '2010 tracts' in html and '2022 tracts' in html
