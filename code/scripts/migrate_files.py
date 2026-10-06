"""Copy and hash the original research folder without modifying it."""
import argparse
import csv
import hashlib
import os
from pathlib import Path
import shutil

SOURCE = Path('/Users/fa4850sc/Library/CloudStorage/OneDrive-LundUniversity/Brazil Project')
ROOT = Path(__file__).resolve().parents[2]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def destination(rel):
    parts = rel.parts
    if any(p.startswith('.') or p.startswith('~$') for p in parts):
        return Path('data/archive/session_files') / rel, 'session'
    if rel.suffix.lower() in {'.qmd', '.r', '.rproj', '.bak'}:
        return Path('data/archive/original_code') / rel, 'original_code'
    if parts[0] == 'CS2Nordic' and rel.suffix.lower() in {'.docx', '.pptx', '.pdf'}:
        return Path('research/cs2nordic') / Path(*parts[1:]), 'research'
    if rel.suffix.lower() in {'.png', '.jpg', '.jpeg', '.html'}:
        return Path('data/archive/original_outputs') / rel, 'original_output'
    tail = Path(*parts[2:]) if len(parts) > 2 and parts[0] == 'Scripts_Data' else Path(*parts[1:])
    source = parts[1].lower().replace(' ', '_') if len(parts) > 2 and parts[0] == 'Scripts_Data' else 'ibge'
    if rel.suffix.lower() in {'.md', '.txt'}:
        return Path('data/archive/original_notes') / rel, 'reference_note'
    if rel.suffix.lower() in {'.pdf', '.xlsx'} or 'Questionairs and Codebooks' in parts:
        return Path('data/reference') / source / tail, 'reference_data'
    # Existing results are baselines, not newly validated outputs.
    category = 'processed' if rel.suffix.lower() == '.gpkg' and rel.name != 'ibge_census_tracts.gpkg' else 'raw'
    return Path('data') / category / source / tail, category

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    manifest = ROOT / 'docs/evidence/migration_manifest.csv'
    if args.verify_only:
        with manifest.open() as stream:
            rows = list(csv.DictReader(stream))
        failures = []
        for row in rows:
            for path in (SOURCE / row['original_path'], ROOT / row['destination']):
                # COMPATIBILITY: Simplification removed zero-byte session files;
                # their original source and empty checksum remain accounted for.
                if row['status']=='empty_removed_no_content' and path == ROOT / row['destination'] and not path.exists():
                    continue
                if not path.is_file() or digest(path) != row['sha256']:
                    failures.append(str(path))
        if failures:
            raise SystemExit('Verification failed: ' + '\n'.join(failures))
        print(f'Verified source and destination checksums for {len(rows)} files')
        return
    manifest.parent.mkdir(parents=True, exist_ok=True)
    seen = {}
    failed = []
    fields = ['original_path', 'destination', 'size_bytes', 'sha256', 'classification', 'duplicate_of', 'status']
    with manifest.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for index, path in enumerate(sorted(SOURCE.rglob('*'))):
            if not path.is_file():
                continue
            rel = path.relative_to(SOURCE)
            dest_rel, classification = destination(rel)
            dest = ROOT / dest_rel
            try:
                checksum = digest(path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists() and digest(dest) != checksum:
                    dest_rel = dest_rel.with_name(dest_rel.stem + '__' + checksum[:12] + dest_rel.suffix)
                    dest = ROOT / dest_rel
                if not dest.exists():
                    temp = dest.with_name(dest.name + '.copying')
                    shutil.copy2(path, temp)
                    if digest(temp) != checksum:
                        raise RuntimeError('Copied checksum mismatch')
                    os.replace(temp, dest)
                if digest(dest) != checksum:
                    raise RuntimeError('Destination checksum mismatch')
                writer.writerow(dict(original_path=str(rel), destination=str(dest_rel), size_bytes=path.stat().st_size,
                                     sha256=checksum, classification=classification, duplicate_of=seen.get(checksum, ''), status='verified'))
                seen.setdefault(checksum, str(rel))
                stream.flush()
            except Exception as error:
                failed.append((str(rel), str(error)))
                writer.writerow(dict(original_path=str(rel), destination=str(dest_rel), classification=classification, status=str(error)))
                stream.flush()
    print(f'Copied and verified {len(seen)} distinct file contents; {len(failed)} failures', flush=True)
    if failed:
        raise SystemExit(str(failed))

if __name__ == '__main__':
    main()
