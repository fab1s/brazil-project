"""Render genuine Quarto reports to HTML and reviewed GitHub Markdown previews."""
import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote

from brazil_project.io import WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint

ROOT = Path(__file__).resolve().parents[2]


class PreviewImage(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            attributes = dict(attrs)
            if not attributes.get('src'):
                raise WorkflowError('Rendered image has no source.')
            self.markdown = f"![{attributes.get('alt', 'Rendered code output')}]({attributes['src']})"


def export_preview(source, rendered, assets):
    """Copy only bounded Markdown/PNG outputs; preserve exact image bytes."""
    text = rendered.read_text()
    # WHY: Pandas embeds CSS in HTML tables; GitHub removes it. Keep the actual
    # rendered table values and remove only presentation wrappers.
    text = re.sub(r'<style\b[^>]*>.*?</style>', '', text, flags=re.S)
    text = re.sub(r'^</?div>\s*$', '', text, flags=re.M)
    # COMPATIBILITY: Quarto emits code-cell figures as multiline HTML img tags.
    # Convert them before resolving assets, or GitHub would receive broken paths.
    def html_image(match):
        parser = PreviewImage()
        parser.feed(match[0])
        return parser.markdown
    text = re.sub(r'<img\b[^>]*>', html_image, text, flags=re.I)
    images = []

    def image_link(match):
        target = unquote(match[2].strip('<>'))
        if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target):
            return match[0]
        candidates = [rendered.parent / target, source.parent / target]
        path = next((p.resolve() for p in candidates if p.is_file()), None)
        if path is None:
            raise WorkflowError('Missing rendered preview image: ' + target)
        if not path.is_relative_to(ROOT) or path.suffix.lower() != '.png':
            raise WorkflowError('Review nonlocal/non-PNG preview asset explicitly: ' + str(path))
        if path.stat().st_size > 5 * 1024 * 1024:
            raise WorkflowError('Preview image exceeds reviewed small-artifact limit: ' + str(path))
        checksum = fingerprint(path)
        assets.mkdir(parents=True, exist_ok=True)
        destination = assets / (checksum[:16] + '.png')
        if destination.exists() and fingerprint(destination) != checksum:
            raise WorkflowError('Preview asset name collision.')
        shutil.copyfile(path, destination)
        images.append({'source': str(path.relative_to(ROOT)), 'preview': str(destination.relative_to(ROOT)), 'sha256': checksum})
        relative = os.path.relpath(destination, source.parent)
        return f'![{match[1]}]({relative})'

    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', image_link, text)
    text = text.replace('\n\n\n', '\n\n')
    title_end = text.find('\n')
    notice = f'\n\nRendered preview · [Editable Quarto source]({source.name}) · Generated from saved local artifacts; full datasets stay outside Git.\n'
    text = text[:title_end] + notice + text[title_end:]
    if len(text.encode()) > 1024 * 1024 or '<script' in text.lower() or '<iframe' in text.lower():
        raise WorkflowError('Preview contains an oversized or interactive output; use the HTML report.')
    destination = source.with_suffix('.md')
    temporary = destination.with_suffix('.md.tmp')
    temporary.write_text(text)
    temporary.replace(destination)
    return {'source': str(source.relative_to(ROOT)), 'source_sha256': fingerprint(source),
            'preview': str(destination.relative_to(ROOT)), 'preview_sha256': fingerprint(destination), 'images': images}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', help='Optional report filename stem; default renders all reports.')
    args = parser.parse_args()
    local = ROOT / '.cache/quarto/bin/quarto'
    quarto = str(local) if local.is_file() else shutil.which('quarto')
    if not quarto:
        raise WorkflowError('Install Quarto: https://quarto.org/docs/get-started/')
    sources = sorted((ROOT / 'research/notebooks').glob('*.qmd'))
    if args.only:
        sources = [path for path in sources if path.stem == args.only]
    if not sources:
        raise WorkflowError('No matching research report.')
    env = {**os.environ, 'QUARTO_PYTHON': sys.executable, 'MPLCONFIGDIR': str(ROOT / '.cache/matplotlib')}
    records = []
    for source in sources:
        for output_format in ('gfm', 'html'):
            print(f'Rendering {source.name}: {output_format}', flush=True)
            subprocess.run([quarto, 'render', str(source), '--to', output_format, '--execute-daemon', '0'],
                           cwd=ROOT, env={**env, 'BRAZIL_REPORT_FORMAT': output_format}, check=True)
            if output_format == 'gfm':
                # INVARIANT: Quarto replaces per-source figure folders when
                # switching formats. Export GFM images before HTML rendering.
                rendered = ROOT / 'outputs/reports/research/notebooks' / source.with_suffix('.md').name
                record = export_preview(source, rendered, ROOT / 'research/notebooks/assets')
        rendered = ROOT / 'outputs/reports/research/notebooks' / source.with_suffix('.md').name
        html = rendered.with_suffix('.html')
        if not html.is_file():
            raise WorkflowError('HTML report was not produced: ' + str(html))
        record['html'] = str(html.relative_to(ROOT))
        record['html_sha256'] = fingerprint(html)
        records.append(record)
    evidence = ROOT / 'docs/evidence/report-previews.json'
    # CONTRACT: Partial refreshes replace only the corresponding records.
    previous = json.loads(evidence.read_text()).get('reports', []) if evidence.exists() else []
    refreshed = {row['source']: row for row in records}
    refreshed.update({row['source']: row for row in previous if row['source'] not in refreshed})
    payload = {'status': 'completed', 'quarto_version': subprocess.check_output([quarto, '--version'], text=True).strip(),
               'script_sha256': fingerprint(Path(__file__)), 'reports': sorted(refreshed.values(), key=lambda row: row['source'])}
    temporary = evidence.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(payload, indent=2) + '\n')
    temporary.replace(evidence)
    print(f'Rendered {len(records)} reports; GitHub previews are beside their Quarto sources.', flush=True)


if __name__ == '__main__':
    main()
