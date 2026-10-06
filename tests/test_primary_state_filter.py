import pandas as pd
import geopandas as gpd
import pytest
import json
from pathlib import Path
from types import SimpleNamespace
from shapely.geometry import Point
from scripts.filter_obras_primary_state import apply_filter, verified_inputs
from brazil_project.infrastructure.location_qa import fingerprint
from brazil_project.io import WorkflowError


def fixture():
    components = gpd.GeoDataFrame({'component_id': ['0:0', '0:1', '1:0', '2:0', '3:0', '4:0'],
        'project_id': ['repeat', 'repeat', 'other', 'partial', 'missing', 'invalid'],
        'map_eligible': [True, True, False, True, True, False]}, geometry=[Point(i, 0) for i in range(6)], crs=4674)
    checks = pd.DataFrame({'component_id': components.component_id, 'primary_state_check':
        ['entirely_outside', 'fully_inside', 'entirely_outside', 'partly_inside_or_boundary_contact',
         'unknown_or_missing_primary_state', 'not_assessable_geometry'], 'intersected_states': ['BB', 'AA', '', 'AA|BB', '', '']})
    return components, checks


def test_excludes_exactly_entirely_outside_without_dropping_projects_or_reintroducing_quarantine():
    components, checks = fixture()
    original = components.copy(deep=True)
    result = apply_filter(components, checks.iloc[::-1])
    assert result.primary_state_excluded.tolist() == [True, False, True, False, False, False]
    assert result.final_map_eligible.tolist() == [False, True, False, True, True, False]
    assert result.component_id.tolist() == components.component_id.tolist()
    assert result.geometry.equals(components.geometry)
    assert components.equals(original)
    assert result.loc[1, 'project_id'] == 'repeat'
    assert result.exclusion_reason.iloc[0] == 'entirely_outside_reported_primary_state'


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'unknown'])
def test_rejects_incomplete_duplicate_or_unknown_diagnostics(fault):
    components, checks = fixture()
    if fault == 'missing': checks = checks.iloc[:-1]
    elif fault == 'duplicate': checks = pd.concat([checks, checks.iloc[:1]])
    else: checks.loc[0, 'primary_state_check'] = 'unverified_new_method'
    with pytest.raises(WorkflowError): apply_filter(components, checks)


def test_rejects_tampered_or_incomplete_producer(tmp_path):
    diagnostic = tmp_path / 'outputs/tables/obrasgov-primary-state'
    diagnostic.mkdir(parents=True)
    component = tmp_path / 'component_audit.parquet'; component.write_bytes(b'components')
    source = tmp_path / 'source.gpkg'; source.write_bytes(b'source')
    csv = diagnostic / 'components.csv'; csv.write_text('original diagnostic')
    report = {'status': 'completed', 'output_fingerprints': {'component_audit': fingerprint(component)},
              'contract': {'source_sha256': fingerprint(source)}}
    report_path = tmp_path / 'report.json'; report_path.write_text(json.dumps(report))
    summary = {'status': 'completed', 'inputs': {p.name: fingerprint(p) for p in (component, source)},
               'output_sha256': {'components.csv': fingerprint(csv)},
               'script_sha256': fingerprint(Path(__file__).resolve().parents[1] / 'scripts/check_obras_primary_state.py')}
    (diagnostic / 'summary.json').write_text(json.dumps(summary))
    ctx = SimpleNamespace(root=tmp_path, artifact=lambda stage, name: tmp_path / name,
                          path=lambda section, key: source, require=lambda path: path)
    verified_inputs(ctx)
    csv.write_text('modified diagnostic')
    with pytest.raises(WorkflowError, match='Changed'):
        verified_inputs(ctx)
    summary['status'] = 'running'
    (diagnostic / 'summary.json').write_text(json.dumps(summary))
    with pytest.raises(WorkflowError, match='completed'):
        verified_inputs(ctx)
