#!/usr/bin/env python3
"""Preserve existing here.now assets before rebuilding census tiles; explicit network step."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import urllib.request


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slug',default='sandy-ivory-k65c')
    parser.add_argument('--output',type=Path,default=Path('outputs/maps/website'))
    parser.add_argument('--local-site',type=Path,help='Optional existing local snapshot; reuse only checksum-identical files.')
    args=parser.parse_args()
    key=os.environ.get('HERENOW_API_KEY')
    if not key:
        credentials=Path.home()/'.herenow/credentials'
        if credentials.exists(): key=credentials.read_text().strip()
    if not key: raise RuntimeError('Save a here.now API key in ~/.herenow/credentials or HERENOW_API_KEY.')
    base='https://here.now/api/v1/publish/'+args.slug
    headers={'Authorization':'Bearer '+key,'X-HereNow-Client':'codex/map-snapshot'}
    def fetch(url):
        if not url.startswith(base+'/'): raise RuntimeError('Unexpected site file URL')
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=180) as response:return response.read()
    manifest=json.loads(fetch(base+'/files'))
    for item in manifest['files']:
        name=item['path'];path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts: raise RuntimeError('Unsafe site asset path')
        # CONTRACT: Preserve project/community and legacy reference assets; rebuild active census archives.
        if name.startswith('data/social-') and name.endswith('.pmtiles'): continue
        target=args.output/name;target.parent.mkdir(parents=True,exist_ok=True)
        local=args.local_site/name if args.local_site else None
        if local and local.is_file() and local.stat().st_size==item['size'] and hashlib.sha256(local.read_bytes()).hexdigest()==item.get('hash'):
            shutil.copy2(local,target)
        else:target.write_bytes(fetch(item['url']))
        if item.get('hash') and hashlib.sha256(target.read_bytes()).hexdigest()!=item['hash']:raise RuntimeError('Asset checksum mismatch: '+name)
    report=Path('data/intermediate/website-snapshot/report.json');report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps({'slug':args.slug,'source_version':manifest['currentVersionId'],'files':[{k:f.get(k) for k in ('path','size','hash')} for f in manifest['files']]},indent=2)+'\n')
    print('Preserved existing assets from site version',manifest['currentVersionId'],'under',args.output)

if __name__=='__main__':main()
