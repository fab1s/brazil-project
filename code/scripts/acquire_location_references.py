"""Explicit acquisition of pinned geographic references for location QA."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import zipfile
import requests

SOURCES = {
    'municipalities': ('BR_Municipios_2022.zip', 'https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/BR_Municipios_2022.zip', 'IBGE municipal mesh 2022'),
    'land': ('ne_10m_land.zip', 'https://naturalearth.s3.amazonaws.com/5.1.1/10m_physical/ne_10m_land.zip', 'Natural Earth land 1:10m, 5.1.1'),
    'coastline': ('ne_10m_coastline.zip', 'https://naturalearth.s3.amazonaws.com/5.1.1/10m_physical/ne_10m_coastline.zip', 'Natural Earth ocean coastline 1:10m, release 5.1.1'),
}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def write_manifest(path, content):
    temporary = path.with_suffix('.tmp.json')
    temporary.write_text(json.dumps(content, indent=2)+'\n')
    temporary.replace(path)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=Path('data/reference/location-qa'))
    a = p.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
    manifest_path = a.output/'manifest.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest = {}
    for key, (name, url, description) in SOURCES.items():
        path = a.output/name
        if path.exists():
            if key not in previous or previous[key]['url'] != url or sha256(path) != previous[key]['sha256']:
                raise RuntimeError(f'Unverified existing reference: {path}; move it aside and reacquire explicitly.')
        else:
            temp = path.with_suffix('.partial')
            print('Downloading '+description, flush=True)
            with requests.get(url, stream=True, timeout=(30, 120)) as r:
                r.raise_for_status()
                with temp.open('wb') as f:
                    for block in r.iter_content(1024*1024):
                        f.write(block)
            with zipfile.ZipFile(temp) as z:
                if z.testzip() is not None:
                    raise RuntimeError('Corrupt reference archive: '+name)
            temp.replace(path)
        manifest[key] = {'path': name, 'url': url, 'description': description, 'sha256': sha256(path), 'bytes': path.stat().st_size,
                         'acquired_at': previous.get(key, {}).get('acquired_at', datetime.now(timezone.utc).isoformat())}
        # CONTRACT: Save each verified download so interruption does not lose provenance.
        write_manifest(manifest_path, {**previous, **manifest})
    print('Verified three local references; routine QA uses these without network access.')


if __name__ == '__main__':
    main()
