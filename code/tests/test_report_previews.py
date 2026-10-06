import base64
import hashlib
import json
from pathlib import Path
import zipfile

import pytest
from scripts import render_reports
from brazil_project.io import WorkflowError


def test_markdown_reports_preserve_all_ordered_source_chunks():
    root = Path(__file__).resolve().parents[2]
    evidence = json.loads((root / 'docs/evidence/markdown-consolidation.json').read_text())
    assert len(evidence['reports']) == 9
    assert not list((root / 'research').rglob('*.qmd'))
    assert not (root / '_quarto.yml').exists()
    assert {r['report'] for r in evidence['reports']} == {str(p.relative_to(root)) for p in (root / 'research/reports').glob('*.md')}
    for row in evidence['reports']:
        script = (root / row['script']).read_text()
        compile(script, row['script'], 'exec')
        assert hashlib.sha256(script.encode()).hexdigest() == row['script_sha256']
        assert (root / row['report']).is_file()
        assert '.qmd)' not in (root / row['report']).read_text()
    # The prior commit preserves this archive's exact sources on GitHub as well.
    archive = root / evidence['archive']
    if archive.exists():
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == evidence['archive_sha256']
        with zipfile.ZipFile(archive) as z:
            for row in evidence['preserved_files']:
                assert hashlib.sha256(z.read(row['path'])).hexdigest() == row['sha256']
            import re
            for row in evidence['reports']:
                chunks = re.findall(r'^```\{python\}\n(.*?)^```\s*$', z.read(row['old_source']).decode(), re.M | re.S)
                script = (root / row['script']).read_text()
                cursor = 0
                for chunk in chunks:
                    cursor = script.index(chunk, cursor) + len(chunk)
                assert [hashlib.sha256(c.encode()).hexdigest() for c in chunks] == row['chunk_sha256']


def test_capture_preserves_tables_image_bytes_and_maintained_report(tmp_path, monkeypatch):
    monkeypatch.setattr(render_reports, 'ROOT', tmp_path)
    script = tmp_path / 'code/reports/report.py'; script.parent.mkdir(parents=True)
    report = tmp_path / 'research/reports/report.md'; report.parent.mkdir(parents=True)
    report.write_text('user narrative and findings')
    png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6qxsAAAAASUVORK5CYII=')
    script.write_text('from IPython.display import display, Image\nimport pandas as pd\ndisplay(pd.DataFrame({"Count": [2346]}))\ndisplay(Image(data=' + repr(png) + ', format="png"))\n')
    destination = tmp_path / 'outputs/reports/report.md'
    row = render_reports.execute_script(script, destination)
    assert '2346' in destination.read_text() and '<style' not in destination.read_text()
    assert (tmp_path / row['images'][0]['path']).read_bytes() == png
    assert report.read_text() == 'user narrative and findings'


@pytest.mark.parametrize('body', ['raise RuntimeError("missing input")', 'from IPython.display import display, HTML\ndisplay(HTML("<script>alert(1)</script>"))'])
def test_failed_refresh_preserves_previous_review_copy(tmp_path, monkeypatch, body):
    monkeypatch.setattr(render_reports, 'ROOT', tmp_path)
    script = tmp_path / 'report.py'; script.write_text(body)
    destination = tmp_path / 'outputs/reports/report.md'; destination.parent.mkdir(parents=True)
    destination.write_text('previous review')
    with pytest.raises(WorkflowError):
        render_reports.execute_script(script, destination)
    assert destination.read_text() == 'previous review'


def test_renderer_refuses_to_overwrite_maintained_markdown(tmp_path, monkeypatch):
    monkeypatch.setattr(render_reports, 'ROOT', tmp_path)
    script = tmp_path / 'report.py'; script.write_text('print("outputs")')
    destination = tmp_path / 'research/reports/report.md'
    with pytest.raises(WorkflowError, match='maintained by hand'):
        render_reports.execute_script(script, destination)
    assert not destination.exists()
