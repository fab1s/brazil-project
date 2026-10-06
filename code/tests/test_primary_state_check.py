import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, LineString, Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_obras_primary_state import check_states
from brazil_project.io import WorkflowError


def test_exact_containment_including_polygons_boundaries_and_unassessable():
    geometries = [Point(1, 1), Point(3, 1), LineString([(1, 1), (3, 1)]),
                  box(.5, .5, 1.5, 1.5), box(1, .5, 3, 1.5), Point(2, 1),
                  None, Point(1, 1), Point(181, 1), Polygon([(0, 0), (2, 2), (0, 2), (2, 0)])]
    parts = gpd.GeoDataFrame({'source_row': range(10), 'component_id': [f'{i}:0' for i in range(10)],
                              'project_id': ['same'] * 10, 'declared_uf': ['AA'] * 7 + ['', 'AA', 'AA']},
                             geometry=geometries, crs=4674)
    parts['geometry_type'] = parts.geom_type.fillna('Missing')
    original = parts.copy(deep=True)
    states = gpd.GeoDataFrame({'SIGLA_UF': ['AA', 'BB']}, geometry=[box(0, 0, 2, 2), box(2, 0, 4, 2)], crs=4674)
    checked = check_states(parts, states)
    assert checked.primary_state_check.tolist() == ['fully_inside', 'entirely_outside', 'partly_inside_or_boundary_contact',
        'fully_inside', 'partly_inside_or_boundary_contact', 'fully_inside', 'not_assessable_geometry',
        'unknown_or_missing_primary_state', 'not_assessable_geometry', 'not_assessable_geometry']
    assert checked.intersected_states.iloc[2] == 'AA|BB'
    assert checked.intersected_states.iloc[5] == 'AA|BB'
    assert len(checked) == len(parts)
    assert parts.equals(original)


def test_rejects_mismatched_crs_and_ambiguous_reference():
    parts = gpd.GeoDataFrame(geometry=[Point(1, 1)], crs=4674)
    states = gpd.GeoDataFrame({'SIGLA_UF': ['AA', 'AA']}, geometry=[box(0, 0, 2, 2)] * 2, crs=4674)
    with pytest.raises(WorkflowError, match='one dissolved'):
        check_states(parts, states)
    with pytest.raises(WorkflowError, match='matching'):
        check_states(parts, states.to_crs(5880))
