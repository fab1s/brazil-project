"""Reader-facing results must preserve numerical meaning and the report contract."""
import hashlib
import json
from pathlib import Path
import zipfile
import pandas as pd
from brazil_project import reporting, report_engine


def test_source_archive_and_all_ordered_cells_preserved():
    root=Path(__file__).resolve().parents[2]
    record=json.loads((root/'docs/evidence/report-readability-preservation.json').read_text())
    archive=root/record['archive']
    if archive.exists():
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==record['sha256']
        with zipfile.ZipFile(archive) as z:
            for name,digest in record['files'].items():
                old=z.read(name);assert hashlib.sha256(old).hexdigest()==digest
                if name.endswith('.md'):
                    before,_=report_engine.parse_report(old.decode())
                    after,_=report_engine.parse_report((root/name).read_text())
                    assert [c[1] for c in before]==[c[1] for c in after]
    for name in report_engine.REPORTS:
        text=(root/'research/reports'/(name+'.md')).read_text()
        if name in report_engine.REPORT_ANNEXES:
            assert 'Executive summary' in text
            assert all(annex+'.md' in text for annex in report_engine.REPORT_ANNEXES[name])
            assert 'How to read this analysis' not in text
            continue
        assert 'How to read this analysis' in text and 'docs/codebook.md' in text
        assert 'Interpretation and limits' in text


def test_cleaning_summary_reports_counts_not_geographic_validation(monkeypatch):
    tables=[];prose=[]
    monkeypatch.setattr(reporting,'table',lambda df,*args:tables.append(df))
    monkeypatch.setattr(reporting,'markdown',prose.append)
    reporting.summary({'records':134929,'cleaned_records':133417,'removed':1512,'baseline_cleaned_records':133417,'count_matches_baseline':True,'source':'copied_snapshot'},'obrasgov')
    assert tables[0].Count.tolist()==[134929,133417,1512,133417]
    assert any('counts only' in s and 'coordinate accuracy' in s for s in prose)
    assert any('<details>' in s and '```json' in s for s in prose)


def test_indicator_summary_units_missingness_and_saved_values(monkeypatch):
    tables=[]
    monkeypatch.setattr(reporting,'table',lambda df,*args:tables.append(df.copy()))
    frame=pd.DataFrame({'common_id':['001','002','003'],'water_network_ratio_2010':[.1,.5,float('nan')],
                        'water_network_ratio_2022':[.2,.6,.8],'water_network_ratio_change_pp':[10,10,float('nan')]})
    before=frame.copy(deep=True)
    reporting.indicator_view(None,frame,'water_network')
    assert tables[0]['Median across areas'].tolist()==[30,60]
    assert tables[0]['Unavailable areas'].tolist()==[1,0]
    assert tables[1].common_id.tolist()==['001','002','003']
    pd.testing.assert_frame_equal(tables[1],frame)
    pd.testing.assert_frame_equal(frame,before)


def test_duplicate_legacy_cells_do_not_repeat_results(tmp_path,monkeypatch):
    from types import SimpleNamespace
    path=tmp_path/'code/config';path.mkdir(parents=True)
    entry={'stage':'ibama','artifact':'report','chunk_label':'libraries'}
    (path/'report_chunks.json').write_text(json.dumps({'old':[entry]}))
    ctx=SimpleNamespace(root=tmp_path,_report_presented={('ibama','report')})
    output=[];monkeypatch.setattr(reporting,'markdown',output.append)
    reporting.show_chunk(ctx,'old',1)
    assert output==['<!-- Saved result already presented; original cell retained for traceability. -->']


def test_foreign_scope_does_not_load_belo_horizonte_example(monkeypatch):
    from types import SimpleNamespace
    notes=[];monkeypatch.setattr(reporting,'markdown',notes.append)
    reporting.overview_example(SimpleNamespace(municipality='3550308'),'310620025610001')
    assert 'omitted outside that municipality' in notes[0]


def test_indicator_figure_uses_available_units_and_scoped_path(tmp_path,monkeypatch):
    from types import SimpleNamespace
    outputs=[]
    monkeypatch.setattr(reporting,'table',lambda *args:None)
    monkeypatch.setattr(reporting,'markdown',lambda *args:None)
    def capture(ctx,name,fig,caption):
        outputs.append((name,fig.axes[0].get_ylabel(),caption))
        import matplotlib.pyplot as plt
        plt.close(fig)
    monkeypatch.setattr(reporting,'figure',capture)
    frame=pd.DataFrame({'common_id':['1','2'],'black_ratio_2010':[.1,.2],'black_ratio_2022':[.2,.3],'black_ratio_change_pp':[10,10]})
    reporting.indicator_view(SimpleNamespace(root=tmp_path,municipality='3106200'),frame,'black')
    assert outputs[0][0:2]==('indicator_black','%')
    assert 'not a paired causal comparison' in outputs[0][2]


def test_coverage_reads_final_income_changes_not_legacy_counter(tmp_path):
    root=Path(__file__).resolve().parents[2]
    text=(root/'research/reports/ibge_census_temporal_comparison.md').read_text()
    code=report_engine.parse_report(text)[0][0][2]
    config=tmp_path/'project.toml';config.write_text('[project]\nroot="."\nmunicipality=""\n[census]\nrecompute_harmonisation=false\n')
    ctx=report_engine.context(config)
    folder=ctx.intermediate/'indicators';folder.mkdir(parents=True)
    (folder/'report.json').write_text(json.dumps({'income':{'common_areas':2,'missing_change':0}}))
    pd.DataFrame({'income_change_brl':[10,float('nan')]}).to_parquet(folder/'income.parquet')
    source='<!-- brazil:cell coverage -->\n```python\n'+code+'\n```\n\n<!-- brazil:output coverage begin -->\nold\n<!-- brazil:output coverage end -->\n'
    staging=tmp_path/'staging';staging.mkdir()
    rendered,_=report_engine.execute_cells(ctx,source,staging)
    assert '<td>Income</td>' in rendered and '<td>1</td>' in rendered
    assert 'legacy income missingness counter is not final coverage' in rendered
    assert '"missing_change": 0' in rendered
