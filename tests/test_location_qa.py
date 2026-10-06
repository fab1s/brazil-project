"""Meaningful eligibility boundaries and provenance preservation for location QA."""
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, LineString, Polygon, MultiPoint, GeometryCollection
from brazil_project.infrastructure.location_qa import audit, atomic_parts
from brazil_project.io import WorkflowError


def references():
    municipalities = gpd.GeoDataFrame({'CD_MUN':['3100001','3300001','2600001'],'SIGLA_UF':['MG','RJ','PE']},
        geometry=[Polygon([(-50,-25),(-45,-25),(-45,-20),(-50,-20)]),
                  Polygon([(-45,-25),(-40,-25),(-40,-20),(-45,-20)]),
                  Polygon([(-35.02,-20.02),(-34.98,-20.02),(-34.98,-19.98),(-35.02,-19.98)])],crs=4674)
    # Intentionally omit the small IBGE island from the generalized land mask.
    land = gpd.GeoDataFrame(geometry=[Polygon([(-55,-30),(-40,-30),(-40,-15),(-55,-15)])],crs=4674)
    coast = gpd.GeoDataFrame(geometry=[LineString([(-40,-35),(-40,-10)])],crs=4674)
    return municipalities,land,coast


def frame(geometries, descriptions=None):
    return gpd.GeoDataFrame({'id_projeto_investimento':['duplicate']*len(geometries),
        'uf_principal':['MG']*len(geometries),'desc_nome':descriptions or ['Pavimentação urbana']*len(geometries)},geometry=geometries,crs=4674)


def test_recursive_collections_and_duplicate_ids_preserved():
    geometry = GeometryCollection([MultiPoint([(-46,-22),(-39,-22)]),LineString([(-46,-22),(-46,-23)])])
    f=frame([geometry,Point(-46,-22)])
    a=audit(f,*references())
    assert len(atomic_parts(geometry))==3 and len(a)==4 and a.component_id.is_unique
    assert a.source_row.tolist()==[0,0,0,1] and a.project_id.nunique()==1
    assert a.map_eligible.tolist()==[True,False,True,True]
    assert f.geometry.iloc[0].equals(geometry)


def test_offshore_marine_coastal_foreign_and_island():
    a=audit(frame([Point(-39,-22),Point(-39,-22),Point(-39.99,-22),Point(-51,-22),Point(-35,-20)],
        ['Pavimentação','Dragagem portuária','Pavimentação','Pavimentação','Pavimentação']),*references())
    assert a.location_status.tolist()==['quarantined_offshore','possible_marine_review','coastal_review','quarantined_outside_brazil','administrative_or_coordinate_review']
    assert a.map_eligible.tolist()==[False,True,True,False,True]
    assert a.offshore_samples.iloc[-1]==0


def test_boundary_state_and_municipality_checks():
    f=frame([Point(-45,-22),Point(-42,-22),Point(-46,-22)])
    f['codigo_municipio']=['3300001','3100001','3100001']
    a=audit(f,*references())
    assert a.intersected_municipalities.iloc[0]=='3100001|3300001'
    assert a.uf_mismatch_samples.tolist()==[0,1,0]
    assert a.municipality_mismatch_samples.tolist()==[0,1,0]
    assert a.map_eligible.all()


def test_invalid_missing_polygon_and_crs():
    f=frame([None,Point(),Point(500,-20),Point(float('nan'),-22),Polygon([(-46,-22),(-47,-22),(-46,-23)])])
    a=audit(f,*references())
    assert not a.map_eligible.any()
    assert a.missing_geometry.iloc[0] and a.empty_geometry.iloc[1] and a.out_of_range.iloc[2] and a.nonfinite_coordinates.iloc[3]
    assert a.location_status.iloc[-1]=='polygon_display_excluded'
    with pytest.raises(WorkflowError,match='EPSG:4674'):
        audit(f.set_crs(4326,allow_override=True),*references())


def test_line_path_includes_offshore_vertices():
    # A long offshore excursion must be caught even with both endpoints onshore.
    f=frame([LineString([(-46,-22),(-38,-22),(-46,-23)])])
    a=audit(f,*references(),max_line_samples=2)
    assert a.far_offshore_samples.iloc[0]>0 and not a.map_eligible.iloc[0]
    assert a.sampling_capped.iloc[0]


def test_missing_reference_fails_without_network(tmp_path):
    from brazil_project.infrastructure.location_qa import run
    class Context:
        config={'location_qa':{}}
        municipality=''
        def path(self,section,key):
            return tmp_path/'source.gpkg' if key=='source' else tmp_path/'references'
        def require(self,path):
            if not path.is_file():
                raise WorkflowError('Missing local input: '+str(path))
            return path
    (tmp_path/'source.gpkg').write_bytes(b'placeholder')
    with pytest.raises(WorkflowError,match='manifest.json'):
        run(Context())


def test_coastal_tolerance_changes_eligibility_explicitly():
    f=frame([Point(-39.98,-22)])
    a=audit(f,*references(),coast_tolerance_m=5000)
    b=audit(f,*references(),coast_tolerance_m=1000)
    assert a.map_eligible.iloc[0] and not b.map_eligible.iloc[0]
    assert a.geometry.iloc[0].equals(b.geometry.iloc[0])


def test_broad_taxonomy_or_place_name_is_not_a_marine_exception():
    f=frame([Point(-39,-22),Point(-39,-22)],['Reforma de escola em Nova Friburgo','Pavimentação em Porto Alegre'])
    f['tipo']='Infraestrutura Hídrica, Portos, Hidrovia'
    f['subtipo']='Dragagem, Derrocamento e Associações'
    assert not audit(f,*references()).marine_signal.any()
    assert not audit(f,*references()).map_eligible.any()


def test_nullable_metadata_and_empty_candidate_membership():
    f=frame([Point(-39,-22)])
    f['uf_principal']=pd.NA
    f['desc_projeto']=pd.NA
    a=audit(f,*references())
    assert a.declared_uf.iloc[0]==''
    assert a.intersected_municipalities.iloc[0]==''


def test_near_border_locations_are_reviewed_not_silently_accepted():
    a=audit(frame([Point(-50.005,-22)]),*references())
    assert a.map_eligible.iloc[0] and a.location_status.iloc[0]=='border_review'
    assert a.outside_brazil_samples.iloc[0]==1


def test_segment_index_preserves_coast_distances():
    from brazil_project.infrastructure.location_qa import evaluate_samples
    import numpy as np
    muni,land,coast=references()
    points=gpd.GeoDataFrame(geometry=[Point(-46,-22),Point(-39.5,-23),Point(-40.01,-25)],crs=4674)
    flags=evaluate_samples(points,muni,land,coast,5000,1000)
    projected=points.to_crs(5880);line=coast.to_crs(5880).geometry.iloc[0]
    assert np.allclose(flags.coast_distance_m,[geom.distance(line) for geom in projected.geometry],rtol=1e-12,atol=1e-8)
