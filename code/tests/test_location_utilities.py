"""Post-implementation audit fixes: provenance, durable manifests and checks."""
import json
from pathlib import Path
import pytest
from brazil_project.io import WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint
from scripts.acquire_location_references import write_manifest
from scripts.plot_location_qa import verified_plot_inputs


def test_manifest_interruption_preserves_previous_provenance(tmp_path,monkeypatch):
    path=tmp_path/'manifest.json';write_manifest(path,{'old':'verified'})
    def interrupted(*args):raise OSError('simulated interruption')
    with monkeypatch.context() as m:
        m.setattr(Path,'replace',interrupted)
        with pytest.raises(OSError):write_manifest(path,{'new':'verified'})
    assert json.loads(path.read_text())=={'old':'verified'}
    write_manifest(path,{'new':'verified'})
    assert json.loads(path.read_text())=={'new':'verified'}
    assert not path.with_suffix('.tmp.json').exists()


def plot_context(tmp_path,status):
    source=tmp_path/'source.gpkg';source.write_bytes(b'source')
    component=tmp_path/'component_audit.parquet';component.write_bytes(b'components')
    mun=tmp_path/'municipalities.zip';mun.write_bytes(b'municipalities')
    report={'status':status,'contract':{'source_sha256':fingerprint(source),'references':{'municipalities':{'path':mun.name,'sha256':fingerprint(mun)}}},'output_fingerprints':{'component_audit':fingerprint(component)}}
    (tmp_path/'report.json').write_text(json.dumps(report))
    class Context:
        def path(self,section,key):return source if key=='source' else tmp_path
        def artifact(self,stage,name):return tmp_path/name
        def require(self,path):
            if not path.is_file():raise WorkflowError('Missing input')
            return path
    return Context(),component,mun


def test_plot_rejects_incomplete_producer_run(tmp_path):
    ctx,_,_=plot_context(tmp_path,'running')
    with pytest.raises(WorkflowError,match='completed'):verified_plot_inputs(ctx)


def test_plot_rejects_changed_component_or_reference(tmp_path):
    ctx,component,mun=plot_context(tmp_path,'completed')
    assert verified_plot_inputs(ctx)==(component,mun)
    component.write_bytes(b'changed')
    with pytest.raises(WorkflowError,match='changed'):verified_plot_inputs(ctx)
    component.write_bytes(b'components');mun.write_bytes(b'changed')
    with pytest.raises(WorkflowError,match='changed'):verified_plot_inputs(ctx)
