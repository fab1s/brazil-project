import base64
import hashlib
import json
from pathlib import Path
import re
import zipfile
import pytest
from brazil_project import report_engine as engine
from brazil_project.io import WorkflowError

NAME='brazil_poroject_charts'
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6qxsAAAAASUVORK5CYII=')

def cell(name, code):
    return f'<!-- brazil:cell {name} -->\n```python\n{code}\n```\n\n<!-- brazil:output {name} begin -->\nprevious result\n<!-- brazil:output {name} end -->\n'

@pytest.fixture
def project(tmp_path):
    config=tmp_path/'custom.toml';config.write_text('[project]\nroot="."\nmunicipality=""\n[census]\nrecompute_harmonisation=false\n[example]\nvalue=42\n')
    ctx=engine.context(config)
    source=tmp_path/'research/reports'/(NAME+'.md');source.parent.mkdir(parents=True)
    source.write_text('# Title\n\nAuthored explanation.\n\n'+cell('one','x = ctx.config["example"]["value"]\ndisplay(x)')+cell('two','display(x + 1)')+'\nCaption unchanged.\n')
    engine.stamp_producer(ctx,'charts')
    return ctx,source


def test_all_reports_preserve_archive_and_cell_order():
    root=Path(__file__).resolve().parents[2]
    ledger=json.loads((root/'docs/evidence/report-integration-migration.json').read_text())
    assert len(ledger['reports'])==len(engine.REPORTS)==9
    assert not (root/'code/reports').exists() and not list((root/'research').rglob('*.qmd'))
    for row in ledger['reports']:
        cells,_=engine.parse_report((root/row['report']).read_text())
        assert [m[1] for m in cells]==row['cell_ids']
        original_ids=[c['id'] for c in row['original_cells']]
        assert [m[1] for m in cells if m[1] in original_ids]==original_ids
        assert 'ctx = Context(' not in '\n'.join(c[2] for c in cells)
    archive=root/ledger['archive']
    if archive.exists():
        assert engine.fingerprint(archive)==ledger['archive_sha256']
        with zipfile.ZipFile(archive) as z:
            for row in ledger['files']:
                assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
            for row in ledger['reports']:
                script=z.read(row['retired_script']).decode()
                preservation=json.loads((root/'docs/evidence/report-readability-preservation.json').read_text())
                with zipfile.ZipFile(root/preservation['archive']) as prior:
                    current=prior.read(row['report']).decode()
                assert hashlib.sha256(current.encode()).hexdigest()==preservation['files'][row['report']]
                for match in re.finditer(r'^# %% \[markdown\]\n(.*?)(?=^# %%|\Z)',script,re.M|re.S):
                    lines=[]
                    for line in match[1].splitlines():
                        if line.startswith('# COMPATIBILITY:'): break
                        if line.startswith('# '):lines.append(line[2:])
                        elif line=='#':lines.append('')
                        elif line.strip():break
                    prose='\n'.join(lines).strip()
                    if not prose or prose.startswith('---'):continue
                    prose=re.sub(r'!\[([^]]+)\]\([^)]*\)(?:\{[^}]*\})?',lambda m:m[1]+'.',prose)
                    assert re.sub(r'\s+',' ',prose) in re.sub(r'\s+',' ',current),row['report']


@pytest.mark.parametrize('transform',[
    lambda s:s.replace('brazil:output one end','brazil:output missing end'),
    lambda s:s+cell('one','display(1)'),
    lambda s:s.replace('brazil:cell one','brazil:cell invalid-id'),
    lambda s:s.replace('```python','```r',1),
    lambda s:s.replace('brazil:output one begin','brazil:output two begin'),
])
def test_invalid_markers_rejected_before_execution(transform):
    with pytest.raises((WorkflowError,SyntaxError)):engine.parse_report(transform(cell('one','display(1)')))


def test_success_preserves_authored_content_and_sequential_state(project):
    ctx,source=project;before=source.read_text()
    row=engine.render_report(ctx,NAME);after=source.read_text()
    assert engine.authored_text(before)==engine.authored_text(after)
    assert '\n42\n' in after and '\n43\n' in after
    assert row['status']=='completed'
    engine.render_report(ctx,NAME)
    assert source.read_text()==after
    assert json.loads((ctx.root/row['evidence']).read_text())['configuration']['example']['value']==42


def test_figures_and_table_values_are_exact(project):
    ctx,source=project
    source.write_text(cell('one','from IPython.display import Image\nimport pandas as pd\ndisplay(pd.DataFrame({"Count": [2346]}))\ndisplay(Image(data='+repr(PNG)+', format="png"))'))
    engine.render_report(ctx,NAME)
    assert '2346' in source.read_text()
    images=list((source.parent/'assets').glob('*.png'))
    assert len(images)==1 and images[0].read_bytes()==PNG


