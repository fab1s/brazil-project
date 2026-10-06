"""Execute Python report scripts into review copies; never overwrite research Markdown."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from brazil_project.io import WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint

ROOT = Path(__file__).resolve().parents[2]


def execute_script(script, destination):
    """Capture ordered rich outputs from a saved-artifact report in a fresh worker."""
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    if not destination.resolve().is_relative_to((ROOT / 'outputs/reports').resolve()):
        raise WorkflowError('Review copies must stay under outputs/reports; research Markdown is maintained by hand.')
    shell = InteractiveShell.instance()
    shell.user_ns['__file__'] = str(script)
    with capture_output() as captured:
        result = shell.run_cell(script.read_text(), store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise WorkflowError(f'{script.name}: {result.error_before_exec or result.error_in_exec}')
    sections = [f'# Saved outputs: {script.stem}\n',
                f'Review copy for [the maintained report](../../research/reports/{script.stem}.md). '
                'Generated from local artifacts; original datasets and report edits are unchanged.\n']
    images = []
    if captured.stdout.strip():
        sections.append('```text\n' + captured.stdout.rstrip() + '\n```\n')
    for output in captured.outputs:
        data = output.data
        if 'image/png' in data:
            raw = data['image/png']
            raw = base64.b64decode(raw) if isinstance(raw, str) else raw
            if len(raw) > 5 * 1024 * 1024:
                raise WorkflowError('Review figure exceeds the small-artifact limit.')
            import hashlib
            digest = hashlib.sha256(raw).hexdigest()
            image = destination.parent / 'assets' / (digest[:16] + '.png')
            image.parent.mkdir(parents=True, exist_ok=True)
            if image.exists() and fingerprint(image) != digest:
                raise WorkflowError('Review asset name collision.')
            image.write_bytes(raw)
            images.append({'path': str(image.relative_to(ROOT)), 'sha256': digest})
            sections.append(f'![Saved code output](assets/{image.name})\n')
        elif 'text/markdown' in data:
            sections.append(data['text/markdown'] + '\n')
        elif 'text/html' in data:
            # COMPATIBILITY: Keep table values; discard display-only pandas CSS.
            html = re.sub(r'<style\b[^>]*>.*?</style>', '', data['text/html'], flags=re.S)
            html = re.sub(r'^</?div>\s*$', '', html, flags=re.M)
            sections.append(html + '\n')
        elif 'text/plain' in data:
            sections.append('```text\n' + data['text/plain'] + '\n```\n')
    text = '\n'.join(sections)
    if len(text.encode()) > 1024 * 1024 or re.search(r'<(?:script|iframe)\b', text, re.I):
        raise WorkflowError('Review output contains an interactive or oversized artifact.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix('.md.tmp')
    temporary.write_text(text)
    temporary.replace(destination)
    return {'script': str(script.relative_to(ROOT)), 'script_sha256': fingerprint(script),
            'output': str(destination.relative_to(ROOT)), 'output_sha256': fingerprint(destination),
            'images': images, 'stderr': captured.stderr[-2000:]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', help='Report filename stem; default runs all nine scripts.')
    parser.add_argument('--worker', help=argparse.SUPPRESS)
    args = parser.parse_args()
    scripts = sorted((ROOT / 'code/reports').glob('*.py'))
    selected = args.worker or args.only
    if selected:
        scripts = [s for s in scripts if s.stem == selected]
    if not scripts:
        raise WorkflowError('No matching Python report script.')
    if args.worker:
        row = execute_script(scripts[0], ROOT / 'outputs/reports' / (scripts[0].stem + '.md'))
        print(json.dumps(row))
        return
    rows = []
    env = {**os.environ, 'BRAZIL_REPORT_FORMAT': 'gfm', 'MPLCONFIGDIR': str(ROOT / '.cache/matplotlib')}
    for script in scripts:
        # INVARIANT: No notebook session state is shared between reports.
        result = subprocess.run([sys.executable, str(Path(__file__)), '--worker', script.stem],
                                cwd=ROOT, env=env, check=True, capture_output=True, text=True)
        rows.append(json.loads(result.stdout))
        print('Generated review copy: ' + script.stem, flush=True)
    manifest = ROOT / 'outputs/reports/report-execution.json'
    previous = json.loads(manifest.read_text()).get('reports', []) if manifest.exists() else []
    records = {r['script']: r for r in previous}
    records.update({r['script']: r for r in rows})
    payload = {'status': 'completed', 'renderer_sha256': fingerprint(Path(__file__)),
               'reports': sorted(records.values(), key=lambda r: r['script'])}
    temporary = manifest.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(payload, indent=2) + '\n')
    temporary.replace(manifest)
    print('Review outputs under outputs/reports/. Copy reviewed results into research/reports/ when needed.')


if __name__ == '__main__':
    main()
