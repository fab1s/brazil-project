"""A concise GeoPackage must reconstruct every original map field exactly."""
import runpy
from types import SimpleNamespace

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import MultiPolygon, box

from brazil_project.io import WorkflowError


@pytest.fixture(scope='module')
def exporter():
    return runpy.run_path('code/scripts/export_social_gpkg.py')


@pytest.fixture
def source():
    # The racial denominator is unavailable where density population is observed.
    return gpd.GeoDataFrame({
        'common_id': ['1', '10', 'g_ab0123456789012345678901'],
        'n_2022': [1.0, 2.0, 3.0],
        'income_tracts_total_2022': [1.0, 2.0, 3.0],
        'population_density_2022': [10.0, 20.0, 30.0],
        'population_density_n2022': [100.0, 200.0, 300.0],
        'population_density_d2022': [10.0, 10.0, 10.0],
        'population_density_change': [5.0, None, -25.0],
        'black_brown_2022': [0.6, None, 0.3],
        'black_brown_n2022': [60.0, None, 90.0],
        'black_brown_d2022': [100.0, None, 300.0],
        'black_brown_change': [10.0, None, -5.0],
        'black_d2022': [100.0, 200.0, None],
        'brown_d2022': [100.0, None, 300.0],
        'literacy_n2022': [50.0, 80.0, None],
        'literacy_d2022': [70.0, 120.0, None],
        'rudimentary_sanitation_d2022': [40.0, None, 100.0],
        'water_network_d2022': [40.0, None, 100.0],
        'houses_d2022': [40.0, 60.0, None],
        'income_2022': [1500.0, 0.0, None],
        'income_heads_2022': [30.0, 25.0, 0.0],
        'income_change': [12.5, None, -50.0],
        'income_change_brl': [200.0, None, -1000.0],
    }, geometry=[MultiPolygon([box(x, 0, x+1, 1)]) for x in (0, 2, 4)],
       crs=5880, index=[8, 2, 40])


def test_one_english_column_reconstructs_each_original_with_missingness(exporter, source):
    original = source.copy(deep=True)
    concise, dictionary = exporter['simplify_fields'](source)
    pd.testing.assert_frame_equal(source, original)
    assert concise.crs == source.crs
    assert concise.geometry.to_wkb().equals(source.geometry.to_wkb())
    assert concise.common_id.tolist() == source.common_id.tolist()
    assert len(concise.columns) < len(source.columns)
    assert 'black_brown_n2022' not in concise.columns
    assert 'black_brown_population_2022' in concise.columns
    assert set(dictionary.original_field) == set(source.columns)-{'geometry'}
    assert dictionary.description.notna().all()
    for row in dictionary.itertuples(index=False):
        pd.testing.assert_series_equal(concise[row.readable_field], source[row.original_field],
                                       check_names=False)


def test_exact_equal_columns_share_one_clear_name(exporter, source):
    result, dictionary = exporter['simplify_fields'](source)
    mapped = dictionary.set_index('original_field').readable_field
    assert mapped['n_2022'] == mapped['income_tracts_total_2022'] == 'tracts_2022'
    assert mapped['black_brown_d2022'] == mapped['brown_d2022'] == 'population_for_race_2022'
    assert mapped['rudimentary_sanitation_d2022'] == mapped['water_network_d2022'] == 'households_2022'
    assert result.columns.is_unique
    assert 'income_tracts_total_2022' not in result.columns


def test_distinct_missingness_keeps_distinct_denominators(exporter, source):
    result, dictionary = exporter['simplify_fields'](source)
    mapped = dictionary.set_index('original_field').readable_field
    assert len({mapped['population_density_n2022'], mapped['black_brown_d2022'],
                mapped['black_d2022'], mapped['houses_d2022']}) == 4
    assert result.loc[2, 'total_population_2022'] == 200
    assert pd.isna(result.loc[2, 'population_for_race_2022'])
    assert result.loc[2, mapped['black_d2022']] == 200
    assert pd.isna(result.loc[2, 'households_2022'])


