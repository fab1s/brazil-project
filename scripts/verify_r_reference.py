"""Compare Python to completed fresh R reference exports for a municipality."""
import argparse
import json
import pandas as pd
from brazil_project.io import Context
from brazil_project.verification import compare_tables


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',default='config/project.toml')
    parser.add_argument('--municipality',default='3106200')
    args=parser.parse_args()
    ctx=Context(args.config);ctx.municipality=args.municipality
    ctx.intermediate=ctx.intermediate/('municipality_'+args.municipality)
    folder=ctx.intermediate/'r_reference'
    ctx.require(folder/'reference_status.txt')
    results={}
    for name in ['black','literacy','rudimentary_sanitation','water_network','waste_collection','sewer_septic','brown','black_brown','income','houses','village_condo','apartments','population_density']:
        candidate=folder/(name+'_change.csv')
        if not candidate.exists(): candidate=folder/(name+'_sf.csv')
        expected=pd.read_csv(ctx.require(candidate),dtype={'common_id':'string'})
        actual=ctx.table('indicators',name)
        results[name]=compare_tables(actual,expected,'common_id',rtol=1e-8 if name=='population_density' else 1e-9,atol=1e-7 if name=='population_density' else 1e-8)
    charts={}
    for name,original in [('paired_chart_data','chart_data'),('eligible_2022','chart_data_2022'),('year_summary','year_summary'),('income_box_data','income_box_data')]:
        actual=ctx.table('charts',name);expected=pd.read_csv(ctx.require(folder/(original+'.csv')),dtype={'common_id':'string'})
        for frame in (actual,expected):
            frame['_comparison_key']=frame['year'].astype(str)+'_'+frame['racial_quintile'].astype(str) if name=='year_summary' else frame.common_id.astype(str)+(('_'+frame.year.astype(str)) if 'year' in frame else '')
        charts[name]=compare_tables(actual,expected,'_comparison_key')
    cutoffs=json.loads(ctx.artifact('charts','report.json').read_text())['income_cutoffs']
    import numpy as np
    charts['income_cutoffs']={'passed':bool(np.allclose(cutoffs,pd.read_csv(folder/'income_cutoffs.csv').income_cutoff,rtol=1e-9,atol=1e-8))}
    report=ctx.report('verification-r',{'passed':all(v['passed'] for v in [*results.values(),*charts.values()]),'indicators':results,'charts':charts,'reference':'fresh original R calculations on complete groups intersecting Belo Horizonte'})
    print(json.dumps({k:v['passed'] for k,v in results.items()},indent=2))
    print('Charts:',{k:v['passed'] for k,v in charts.items()})
    if not report['passed']: raise SystemExit(1)

if __name__=='__main__':main()