@pytest.mark.parametrize('code',['raise RuntimeError("failed processing output")','ctx.require(project / "missing.parquet")','from IPython.display import HTML\ndisplay(HTML("<iframe></iframe>"))'])
def test_failed_cell_leaves_previous_report_untouched(project,code):
    ctx,source=project;source.write_text(cell('one',code));before=source.read_bytes()
    with pytest.raises(WorkflowError):engine.render_report(ctx,NAME)
    assert source.read_bytes()==before


def test_configuration_and_input_changes_reject_stale_producer(project):
    ctx,source=project;before=source.read_bytes();raw=ctx.root/'input.txt';raw.write_text('old')
    engine.stamp_producer(ctx,'charts',inputs={str(raw):engine.fingerprint(raw)})
    raw.write_text('new')
    with pytest.raises(WorkflowError,match='Producer input/output changed'):engine.render_report(ctx,NAME)
    assert source.read_bytes()==before
    engine.stamp_producer(ctx,'charts');ctx.config['example']['value']=99
    with pytest.raises(WorkflowError,match='provenance'):engine.render_report(ctx,NAME)


def test_scoped_run_keeps_national_report_and_rebases_links(project):
    ctx,source=project;source.write_text(source.read_text()+'\n[Documentation](../../docs/index.md)\n');before=source.read_bytes()
    scoped=engine.context(ctx.config_path,'3106200');engine.stamp_producer(scoped,'charts')
    row=engine.render_report(scoped,NAME)
    assert source.read_bytes()==before
    copied=ctx.root/row['output'];assert 'municipality_3106200' in str(copied)
    assert '../../../docs/index.md' in copied.read_text()


def test_concurrent_edit_is_preserved_and_blocks_publication(project):
    ctx,source=project
    source.write_text(cell('one','(project / "research/reports/'+NAME+'.md").write_text("new user edit")'))
    with pytest.raises(WorkflowError,match='changed during execution'):engine.render_report(ctx,NAME)
    assert source.read_text()=='new user edit'


def test_concurrent_lock_rejected_and_released(tmp_path):
    path=tmp_path/'lock'
    with engine.report_lock(path):
        with pytest.raises(WorkflowError,match='locked'):
            with engine.report_lock(path):pass
    assert not path.exists()


def test_atomic_publication_failure_preserves_report(project,monkeypatch):
    ctx,source=project;before=source.read_bytes();original=Path.replace
    def fail(path,destination):
        if path.name.endswith('.tmp.md'):raise OSError('interrupted publication')
        return original(path,destination)
    monkeypatch.setattr(Path,'replace',fail)
    with pytest.raises(OSError):engine.render_report(ctx,NAME)
    assert source.read_bytes()==before
    assert not list((ctx.root/'outputs/reports/evidence').rglob('current.json'))


def test_workers_do_not_share_report_state(project):
    ctx,source=project;engine.render_report(ctx,NAME)
    source.write_text(cell('one','display(x)'))
    before=source.read_bytes()
    with pytest.raises(WorkflowError,match='not defined'):engine.render_report(ctx,NAME)
    assert source.read_bytes()==before


def test_input_change_during_execution_blocks_report(project):
    ctx,source=project;raw=ctx.root/'read.txt';raw.write_text('old')
    source.write_text(cell('one','p=ctx.require(project / "read.txt")\np.write_text("changed")\ndisplay(1)'))
    before=source.read_bytes()
    with pytest.raises(WorkflowError,match='input changed during execution'):engine.render_report(ctx,NAME)
    assert source.read_bytes()==before


def test_changed_saved_output_rejected(project):
    ctx,source=project;output=ctx.root/'result.txt';output.write_text('old')
    engine.stamp_producer(ctx,'charts',outputs={str(output):engine.fingerprint(output)})
    output.write_text('changed')
    with pytest.raises(WorkflowError,match='input/output changed'):engine.render_report(ctx,NAME)


def test_fresh_worker_generates_headless_matplotlib_figure(project):
    ctx,source=project
    source.write_text(cell('one','import matplotlib\nmatplotlib.use("Agg")\nimport matplotlib.pyplot as plt\nfrom IPython.display import Image\nfrom io import BytesIO\nfig, ax = plt.subplots()\nax.plot([0, 1], [2, 3])\nraw = BytesIO()\nfig.savefig(raw, format="png")\nplt.close(fig)\ndisplay(Image(data=raw.getvalue(), format="png"))'))
    row=engine.render_report(ctx,NAME)
    assert row['status']=='completed'
    assert '![Generated figure](assets/' in source.read_text()
