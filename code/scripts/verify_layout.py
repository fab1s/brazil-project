"""Verify relocated files and recovery copies using the layout preservation ledger."""
import csv
import hashlib
import json
from pathlib import Path
import re
import zipfile

from brazil_project.infrastructure.location_qa import fingerprint
from brazil_project.io import WorkflowError

ROOT = Path(__file__).resolve().parents[2]


def archived_hash(archive, name):
    digest = hashlib.sha256()
    with archive.open(name) as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    with (ROOT / 'docs/evidence/layout-moves.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    notes = (ROOT / 'docs/folder-notes.md').read_text()
    working = sorted(p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith('.'))
    if working != ['code', 'data', 'docs', 'outputs', 'research', 'website']:
        raise WorkflowError('Unexpected visible working folders: ' + str(working))
    with zipfile.ZipFile(ROOT / 'data/archive/layout-before-2026-10-06.zip') as archive:
        for row in rows:
            path = ROOT / row['destination']
            # WHY: Python caches/installed-package metadata are derived runtime
            # files, not research documents; they may change after any execution.
            if row['preservation_kind'] == 'generated-runtime':
                continue
            if row['preservation_kind'] == 'empty-content':
                if row['size_bytes'] != '0' or row['original_sha256'] != hashlib.sha256(b'').hexdigest():
                    raise WorkflowError('Nonempty file incorrectly marked empty: ' + row['original_path'])
                continue
            if not path.is_file() or fingerprint(path) != row['current_sha256']:
                raise WorkflowError('Relocated file missing or changed since the layout audit: ' + str(path))
            if row['preservation_kind'] == 'verbatim-folder-notes':
                quoted = re.search(r'<details><summary>' + re.escape(row['original_path']) + r'</summary>\n\n````markdown\n(.*?)\n````', notes, re.S)
                if not quoted or hashlib.sha256(quoted[1].encode()).hexdigest() != row['original_sha256']:
                    raise WorkflowError('Consolidated document contents changed: ' + row['original_path'])
            elif row['preservation_kind'] == 'recovery-archive':
                if archived_hash(archive, row['original_path']) != row['original_sha256']:
                    raise WorkflowError('Recovery content differs: ' + row['original_path'])
            elif row['preservation_kind'] == 'unchanged-file':
                if row['current_sha256'] != row['original_sha256']:
                    raise WorkflowError('Unexplained content change: ' + row['original_path'])
            else:
                raise WorkflowError('Unknown preservation contract: ' + row['preservation_kind'])
    print(json.dumps({'verified_inventory_rows': len(rows), 'visible_working_folders': working,
                      'research_and_document_contents_preserved': True}, indent=2))


if __name__ == '__main__':
    main()
