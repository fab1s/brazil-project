"""Verify project-authored Markdown metadata and local navigation links."""
from pathlib import Path
import re
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
paths=[ROOT/n for n in ['README.md','AGENTS.md','NOTICE.md']]
paths+=list((ROOT/'docs').rglob('*.md'))
paths+=[p for p in ROOT.rglob('README.md') if not any(part.startswith('.') or part in ['renv','archive','data','research','outputs','docs'] for part in p.relative_to(ROOT).parts)]
for folder in ["data", "outputs", "archive", "research"]:
    paths += list((ROOT / folder).glob("README.md"))
    paths += list((ROOT / folder).glob("*/README.md"))
errors=[]
for path in set(paths):
    if 'original_notes' in path.parts:continue
    text=path.read_text()
    if path != ROOT/'README.md':
        for key in ['Status:','Last updated:','Version:','Scope:']:
            if key not in text:errors.append(f'{path}: {key} missing')
    if path!=ROOT/'README.md' and '## Edit History' not in text:errors.append(f'{path}: edit history missing')
    if len(re.findall(r'^```',text,re.M))%2:errors.append(f'{path}: unmatched code fence')
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
        target=unquote(target.split('#')[0].strip('<>'))
        if target and not (path.parent/target).exists():errors.append(f'{path}: missing link {target}')
if errors:raise SystemExit('\n'.join(errors))
print(f'Checked {len(set(paths))} project Markdown files')
