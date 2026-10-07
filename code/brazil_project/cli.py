"""Run analytical stages and their executable Markdown reports with shared context."""
import argparse
from datetime import datetime, timezone
import json
import os
import sys
from brazil_project.io import WorkflowError
from brazil_project.report_engine import (REPORTS, SCOPED, OBRAS_FLOW, context,
                                          render_report, stamp_producer, code_hashes)
from brazil_project.infrastructure.location_qa import fingerprint

STAGES = ('overview','census-exploration','harmonisation','indicators','ibama','obrasgov','land-value','charts')
INDIVIDUAL = OBRAS_FLOW
DEPENDENCIES = {'indicators':['harmonisation'], 'charts':['harmonisation','indicators'],
                'obrasgov-location-qa':['obrasgov-snapshot'],
                'obrasgov-location-plot':['obrasgov-location-qa'],
                'obrasgov-primary-state-check':['obrasgov-location-plot'],
                'obrasgov-primary-state-filter':['obrasgov-primary-state-check']}
ACQUISITION=('acquire-census','acquire-ibama','acquire-obrasgov')


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
    elif stage in ('ibama','obrasgov-snapshot'):
        from brazil_project.infrastructure.projects import run
        return run(ctx,'obrasgov' if stage=='obrasgov-snapshot' else stage)
    elif stage=='obrasgov-location-qa':
        from brazil_project.infrastructure.location_qa import run
    elif stage=='obrasgov-location-plot':
        from scripts.plot_location_qa import run
    elif stage=='obrasgov-primary-state-check':
        from scripts.check_obras_primary_state import run
    elif stage=='obrasgov-primary-state-filter':
        from scripts.filter_obras_primary_state import run
    elif stage=='acquire-census':
        from brazil_project.acquisition.census import run
    elif stage in ('acquire-ibama','acquire-obrasgov'):
        from brazil_project.acquisition.infrastructure import run
        return run(ctx,stage.removeprefix('acquire-'))
    else: raise WorkflowError('Unknown stage: '+stage)
    return run(ctx)


