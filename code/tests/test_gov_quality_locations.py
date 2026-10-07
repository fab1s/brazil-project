"""Verify diagnostic units and immutable frozen-source contracts, not geocoding truth."""
import json

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, LineString

from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.gov_quality import audit_locations, verify_frozen_inputs, run
from brazil_project.infrastructure.location_qa import fingerprint


def inputs():
    source = pd.DataFrame({'id_projeto_investimento': ['1', '1', '2', '3', '3', '4', '5'],
                           'uf_principal': ['MG', 'MG', 'MG', 'MG', 'SP', 'SP', None]})
    geometry = [Point(-43, -19)]*4 + [Point(-44, -20), LineString([(-40, -20), (-41, -21)]), None]
    parts = gpd.GeoDataFrame({'component_id': [str(i) for i in range(7)], 'source_row': range(7),
        'project_id': source.id_projeto_investimento, 'geometry_type': ['Point']*5+['LineString', 'Missing'],
        'location_status': ['eligible_unverified']*6+['quarantined_invalid_location'],
        'map_eligible': [True]*6+[False], 'primary_state_excluded': [False, False, True, False, False, False, False],
        'final_map_eligible': [True, True, False, True, True, True, False]}, geometry=geometry, crs=4674)
    return source, parts


def test_coordinate_multiplicity_counts_project_ids_not_rows_or_components():
    source, parts = inputs()
    original_source, original_parts = source.copy(deep=True), parts.copy(deep=True)
    result = audit_locations(source, parts, 2)
    meta = result['metadata']
    assert meta['max_projects_at_one_coordinate'] == 3
    assert meta['valid_point_projects'] == 3
    assert meta['shared_point_projects'] == 3
    assert meta['only_shared_point_projects'] == 2
    assert meta['eligible_point_projects'] == 2
    assert meta['eligible_nonshared_point_projects'] == 1
    site = result['tables']['coordinate_sites'].iloc[0]
    assert site.distinct_projects == 3 and site.point_components == 4
    assert meta['new_exclusions'] == meta['point_coordinates_corrected'] == 0
    pd.testing.assert_frame_equal(source, original_source)
    pd.testing.assert_frame_equal(parts, original_parts)


def test_project_with_shared_and_separate_point_is_not_only_shared():
    source, parts = inputs()
    project = audit_locations(source, parts, 2)['tables']['point_project_coverage'].set_index('project_id')
    assert project.loc['3', 'has_shared_point']
    assert project.loc['3', 'has_eligible_nonshared_point']
    assert not project.loc['3', 'only_shared_valid_points']
    assert project.loc['3', 'state'] == 'Conflicting'
    assert project.loc['4', 'has_line'] and not project.loc['4', 'has_valid_point']
    assert project.loc['5', 'has_no_eligible_component']


def test_nonstandard_source_index_and_binary_integer_flags_keep_correct_id_counts():
    source, parts = inputs()
    source.index = range(20, 27)
    for flag in ['map_eligible', 'primary_state_excluded', 'final_map_eligible']:
        parts[flag] = parts[flag].astype(int)
    result = audit_locations(source, parts, 2)
    assert result['metadata']['eligible_point_projects'] == 2
    projects = result['tables']['point_project_coverage'].set_index('project_id')
    assert projects.loc['1', 'state'] == 'MG'
    assert projects.loc['3', 'state'] == 'Conflicting'


@pytest.mark.parametrize('mutation,match', [
    ('identity', 'identities'), ('missing_row', 'every original'), ('duplicate', 'unique'),
    ('policy', 'approved policy'), ('fractional_row', 'source rows'), ('geometry_type', 'geometry types'), ('crs', 'EPSG:4674')])
def test_bad_frozen_geometry_contract_fails_instead_of_silent_cleanup(mutation, match):
    source, parts = inputs()
    if mutation == 'identity': parts.loc[0, 'project_id'] = 'unrelated'
    if mutation == 'missing_row': parts = parts.iloc[:-1]
    if mutation == 'duplicate': parts.loc[1, 'component_id'] = parts.loc[0, 'component_id']
    if mutation == 'policy': parts.loc[2, 'final_map_eligible'] = True
    if mutation == 'fractional_row':
        parts['source_row'] = parts.source_row.astype(float)
        parts.loc[0, 'source_row'] = .5
    if mutation == 'geometry_type': parts.loc[0, 'geometry_type'] = 'Polygon'
    if mutation == 'crs': parts = parts.to_crs(4326)
    with pytest.raises(WorkflowError, match=match): audit_locations(source, parts, 2)


