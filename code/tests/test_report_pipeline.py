import json
from pathlib import Path
from brazil_project import cli


def config(tmp_path):
    p=tmp_path/'project.toml';p.write_text('[project]\nroot="."\nmunicipality=""\n[census]\nrecompute_harmonisation=false\n');return p


def test_obrasgov_one_command_orders_full_flow_and_reports(tmp_path,monkeypatch):
    calls=[];reports=[]
    monkeypatch.setattr(cli,'dispatch',lambda ctx,stage:calls.append(stage) or {})
    monkeypatch.setattr(cli,'render_report',lambda ctx,name:reports.append(name) or {'report':name,'status':'completed'})
    assert cli.main(['run','obrasgov','--config',str(config(tmp_path))])==0
    assert calls==list(cli.OBRAS_FLOW)
    assert set(reports)=={'obrasgov_data_extraction','obrasgov_preprocessing'}
    assert len(reports)==2


def test_failed_processing_blocks_dependent_reports_but_continues_all(tmp_path,monkeypatch):
    calls=[];reports=[]
    def dispatch(ctx,stage):
        calls.append(stage)
        if stage=='harmonisation':raise RuntimeError('bad input')
        return {}
    monkeypatch.setattr(cli,'dispatch',dispatch)
    monkeypatch.setattr(cli,'render_report',lambda ctx,name:reports.append(name) or {'report':name,'status':'completed'})
    assert cli.main(['run','all','--config',str(config(tmp_path))])==1
    assert 'ibama' in calls and 'indicators' not in calls and 'charts' not in calls
    assert 'ibge_census_temporal_comparison' not in reports
    assert 'obrasgov_preprocessing' in reports


def test_report_failure_does_not_relabel_processing(tmp_path,monkeypatch):
    monkeypatch.setattr(cli,'dispatch',lambda ctx,stage:{})
    def fail(ctx,name):raise RuntimeError('report failed')
    monkeypatch.setattr(cli,'render_report',fail)
    assert cli.main(['run','harmonisation','--config',str(config(tmp_path))])==1
    evidence=json.loads((tmp_path/'data/intermediate/runs/report.json').read_text())
    assert evidence['stages'][0]['status']=='completed'
    assert evidence['reports'][0]['status']=='failed'


def test_scope_rejection_precedes_processing(tmp_path,monkeypatch):
    calls=[];monkeypatch.setattr(cli,'dispatch',lambda ctx,stage:calls.append(stage))
    assert cli.main(['run','obrasgov','--municipality','3106200','--config',str(config(tmp_path))])==1
    assert calls==[]


def test_from_saved_skips_processing(tmp_path,monkeypatch):
    monkeypatch.setattr(cli,'dispatch',lambda *args:(_ for _ in ()).throw(AssertionError('unexpected processing')))
    monkeypatch.setattr(cli,'render_report',lambda ctx,name:{'report':name,'status':'completed'})
    assert cli.main(['report','ibge_census_tract_harmonisation','--from-saved','--config',str(config(tmp_path))])==0


def test_individual_snapshot_succeeds_without_publishing_incomplete_report(tmp_path,monkeypatch):
    calls=[];monkeypatch.setattr(cli,'dispatch',lambda ctx,stage:calls.append(stage) or {})
    monkeypatch.setattr(cli,'render_report',lambda *args:(_ for _ in ()).throw(AssertionError('incomplete report published')))
    assert cli.main(['run','obrasgov-snapshot','--config',str(config(tmp_path))])==0
    assert calls==['obrasgov-snapshot']


def test_acquisition_is_never_an_ordinary_dependency():
    assert not set(cli.expand(cli.STAGES)).intersection(cli.ACQUISITION)