def expand(stages):
    ordered=[]
    def add(stage):
        if stage=='obrasgov': stage=OBRAS_FLOW[-1]
        for dep in DEPENDENCIES.get(stage,[]): add(dep)
        if stage not in ordered: ordered.append(stage)
    for stage in stages: add(stage)
    return ordered


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run');run.add_argument('stage',choices=(*STAGES,*INDIVIDUAL,*ACQUISITION,'all'))
    report=sub.add_parser('report');report.add_argument('name',choices=(*REPORTS,'all'));report.add_argument('--from-saved',action='store_true')
    cache=sub.add_parser('import-cache');cache.add_argument('cache')
    check=sub.add_parser('verify-parity')
    for command in (run,report,cache,check):
        command.add_argument('--config',default='project.toml');command.add_argument('--municipality')
        command.add_argument('--recompute-harmonisation',action='store_true')
    args=parser.parse_args(argv)
    ctx=context(args.config,args.municipality,args.recompute_harmonisation)
    if ctx.municipality and (len(ctx.municipality)!=7 or not ctx.municipality.isdigit()): parser.error('municipality must be a seven-digit IBGE code')
    os.environ.setdefault('MPLCONFIGDIR',str(ctx.root/'.cache/matplotlib'))
    try:
        if args.command=='import-cache':
            from pathlib import Path
            from brazil_project.acquisition.census import import_cache
            print(json.dumps(import_cache(ctx,Path(args.cache)),indent=2));return 0
        if args.command=='verify-parity':
            from brazil_project.verification import verify
            evidence=verify(ctx);print(json.dumps(evidence,indent=2));return 0 if evidence['passed'] else 1
        requested_reports=list(REPORTS) if args.command=='report' and args.name=='all' else [args.name] if args.command=='report' else []
        if args.command=='report':
            roots=[s for name in requested_reports for s in REPORTS[name]]
        else: roots=STAGES if args.stage=='all' else [args.stage]
        stages=[] if getattr(args,'from_saved',False) else expand(roots)
        if args.command=='run': requested_reports=[n for n,deps in REPORTS.items() if set(deps).intersection(stages)]
        # INVARIANT: Reject unsupported scope before any stage writes outputs.
        if ctx.municipality and any(n not in SCOPED for n in requested_reports):
            raise WorkflowError('Requested workflow includes national-only reports; omit --municipality or select a supported census/chart stage.')
        evidence=[];outcomes={};reports=[]
        for stage in stages:
            blocked=[d for d in DEPENDENCIES.get(stage,[]) if outcomes.get(d)!='completed']
            if blocked:
                outcomes[stage]='blocked';evidence.append({'stage':stage,'status':'blocked','error':'Dependencies failed: '+', '.join(blocked)});continue
            print('Running '+stage,flush=True)
            row={'stage':stage,'started_at':datetime.now(timezone.utc).isoformat()}
            original_require=ctx.require;original_write=ctx.write_table;original_report=ctx.report
            inputs={};outputs={};implementation=code_hashes(ctx.root)
            def observed(path):
                path=original_require(path).resolve()
                if str(path) not in inputs: inputs[str(path)]=fingerprint(path)
                return path
            def written(frame, producer, name):
                path=original_write(frame,producer,name);outputs[str(path.resolve())]=fingerprint(path);return path
            def reported(producer, payload):
                result=original_report(producer,payload);path=ctx.artifact(producer,'report.json');outputs[str(path.resolve())]=fingerprint(path);return result
            ctx.require=observed;ctx.write_table=written;ctx.report=reported
            try:
                result=dispatch(ctx,stage)
                for path,digest in inputs.items():
                    if fingerprint(__import__('pathlib').Path(path))!=digest: raise WorkflowError('Processing input changed: '+path)
                if code_hashes(ctx.root)!=implementation: raise WorkflowError('Implementation changed during processing; rerun.')
                # Capture direct script/map/figure outputs in addition to Context writes.
                directories=[]
                if stage=='harmonisation': directories=[ctx.intermediate/'harmonisation/current.json']
                elif stage=='obrasgov-location-plot': directories=[ctx.root/'outputs/figures/obrasgov-location-qa/location-screening.png']
                elif stage=='obrasgov-primary-state-check': directories=[ctx.root/'outputs/tables/obrasgov-primary-state',ctx.root/'outputs/figures/obrasgov-location-qa/primary-state-check.png']
                elif stage=='obrasgov-primary-state-filter': directories=[ctx.root/'outputs/maps/obrasgov-primary-state-filter',ctx.root/'outputs/figures/obrasgov-location-qa/primary-state-filter.png']
                elif stage=='charts': directories=[ctx.root/'outputs/figures'/('municipality_'+ctx.municipality if ctx.municipality else 'brazil')]
                elif stage=='overview': directories=[ctx.root/'outputs/maps'/('municipality_'+ctx.municipality if ctx.municipality else 'overview')]
                elif stage=='ibama': directories=[ctx.root/'outputs/maps/ibama.html']
                elif stage=='census-exploration': directories=[ctx.root/'outputs/maps/black_ratio_2010_2022.html']
                for path in directories:
                    for output in list(path.rglob('*')) if path.is_dir() else [path]:
                        if output.is_file(): outputs[str(output.resolve())]=fingerprint(output)
                stamp_producer(ctx,stage,inputs=inputs,outputs=outputs)
                row.update(status='completed',result=result)
            except Exception as error:
                row.update(status='blocked' if isinstance(error,WorkflowError) else 'failed',error=str(error))
                # COMPATIBILITY: The original exploratory importer saves workbook
                # results before reporting absent exact cadastral inputs. Keep the
                # stage blocked; permit an explicit saved-output report with notice.
                partial=ctx.artifact('land-value','report.json')
                if stage=='land-value' and str(partial.resolve()) in outputs and isinstance(error,WorkflowError) and json.loads(partial.read_text()).get('status')=='exploratory':
                    stamp_producer(ctx,stage,status='exploratory_partial',inputs=inputs,outputs=outputs)
                print(stage+': '+str(error),file=sys.stderr)
            finally: ctx.require=original_require;ctx.write_table=original_write;ctx.report=original_report
            evidence.append(row);outcomes[stage]=row['status']
        for name in requested_reports:
            required=REPORTS[name]
            if stages and any(outcomes.get(s)!='completed' for s in required):
                reports.append({'report':name,'status':'blocked' if any(outcomes.get(s) in ('blocked','failed') for s in required) or args.command=='report' else 'skipped','error':'Required stages did not complete in this invocation.'});continue
            try:
                print('Updating report '+name,flush=True);reports.append(render_report(ctx,name))
            except Exception as error:
                reports.append({'report':name,'status':'failed','error':str(error)});print(name+': '+str(error),file=sys.stderr)
        ctx.report('runs',{'config':str(ctx.config_path),'municipality':ctx.municipality,
                          'recompute_harmonisation':ctx.config['census']['recompute_harmonisation'],
                          'stages':evidence,'reports':reports})
        return 1 if any(r['status'] not in ('completed','skipped') for r in evidence+reports) else 0
    except (WorkflowError,FileNotFoundError) as error:
        print(str(error),file=sys.stderr);return 1

if __name__=='__main__': raise SystemExit(main())
