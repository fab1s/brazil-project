"""Verify project-authored Markdown metadata and local navigation links."""
from pathlib import Path
import re
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[2]
paths=[ROOT/n for n in ['README.md','AGENTS.md','NOTICE.md','code/README.md','data/README.md','outputs/README.md','research/README.md','website/README.md']]
paths+=list((ROOT/'docs').rglob('*.md'))
paths+=list((ROOT/'research/notebooks').glob('*.qmd'))
paths+=list((ROOT/'research/notebooks').glob('*.md'))
errors=[]
for path in set(paths):
    if 'original_notes' in path.parts:continue
    text=path.read_text()
    generated_preview = path.parent == ROOT/'research/notebooks' and path.suffix=='.md'
    if path != ROOT/'README.md' and path.suffix=='.md' and not generated_preview:
        for key in ['Status:','Last updated:','Version:','Scope:']:
            if key not in text:errors.append(f'{path}: {key} missing')
    if path!=ROOT/'README.md' and path.suffix=='.md' and not generated_preview and '## Edit History' not in text:errors.append(f'{path}: edit history missing')
    if len(re.findall(r'^```',text,re.M))%2:errors.append(f'{path}: unmatched code fence')
    # WHY: Verbatim legacy folder notes quote previous paths, not current links.
    if path.name=='folder-notes.md':
        text=text.split('<details>',1)[0]
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
        target=unquote(target.split('#')[0].strip('<>'))
        if target and not (path.parent/target).exists():errors.append(f'{path}: missing link {target}')
if errors:raise SystemExit('\n'.join(errors))
print(f'Checked {len(set(paths))} project Markdown files')
