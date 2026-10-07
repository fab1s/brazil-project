"""The public export must use the approved derivative without losing provenance."""
import importlib.util
import json
from pathlib import Path
import geopandas as gpd
import pytest
from shapely.geometry import Point, LineString, box
from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint

spec=importlib.util.spec_from_file_location('obras_web','code/scripts/build_obras_web_map.py')
web=importlib.util.module_from_spec(spec);spec.loader.exec_module(web)

@pytest.fixture
def prepared(tmp_path,monkeypatch):
    config=tmp_path/'project.toml';config.write_text('[project]\nroot="."\n[location_qa]\nsource="original.gpkg"\n')
    ctx=Context(config)
    original=gpd.GeoDataFrame({'id_projeto_investimento':['p','p'],'tipo':['Saúde','Saúde'],'vl_investimento_previsto_total':[100.,100.]},geometry=[Point(-44,-20),Point(-43,-20)],crs=4674)
    for column in web.PUBLIC_FIELDS:
        if column not in original:original[column]=column
    original.to_file(tmp_path/'original.gpkg',driver='GPKG')
    frame=original.assign(component_id=['s0-p0','s1-p0'],source_row=[0,1],location_status=['eligible_unverified','administrative_or_coordinate_review'],primary_state_check=['fully_inside_primary_state','partly_inside_or_boundary_contact'],final_map_eligible=True,primary_state_excluded=False)
    frame.loc[1,'geometry']=LineString([(-43,-20),(-43.1,-20)])
    monkeypatch.setattr(web,'require_producers',lambda *args:None)
    return ctx,frame


def save(ctx,frame):
    path=ctx.write_geo(frame,'obrasgov-primary-state-filter','map_components')
    ctx.report('obrasgov-primary-state-filter',{'status':'completed','output_sha256':{'map_components':fingerprint(path)},'map_components_after':len(frame)})


def test_export_preserves_source_rows_attributes_coordinates_and_review_flags(prepared):
    ctx,frame=prepared;save(ctx,frame)
    result,_,_=web.prepare(ctx)
    assert result.component_id.tolist()==['s0-p0','s1-p0']
    assert result.id_projeto_investimento.tolist()==['p','p']
    assert result.vl_investimento_previsto_total.tolist()==[100.,100.]
    assert result.location_status.tolist()==frame.location_status.tolist()
    assert result.geometry.to_wkb().tolist()==frame.geometry.to_wkb().tolist()


@pytest.mark.parametrize('change',['excluded','ineligible','polygon','duplicate'])
def test_export_rejects_invalid_eligibility_or_membership(prepared,change):
    ctx,frame=prepared
    if change=='excluded':frame.loc[0,'primary_state_excluded']=True
    elif change=='ineligible':frame.loc[0,'final_map_eligible']=False
    elif change=='polygon':frame.loc[0,'geometry']=box(-44,-20,-43,-19)
    else:frame.loc[1,'component_id']=frame.loc[0,'component_id']
    save(ctx,frame)
    with pytest.raises(WorkflowError):web.prepare(ctx)


def test_export_rejects_changed_output_and_municipality_scope(prepared):
    ctx,frame=prepared;save(ctx,frame)
    frame.loc[0,'component_id']='changed';ctx.write_geo(frame,'obrasgov-primary-state-filter','map_components')
    with pytest.raises(WorkflowError,match='changed'):web.prepare(ctx)
    ctx.municipality='3106200'
    with pytest.raises(WorkflowError,match='national'):web.prepare(ctx)
