"""Import existing censobr cache explicitly; optional isolated R acquisition."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import pandas as pd
from brazil_project.io import WorkflowError, keys

DATASETS = {2000: ['Basico'], 2010: ['Pessoa', 'Domicilio', 'ResponsavelRenda'],
            2022: ['Basico', 'Pessoas', 'Domicilio', 'ResponsavelRenda']}

def filename(year, dataset, release):
    return f'{year}_tracts_{dataset}_{release}.parquet'


def import_cache(ctx, cache):
    cache = Path(cache)
    target = ctx.path('census', 'tables')
    target.mkdir(parents=True, exist_ok=True)
    records = []
    for year, datasets in DATASETS.items():
        for dataset in datasets:
            name = filename(year, dataset, ctx.config['census']['release'])
            source = ctx.require(cache / name)
            checksum = hashlib.sha256(source.read_bytes()).hexdigest()
            dest = target / name
            if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() != checksum:
                raise WorkflowError(f'Cache differs from immutable input {dest}; use a new release directory')
            if not dest.exists():
                temp = dest.with_suffix('.copying')
                shutil.copy2(source, temp)
                if hashlib.sha256(temp.read_bytes()).hexdigest() != checksum:
                    raise WorkflowError(f'Cache copy mismatch: {source}')
                os.replace(temp, dest)
            records.append({'source': str(source), 'destination': str(dest.relative_to(ctx.root)), 'sha256': checksum})
    (target / 'provenance.json').write_text(json.dumps(records, indent=2) + '\n')
    return ctx.report('acquisition', {'cache_imported': len(records), 'network': False})


def run(ctx):
    if ctx.config['census']['release']!='v0.5.0':
        raise WorkflowError('The R acquisition adapter is locked to censobr v0.5.0. Update the adapter and renv lock together for another release.')
    runtime = shutil.which('Rscript')
    if runtime is None:
        raise WorkflowError('Install R and restore renv.lock, or import existing Parquet inputs with import-cache.')
    script = ctx.root / 'code/scripts/r/acquire_census.R'
    result = subprocess.run([runtime, str(script), str(ctx.root), str(ctx.path('census', 'tables'))], cwd=ctx.root, text=True)
    if result.returncode:
        raise WorkflowError('R acquisition failed. Run Rscript code/scripts/r/restore.R and review package/source availability.')
    for year, datasets in DATASETS.items():
        for dataset in datasets:
            path=ctx.require(ctx.path('census', 'tables') / filename(year, dataset, ctx.config['census']['release']))
            keys(pd.read_parquet(path,columns=['code_tract']),'code_tract')
    return ctx.report('acquisition', {'status': 'completed', 'adapter': 'censobr_R'})


def read(ctx, year, dataset, columns=None):
    path = ctx.require(ctx.path('census', 'tables') / filename(year, dataset, ctx.config['census']['release']))
    import pyarrow.parquet as pq
    import pyarrow as pa
    schema = pq.read_schema(path)
    filters = None
    lookup_path = ctx.artifact('harmonisation', f'lookup_{year}.parquet')
    requested = None
    if ctx.municipality and lookup_path.exists():
        requested = pd.read_parquet(lookup_path)[f'id_{year}'].dropna().unique().tolist()
        field = schema.field('code_tract').type
        values = requested if pa.types.is_string(field) else [int(v) for v in requested]
        filters = [('code_tract', 'in', values)]
    frame = pd.read_parquet(path, columns=columns, filters=filters)
    from brazil_project.io import identifiers
    frame['code_tract'] = identifiers(frame.code_tract)
    if ctx.municipality and requested is None:
        frame = frame[frame.code_tract.str.startswith(ctx.municipality)]
    return frame.reset_index(drop=True)
