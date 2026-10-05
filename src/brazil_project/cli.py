"""Explicit command line entry point with per-stage execution evidence."""
import argparse
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from brazil_project.io import Context, WorkflowError

STAGES = ('overview','census-exploration','harmonisation','indicators','ibama','obrasgov','land-value','charts')
DEPENDENCIES = {'indicators':['harmonisation'], 'charts':['harmonisation','indicators']}

def dispatch(ctx, stage):
    if stage=='census-exploration':
        from brazil_project.visualisation.census import run
    elif stage=='harmonisation':
        from brazil_project.harmonisation.census import run
    elif stage=='indicators':
        from brazil_project.indicators.temporal import run
    elif stage=='charts':
        from brazil_project.visualisation.charts import run
    elif stage=='land-value':
        from brazil_project.land_value.property import run
    elif stage=='overview':
        from brazil_project.harmonisation.overview import run
    elif stage in ('ibama','obrasgov'):
        from brazil_project.infrastructure.projects import run
        return run(ctx,stage)
    elif stage=='acquire-census':
        from brazil_project.acquisition.census import run
    elif stage in ('acquire-ibama','acquire-obrasgov'):
        from brazil_project.acquisition.infrastructure import run
        return run(ctx,stage.removeprefix('acquire-'))
    else:
        raise WorkflowError(f'Unknown stage: {stage}')
    return run(ctx)


def main(argv=None):
    parser=argparse.ArgumentParser(description='Brazil research workflow runner')
    sub=parser.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run')
    run.add_argument('stage',choices=(*STAGES,'all','acquire-census','acquire-ibama','acquire-obrasgov'))
    run.add_argument('--config',default='config/project.toml')
    run.add_argument('--municipality',help='Explicit validation/research subset; numeric IBGE municipality code')
    run.add_argument('--recompute-harmonisation',action='store_true')
    cache=sub.add_parser('import-cache')
    cache.add_argument('cache',type=Path)
    cache.add_argument('--config',default='config/project.toml')
    check=sub.add_parser('verify-parity')
    check.add_argument('--config',default='config/project.toml')
    check.add_argument('--municipality')
    args=parser.parse_args(argv)
    ctx=Context(args.config)
    os.environ.setdefault('MPLCONFIGDIR', str(ctx.root / '.cache/matplotlib'))
    if getattr(args,'municipality',None): ctx.municipality=args.municipality
    if ctx.municipality and (len(ctx.municipality)!=7 or not ctx.municipality.isdigit()): parser.error('municipality must be a seven-digit IBGE code')
    if getattr(args,'recompute_harmonisation',False): ctx.config['census']['recompute_harmonisation']=True
    # Scope-specific intermediates prevent subset results overwriting national artifacts.
    if ctx.municipality:
        ctx.intermediate=ctx.intermediate / ('municipality_'+ctx.municipality)
        ctx.intermediate.mkdir(parents=True,exist_ok=True)
    try:
        if args.command=='import-cache':
            from brazil_project.acquisition.census import import_cache
            print(json.dumps(import_cache(ctx,args.cache),indent=2))
            return 0
        if args.command=='verify-parity':
            from brazil_project.verification import verify
            report=verify(ctx)
            print(json.dumps(report,indent=2))
            return 0 if report['passed'] else 1
        requested=STAGES if args.stage=='all' else [args.stage]
        stages=[]
        def add(stage):
            for dep in DEPENDENCIES.get(stage,[]): add(dep)
            if stage not in stages: stages.append(stage)
        for stage in requested: add(stage)
        evidence=[]
        outcomes={}
        for stage in stages:
            failed_dependencies=[dep for dep in DEPENDENCIES.get(stage,[]) if outcomes.get(dep)!='completed']
            if failed_dependencies:
                evidence.append({'stage':stage,'status':'blocked','error':'Dependencies failed: '+', '.join(failed_dependencies)})
                outcomes[stage]='blocked'
                ctx.report(stage,evidence[-1])
                continue
            print('Running '+stage,flush=True)
            start=datetime.now(timezone.utc).isoformat()
            try:
                result=dispatch(ctx,stage)
                evidence.append({'stage':stage,'status':'completed','started_at':start,'result':result})
                outcomes[stage]='completed'
            except Exception as error:
                evidence.append({'stage':stage,'status':'blocked' if isinstance(error,WorkflowError) else 'failed','started_at':start,'error':str(error)})
                outcomes[stage]=evidence[-1]['status']
                ctx.report('runs',{'stages':evidence,'municipality':ctx.municipality})
                if args.stage!='all': raise
                print(f'{stage}: {error}',file=sys.stderr,flush=True)
        ctx.report('runs',{'config':str(ctx.config_path.relative_to(ctx.root)), 'municipality':ctx.municipality,
                           'recompute_harmonisation':ctx.config['census']['recompute_harmonisation'], 'stages':evidence})
        return 1 if any(s['status']!='completed' for s in evidence) else 0
    except (WorkflowError, FileNotFoundError) as error:
        print(str(error),file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