def test_invalid_points_are_reported_without_relocation_or_reclassification():
    source, parts = inputs()
    parts.loc[0, 'geometry'] = Point(-181, -19)
    meta = audit_locations(source, parts, 2)['metadata']
    assert meta['invalid_nonempty_point_components'] == 1
    assert meta['valid_point_components'] == 4
    assert parts.loc[0, 'geometry'].x == -181


def test_signed_zero_coordinates_share_one_geographic_site():
    source, parts = inputs()
    parts.loc[0, 'geometry'] = Point(0., 0.)
    parts.loc[2, 'geometry'] = Point(-0., 0.)
    sites = audit_locations(source, parts, 2)['tables']['coordinate_sites']
    assert sites.loc[sites.longitude.eq(0), 'distinct_projects'].iloc[0] == 2


def frozen(tmp_path):
    cfg = tmp_path/'custom.toml'
    cfg.write_text('[project]\nroot="."\nmunicipality=""\n[location_qa]\nsource="data/source.bin"\nreferences="data/reference"\n')
    ctx = Context(cfg)
    paths = [tmp_path/'data/source.bin', tmp_path/'code/brazil_project/infrastructure/location_qa.py',
        tmp_path/'code/scripts/filter_obras_primary_state.py', tmp_path/'data/reference/municipalities.zip',
        tmp_path/'data/intermediate/obrasgov-primary-state-filter/component_audit.parquet']
    for n, path in enumerate(paths):
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(('frozen-'+str(n)).encode())
    qa = {'status': 'completed', 'contract': {'policy_version': '1.0', 'source_sha256': fingerprint(paths[0]), 'code_sha256': fingerprint(paths[1]),
            'references': {'municipalities': {'path': paths[3].name, 'sha256': fingerprint(paths[3])}}}}
    filtered = {'status': 'completed', 'policy': 'exclude_entirely_outside_primary_state_v1', 'script_sha256': fingerprint(paths[2]),
                'inputs': {'data/source.bin': fingerprint(paths[0])},
                'output_sha256': {'component_audit': fingerprint(paths[4])}}
    for stage, payload in [('obrasgov-location-qa', qa), ('obrasgov-primary-state-filter', filtered)]:
        path = ctx.artifact(stage, 'report.json'); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload))
    return ctx, paths


def test_frozen_inputs_are_bound_by_bytes_and_relevant_implementation(tmp_path):
    ctx, paths = frozen(tmp_path)
    source, components, hashes, _, _ = verify_frozen_inputs(ctx)
    assert source == paths[0] and components == paths[4]
    assert all(hashes[path] == fingerprint(path) for path in paths)
    paths[1].write_text('changed QA implementation')
    with pytest.raises(WorkflowError, match='changed'): verify_frozen_inputs(ctx)


def test_changed_frozen_reference_is_rejected(tmp_path):
    ctx, paths = frozen(tmp_path)
    paths[3].write_bytes(b'changed geography')
    with pytest.raises(WorkflowError, match='changed'): verify_frozen_inputs(ctx)


def test_contradictory_saved_source_manifests_fail_before_reading(tmp_path):
    ctx, _ = frozen(tmp_path)
    path = ctx.artifact('obrasgov-primary-state-filter', 'report.json')
    saved = json.loads(path.read_text())
    saved['inputs']['data/source.bin'] = 'different-original-source'
    path.write_text(json.dumps(saved))
    with pytest.raises(WorkflowError, match='Contradictory'): verify_frozen_inputs(ctx)


def test_unapproved_frozen_policy_cannot_be_silently_adopted(tmp_path):
    ctx, _ = frozen(tmp_path)
    path = ctx.artifact('obrasgov-primary-state-filter', 'report.json')
    saved = json.loads(path.read_text()); saved['policy'] = 'exclude-whole-projects'
    path.write_text(json.dumps(saved))
    with pytest.raises(WorkflowError, match='approved national policies'): verify_frozen_inputs(ctx)


def test_future_date_screening_requires_explicit_reproducible_as_of_date(tmp_path):
    ctx, _ = frozen(tmp_path)
    with pytest.raises(WorkflowError, match='explicit ISO date'): run(ctx)
