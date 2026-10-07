"""Execute marked Markdown cells and publish only their generated result sections."""
import argparse
import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint

OBRAS_FLOW = ('obrasgov-snapshot', 'obrasgov-location-qa', 'obrasgov-location-plot',
              'obrasgov-primary-state-check', 'obrasgov-primary-state-filter')
REPORTS = {
    'brazil_poroject_charts': ('charts',),
    'ibama_data_extraction': ('ibama',),
    'ibge_census_data_extraction': ('census-exploration',),
    'ibge_census_temporal_comparison': ('indicators',),
    'ibge_census_tract_harmonisation': ('harmonisation',),
    'ibge_dataset_overview': ('overview',),
    'obrasgov_data_extraction': OBRAS_FLOW,
    'obrasgov_preprocessing': OBRAS_FLOW,
    'property_value': ('land-value',),
}
SCOPED = {'brazil_poroject_charts', 'ibge_census_temporal_comparison',
          'ibge_census_tract_harmonisation', 'ibge_dataset_overview'}
CELL = re.compile(r'^<!-- brazil:cell ([a-zA-Z0-9_]+) -->\n```python\n(.*?)^```\s*$', re.M | re.S)
OUTPUT = re.compile(r'^<!-- brazil:output ([a-zA-Z0-9_]+) begin -->\n(.*?)^<!-- brazil:output \1 end -->$', re.M | re.S)


def parse_report(text):
    cells = list(CELL.finditer(text)); outputs = list(OUTPUT.finditer(text))
    ids = [m[1] for m in cells]
    if not ids or len(set(ids)) != len(ids) or ids != [m[1] for m in outputs]:
        raise WorkflowError('Report requires unique ordered cells and matching output sections.')
    markers = re.findall(r'^.*<!--\s*brazil:[^\n]*$', text, re.M)
    if len(markers) != len(cells) * 3:
        raise WorkflowError('Malformed or unmatched report marker.')
    previous = -1
    for cell, output in zip(cells, outputs):
        if not previous < cell.start() < cell.end() < output.start():
            raise WorkflowError('Cell and output sections must be sequential and non-nested.')
        previous = output.end()
        compile(cell[2], '<report:'+cell[1]+'>', 'exec')
    return cells, outputs


def authored_text(text):
    """Invariant tested independently of computed result values."""
    parse_report(text)
    return OUTPUT.sub(lambda m: '<!-- brazil:output '+m[1]+' begin -->\n<!-- brazil:output '+m[1]+' end -->', text)