def test_dictionary_units_and_change_names_are_clear(exporter, source):
    _, dictionary = exporter['simplify_fields'](source)
    fields = dictionary.set_index('original_field')
    assert fields.loc['black_brown_2022', 'readable_field'] == 'black_brown_share_2022'
    assert fields.loc['black_brown_2022', 'unit'] == 'fraction'
    assert fields.loc['black_brown_change', 'readable_field'] == 'black_brown_change_pp'
    assert fields.loc['black_brown_change', 'unit'] == 'percentage points'
    assert fields.loc['population_density_change', 'readable_field'] == 'population_density_change_pct'
    assert fields.loc['population_density_change', 'unit'] == 'percent'
    assert fields.loc['income_change', 'readable_field'] == 'income_change_pct'
    assert fields.loc['income_change_brl', 'unit'] == 'BRL at July 2022 prices'


def test_unmapped_code_fails_without_dropping_source_contents(exporter, source):
    source['unknown_source_code'] = [1, 2, 3]
    before = source.copy(deep=True)
    with pytest.raises(WorkflowError, match='Unmapped'):
        exporter['simplify_fields'](source)
    pd.testing.assert_frame_equal(source, before)


def test_different_units_never_merge_even_if_values_match(exporter):
    frame = gpd.GeoDataFrame({'common_id':['1'], 'n_2022':[1.0],
                             'population_density_d2022':[1.0]},
                            geometry=[MultiPolygon([box(0,0,1,1)])], crs=5880)
    output, dictionary = exporter['simplify_fields'](frame)
    assert len(output.columns) == len(frame.columns)
    assert dictionary.readable_field.is_unique


def test_clean_geopackage_roundtrip_reconstructs_every_source_field(exporter, source, tmp_path):
    clean, dictionary = exporter['simplify_fields'](source)
    path = tmp_path/'social.gpkg'
    clean.to_file(path, layer='social', driver='GPKG', index=False)
    loaded = gpd.read_file(path, layer='social')
    exporter['verify_simplified'](source, loaded, dictionary)
    assert loaded.common_id.tolist() == source.common_id.tolist()
    assert loaded.columns.is_unique


@pytest.mark.parametrize('mutation', ['value','missingness','geometry','crs'])
def test_verification_rejects_changed_export(exporter, source, mutation):
    clean, dictionary = exporter['simplify_fields'](source)
    changed = clean.copy(deep=True)
    if mutation == 'value': changed.loc[8,'total_population_2022'] += 0.001
    elif mutation == 'missingness': changed.loc[2,'population_for_race_2022'] = 0.0
    elif mutation == 'geometry': changed.loc[8,'geometry'] = MultiPolygon([box(0,0,1.1,1)])
    else: changed = changed.set_crs(4674, allow_override=True)
    with pytest.raises(WorkflowError): exporter['verify_simplified'](source, changed, dictionary)


def test_overview_municipality_code_is_english_only(exporter):
    frame = gpd.GeoDataFrame({'code_muni':['3106200'], 'black_brown_2022':[0.4]},
                             geometry=[MultiPolygon([box(0,0,1,1)])], crs=5880)
    clean, dictionary = exporter['simplify_fields'](frame)
    assert clean.municipality_code.tolist()==['3106200']
    assert 'code_muni' not in clean.columns
    assert dictionary.set_index('original_field').loc['code_muni','readable_field']=='municipality_code'


def test_national_scope_and_existing_destination_are_protected(exporter, tmp_path):
    target = tmp_path/'not-created'/'social.gpkg'
    with pytest.raises(WorkflowError, match='national'):
        exporter['run'](SimpleNamespace(municipality='3106200'), target)
    assert not target.parent.exists()
    existing = tmp_path/'social.gpkg'; existing.write_bytes(b'existing data')
    with pytest.raises(WorkflowError, match='overwrite'):
        exporter['run'](SimpleNamespace(municipality=''), existing)
    assert existing.read_bytes()==b'existing data'
