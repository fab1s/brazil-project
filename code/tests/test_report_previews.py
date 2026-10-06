from pathlib import Path
import base64
import pytest
from scripts import render_reports
from brazil_project.io import WorkflowError


def test_project_render_patterns_cover_actual_sources():
    root = Path(__file__).resolve().parents[2]
    import re
    patterns = re.findall(r'^    - (.+\.qmd)$', (root / '_quarto.yml').read_text(), re.M)
    selected = {path for pattern in patterns for path in root.glob(pattern)}
    actual = set((root / 'research/notebooks').glob('*.qmd'))
    assert selected == actual and actual
    for path in actual:
        header = path.read_text().split('---', 2)[1]
        assert 'editor: visual' in header
        assert 'jupyter: python3' in header
        assert 'html:' in header and 'gfm:' in header


def test_preview_preserves_values_and_exact_images(tmp_path, monkeypatch):
    monkeypatch.setattr(render_reports, 'ROOT', tmp_path)
    source = tmp_path / 'research/notebooks/report.qmd'; source.parent.mkdir(parents=True)
    source.write_text('---\ntitle: Report\n---\n')
    rendered = tmp_path / 'outputs/report.md'; rendered.parent.mkdir()
    png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6qxsAAAAASUVORK5CYII=')
    (rendered.parent / 'chart.png').write_bytes(png)
    rendered.write_text('# Report\n\n<style>hidden CSS</style>\n<div>\n\n| Count |\n| --- |\n| 2346 |\n\n![Actual output](chart.png)\n<img\nsrc="chart.png"\nalt="Code figure" />\n</div>\n')
    record = render_reports.export_preview(source, rendered, source.parent / 'assets')
    text = source.with_suffix('.md').read_text()
    assert '| 2346 |' in text and 'Actual output' in text
    assert '<style>' not in text and '<div>' not in text
    assert '<img' not in text and '![Code figure](assets/' in text
    assert len(record['images']) == 2
    assert (tmp_path / record['images'][0]['preview']).read_bytes() == png
    assert '[Editable Quarto source](report.qmd)' in text


@pytest.mark.parametrize('body', ['![Missing output](missing.png)', '<script>alert(1)</script>'])
def test_failed_preview_preserves_previous_document(tmp_path, monkeypatch, body):
    monkeypatch.setattr(render_reports, 'ROOT', tmp_path)
    source = tmp_path / 'report.qmd'; source.write_text('source')
    source.with_suffix('.md').write_text('previous reviewed preview')
    rendered = tmp_path / 'rendered.md'; rendered.write_text('# Report\n\n' + body)
    with pytest.raises(WorkflowError):
        render_reports.export_preview(source, rendered, tmp_path / 'assets')
    assert source.with_suffix('.md').read_text() == 'previous reviewed preview'
    assert not (tmp_path / 'assets').exists()


def test_render_exports_gfm_figures_before_html_replaces_them(tmp_path, monkeypatch):
    import json
    import shutil
    monkeypatch.setattr(render_reports, 'ROOT', tmp_path)
    monkeypatch.setattr(render_reports.sys, 'argv', ['render_reports.py'])
    monkeypatch.setattr(render_reports.shutil, 'which', lambda name: '/quarto')
    monkeypatch.setattr(render_reports.subprocess, 'check_output', lambda *a, **kw: '1.9.38')
    source = tmp_path / 'research/notebooks/report.qmd'
    source.parent.mkdir(parents=True)
    source.write_text('source')
    rendered_dir = tmp_path / 'outputs/reports/research/notebooks'
    rendered_dir.mkdir(parents=True)
    (tmp_path / 'docs/evidence').mkdir(parents=True)
    formats = []

    def render(command, **kwargs):
        output_format = command[command.index('--to') + 1]
        formats.append(output_format)
        figures = rendered_dir / 'report_files'
        if figures.exists():
            shutil.rmtree(figures)
        figures.mkdir()
        (figures / f'{output_format}.png').write_bytes(b'original figure bytes')
        if output_format == 'gfm':
            (rendered_dir / 'report.md').write_text('# Report\n\n<img src="report_files/gfm.png" />\n')
        else:
            (rendered_dir / 'report.html').write_text('<h1>Report</h1><img src="report_files/html.png">')

    monkeypatch.setattr(render_reports.subprocess, 'run', render)
    render_reports.main()
    assert formats == ['gfm', 'html']
    evidence = json.loads((tmp_path / 'docs/evidence/report-previews.json').read_text())
    row = evidence['reports'][0]
    assert (tmp_path / row['images'][0]['preview']).read_bytes() == b'original figure bytes'
    assert (rendered_dir / 'report_files/html.png').exists()
    assert not (rendered_dir / 'report_files/gfm.png').exists()