def effective_config(ctx):
    raw = json.dumps({'config': ctx.config, 'municipality': ctx.municipality}, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()


def code_hashes(root):
    paths = list((root/'code/brazil_project').rglob('*.py'))
    paths += list((root/'code/scripts/r').glob('*.R')) + list((root/'code/config').glob('*.json'))
    paths += [root/'code/scripts'/n for n in ('plot_location_qa.py','check_obras_primary_state.py','filter_obras_primary_state.py')]
    return {str(p.relative_to(root)): fingerprint(p) for p in paths if p.is_file()}


def stamp_producer(ctx, stage, status='completed', inputs=None, outputs=None):
    path = ctx.artifact(stage, 'producer.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {'stage': stage, 'status': status, 'effective_config': effective_config(ctx),
              'config_sha256': fingerprint(ctx.config_path), 'municipality': ctx.municipality,
              'code': code_hashes(ctx.root), 'inputs': inputs or {}, 'outputs': outputs or {}}
    tmp=path.with_suffix('.tmp.json');tmp.write_text(json.dumps(record,indent=2)+'\n');tmp.replace(path)


def require_producers(ctx, name):
    for stage in REPORTS[name]:
        path=ctx.require(ctx.artifact(stage,'producer.json'))
        record=json.loads(path.read_text())
        for relative, expected in {**record.get('inputs', {}), **record.get('outputs', {})}.items():
            if fingerprint(Path(relative)) != expected: raise WorkflowError('Producer input/output changed: '+relative)
        partial = stage=='land-value' and record.get('status')=='exploratory_partial'
        if (record.get('status')!='completed' and not partial) or record.get('effective_config')!=effective_config(ctx) or record.get('code')!=code_hashes(ctx.root):
            raise WorkflowError(f'Saved {stage} provenance does not match this configuration/code. Run processing first.')


def context(config, municipality=None, recompute=False):
    ctx=Context(config)
    if municipality is not None: ctx.municipality=municipality
    if recompute: ctx.config['census']['recompute_harmonisation']=True
    if ctx.municipality:
        ctx.intermediate=ctx.intermediate/('municipality_'+ctx.municipality)
    return ctx


def execute_cells(ctx, text, staging):
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    from IPython.display import display, Image
    cells, outputs=parse_report(text)
    shell=InteractiveShell.instance()
    inputs={str(ctx.config_path): fingerprint(ctx.config_path)}
    original_require=ctx.require
    def require(path):
        path=original_require(path).resolve()
        if str(path) not in inputs: inputs[str(path)]=fingerprint(path)
        return path
    ctx.require=require
    def report_file(relative):
        return json.loads(ctx.require(ctx.root/relative).read_text())
    def report_json(stage):
        return json.loads(ctx.require(ctx.artifact(stage,'report.json')).read_text())
    def report_image(relative):
        display(Image(filename=str(ctx.require(ctx.root/relative))))
    shell.user_ns.update({'ctx':ctx,'project':ctx.root,'display':display,
                          'report_file':report_file,'report_json':report_json,'report_image':report_image})
    figures={}; sections={}; stderr=[]
    for cell in cells:
        with capture_output() as captured:
            result=shell.run_cell(cell[2], store_history=False)
        if result.error_before_exec or result.error_in_exec:
            raise WorkflowError(f'{cell[1]} failed: {result.error_before_exec or result.error_in_exec}')
        fragments=[]
        if captured.stdout.strip(): fragments.append('```text\n'+captured.stdout.rstrip()+'\n```')
        stderr.append(captured.stderr[-2000:])
        for rich in captured.outputs:
            data=rich.data
            if 'image/png' in data:
                raw=data['image/png'];raw=base64.b64decode(raw) if isinstance(raw,str) else raw
                if len(raw)>5*1024*1024 or not raw.startswith(b'\x89PNG\r\n\x1a\n'):
                    raise WorkflowError('Report image is not a bounded PNG.')
                digest=hashlib.sha256(raw).hexdigest();name=digest+'.png'
                (staging/name).write_bytes(raw);figures[name]=digest
                fragments.append(f'![Generated figure](assets/{name})')
            elif 'text/markdown' in data: fragments.append(data['text/markdown'])
            elif 'text/html' in data:
                html=re.sub(r'<style\b[^>]*>.*?</style>','',data['text/html'],flags=re.S)
                fragments.append(re.sub(r'^</?div>\s*$','',html,flags=re.M))
            elif 'text/plain' in data: fragments.append('```text\n'+data['text/plain']+'\n```')
        sections[cell[1]]='\n\n'.join(fragments) or '_No displayed output._'
    rendered=OUTPUT.sub(lambda m: '<!-- brazil:output '+m[1]+' begin -->\n'+sections[m[1]]+'\n<!-- brazil:output '+m[1]+' end -->',text)
    if len(rendered.encode())>1024*1024 or re.search(r'<(?:script|iframe)\b',rendered,re.I):
        raise WorkflowError('Report contains an interactive or oversized output.')
    if authored_text(rendered)!=authored_text(text): raise WorkflowError('Authored report content changed.')
    return rendered, {'inputs':inputs,'figures':figures,'stderr':stderr,'cells':[c[1] for c in cells]}


@contextmanager
def report_lock(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    try: fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        raise WorkflowError('Report is locked. If an interrupted process has exited, remove '+str(path))
    try:
        os.write(fd,str(os.getpid()).encode());os.close(fd);yield
    finally: path.unlink(missing_ok=True)


def scoped_links(text, source, destination):
    from urllib.parse import unquote
    def replace(m):
        target=m[1]
        if target.startswith(('assets/','#')) or re.match(r'^[\w+.-]+:',target): return m[0]
        link,sep,anchor=target.partition('#')
        resolved=(source.parent/unquote(link)).resolve()
        return ']('+os.path.relpath(resolved,destination.parent)+(sep+anchor if sep else '')+')'
    # Rebase relative authored links; generated assets remain beside the scoped copy.
    return re.sub(r'\]\(([^)]+)\)',replace,text)


def render_report(ctx, name):
    if name not in REPORTS: raise WorkflowError('Unknown report: '+name)
    if ctx.municipality and name not in SCOPED: raise WorkflowError('Report is national-only: '+name)
    source=ctx.root/'research/reports'/(name+'.md')
    text=ctx.require(source).read_text();parse_report(text)
    source_sha=fingerprint(source);code=code_hashes(ctx.root)
    destination=source if not ctx.municipality else ctx.root/'outputs/reports'/('municipality_'+ctx.municipality)/source.name
    scope=ctx.municipality or 'national'
    cache=ctx.root/'.cache/report-render';cache.mkdir(parents=True,exist_ok=True)
    with report_lock(ctx.root/'.cache/report-locks'/(name+'-'+scope+'.lock')):
        require_producers(ctx,name)
        with tempfile.TemporaryDirectory(dir=cache) as temporary:
            staging=Path(temporary);(staging/'source.md').write_text(text)
            command=[sys.executable,'-m','brazil_project.report_engine','--worker',name,'--config',str(ctx.config_path),'--staging',str(staging)]
            if ctx.municipality: command += ['--municipality',ctx.municipality]
            if ctx.config['census']['recompute_harmonisation']: command+=['--recompute']
            env={**os.environ,'BRAZIL_REPORT_FORMAT':'gfm','MPLCONFIGDIR':str(ctx.root/'.cache/matplotlib'),'IPYTHONDIR':str(ctx.root/'.cache/ipython')}
            result=subprocess.run(command,cwd=ctx.root,env=env,capture_output=True,text=True)
            if result.returncode: raise WorkflowError(result.stderr[-4000:] or result.stdout[-4000:])
            payload=json.loads((staging/'evidence.json').read_text())
            rendered=(staging/'rendered.md').read_text()
            if fingerprint(source)!=source_sha or code_hashes(ctx.root)!=code:
                raise WorkflowError('Report source or implementation changed during execution; rerun.')
            for path,expected in payload['inputs'].items():
                if fingerprint(Path(path))!=expected: raise WorkflowError('Report input changed during execution: '+path)
            require_producers(ctx,name)
            if ctx.municipality: rendered=scoped_links(rendered,source,destination)
            destination.parent.mkdir(parents=True,exist_ok=True)
            for image,digest in payload['figures'].items():
                asset=destination.parent/'assets'/image
                asset.parent.mkdir(parents=True,exist_ok=True)
                if asset.exists() and fingerprint(asset)!=digest: raise WorkflowError('Report asset collision.')
                tmp=asset.with_suffix('.tmp.png');tmp.write_bytes((staging/image).read_bytes());tmp.replace(asset)
            generation=uuid.uuid4().hex
            evidence={**payload,'report':name,'generation':generation,'scope':scope,'configuration':ctx.config,
                      'effective_config':effective_config(ctx),'source_sha256':source_sha,'code':code,
                      'output':str(destination.relative_to(ctx.root)), 'output_sha256':hashlib.sha256(rendered.encode()).hexdigest(),
                      'authored_sha256':hashlib.sha256(authored_text(text).encode()).hexdigest()}
            # CONTRACT: Immutable evidence is staged first; the completion pointer
            # moves only after the atomic Markdown publication. Interrupted runs
            # are detectable through the prior pointer's output hash.
            record=ctx.root/'outputs/reports/evidence'/scope/name/generation
            record.mkdir(parents=True,exist_ok=True)
            (record/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
            tmp=destination.with_suffix('.tmp.md');tmp.write_text(rendered)
            if fingerprint(source)!=source_sha: raise WorkflowError('Source edited before publication; rerun.')
            tmp.replace(destination)
            pointer=record.parent/'current.json';tmp=pointer.with_suffix('.tmp.json')
            tmp.write_text(json.dumps({'status':'completed','generation':generation,'output_sha256':evidence['output_sha256']})+'\n');tmp.replace(pointer)
            return {'report':name,'status':'completed','generation':generation,'output':evidence['output'],'output_sha256':evidence['output_sha256'],'evidence':str((record/'evidence.json').relative_to(ctx.root))}


def main():
    p=argparse.ArgumentParser();p.add_argument('--worker',required=True);p.add_argument('--config',required=True)
    p.add_argument('--staging',type=Path,required=True);p.add_argument('--municipality');p.add_argument('--recompute',action='store_true');args=p.parse_args()
    ctx=context(args.config,args.municipality,args.recompute)
    rendered,evidence=execute_cells(ctx,(args.staging/'source.md').read_text(),args.staging)
    require_producers(ctx,args.worker)
    (args.staging/'rendered.md').write_text(rendered);(args.staging/'evidence.json').write_text(json.dumps(evidence))

if __name__=='__main__': main()
