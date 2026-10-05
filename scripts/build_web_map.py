#!/usr/bin/env python3
"""Build here.now census tiles from the validated national common-area bundle."""
import argparse
import hashlib
import json
import shutil
import re
import sqlite3
import subprocess
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from brazil_project.harmonisation.census import load_bundle, sha256
from brazil_project.io import Context, WorkflowError, keys

REGIONS = {
    'north': ('11','12','13','14','15','16','17'),
    'northeast-west': ('21','22','23','24','25'),
    'northeast-east': ('26','27','28','29'),
    'minas-espirito-santo': ('31','32'), 'rio-de-janeiro': ('33',),
    'sao-paulo': ('35',), 'south': ('41','42','43'), 'centre-west': ('50','51','52','53'),
}
INDICATORS = {
    'population_density': ('Population density','Population','area','pop'),
    'black': ('Black population proportion','Population','pop','black_pop'),
    'brown': ('Brown population proportion','Population','pop','brown_pop'),
    'black_brown': ('Black + Brown population proportion','Population','pop','black_brown_pop'),
    'literacy': ('Literacy · ages 15+','Education','pop_15plus','literate_15plus'),
    'rudimentary_sanitation': ('Rudimentary sanitation','Basic services','households','rudimentary_sanitation_households'),
    'water_network': ('Water network','Basic services','households','water_network_households'),
    'waste_collection': ('Waste collection','Basic services','households','waste_collection_households'),
    'sewer_septic': ('Sewer / septic','Basic services','households','sewer_septic_households'),
    'houses': ('Houses proportion','Housing','households','houses'),
    'village_condo': ('Village / condominium houses proportion','Housing','households','village_condo'),
    'apartments': ('Apartments proportion','Housing','households','apartments'),
}


def common_shard(identifier):
    identifier = str(identifier)
    if identifier.isdigit(): return str(int(identifier)//10000)
    if re.fullmatch(r'g_[0-9a-f]{24}',identifier): return 'g-'+identifier[2:4]
    raise WorkflowError('Unsupported common-area identifier: '+identifier)


def measure_fields(ctx, common):
    result = common[['common_id','n_2010','n_2022','relationship','geometry']].copy()
    for key, (_, _, denominator, numerator) in INDICATORS.items():
        table = ctx.table('indicators', key); keys(table, 'common_id')
        if not set(table.common_id).issubset(set(common.common_id)):
            raise WorkflowError('Indicator membership differs from the active bundle: ' + key)
        fields = {'common_id': table.common_id}
        for year in (2010,2022):
            fields[f'{key}_{year}'] = table[f'{key}_{year}' if key == 'population_density' else f'{key}_ratio_{year}']
            fields[f'{key}_n{year}'] = table[f'pop_{year}' if key == 'population_density' else f'{numerator}_{year}']
            fields[f'{key}_d{year}'] = table['area_km2' if key == 'population_density' else f'{denominator}_{year}']
            # PRESENTATION: preserve unavailable/out-of-range map estimates, never clip them.
            valid = np.isfinite(fields[f'{key}_{year}']) & (fields[f'{key}_{year}'] >= 0)
            if key != 'population_density': valid &= fields[f'{key}_{year}'] <= 1
            for suffix in (str(year),'n'+str(year),'d'+str(year)):
                fields[f'{key}_{suffix}'] = fields[f'{key}_{suffix}'].where(valid)
        fields[f'{key}_change'] = table[f'{key}_change_pct' if key == 'population_density' else f'{key}_ratio_change_pp'].where(
            fields[f'{key}_2010'].notna() & fields[f'{key}_2022'].notna())
        result = result.merge(pd.DataFrame(fields), on='common_id', how='left', validate='one_to_one')
    income = ctx.table('indicators','income'); keys(income,'common_id')
    if not set(income.common_id).issubset(set(common.common_id)):
        raise WorkflowError('Income contains groups absent from the active bundle.')
    income_fields = income[['common_id','income_2010','income_2022','income_change_pct','income_change_brl']].rename(columns={'income_change_pct':'income_change'})
    for year in (2010,2022):
        for field, source in [('heads','heads_used'),('tracts_used','n_used'),('missing_weights','missing_weights'),('complete','complete')]:
            income_fields[f'income_{field}_{year}'] = income[f'{source}_{year}'].astype(float)
        income_fields[f'income_tracts_total_{year}'] = income[f'n_{year}_y']
    result = result.merge(income_fields,on='common_id',how='left',validate='one_to_one')
    return result


def aggregate(frame, key):
    density = key == 'population_density'
    annual = []
    valid = []
    for year in (2010,2022):
        mask = np.isfinite(frame[f'{key}_{year}']) & np.isfinite(frame[f'{key}_n{year}']) & (frame[f'{key}_d{year}'] > 0)
        valid.append(mask)
    def totals(mask, year):
        n = float(frame.loc[mask,f'{key}_n{year}'].sum()); d = float(frame.loc[mask,f'{key}_d{year}'].sum())
        return {'areas':int(mask.sum()),'numerator':n,'denominator':d,'percent': (1 if density else 100)*n/d if d>0 else None}
    annual = [totals(mask,year) for mask,year in zip(valid,(2010,2022))]
    paired = [totals(valid[0] & valid[1],year) for year in (2010,2022)]
    a,b = [p['percent'] for p in paired]
    if a is None or b is None: change = None
    elif density: change = 100*(b/a-1) if a>0 else None
    else: change = b-a
    return {'annual':annual,'paired':paired,'changePP':change}


def overview_metrics(metrics, members):
    joined = members.merge(pd.DataFrame(metrics.drop(columns='geometry')),on='common_id',validate='many_to_one')
    result = pd.DataFrame({'code_muni': sorted(members.code_muni.unique())}).set_index('code_muni')
    for key in INDICATORS:
        for year in (2010,2022):
            mask = np.isfinite(joined[f'{key}_{year}']) & (joined[f'{key}_d{year}'] > 0)
            totals = joined.loc[mask].groupby('code_muni')[[f'{key}_n{year}',f'{key}_d{year}']].sum()
            result = result.join(totals)
            result[f'{key}_{year}'] = result[f'{key}_n{year}'] / result[f'{key}_d{year}']
        result[f'{key}_change'] = 100*(result[f'{key}_2022']/result[f'{key}_2010'].where(result[f'{key}_2010']>0)-1) if key=='population_density' else 100*(result[f'{key}_2022']-result[f'{key}_2010'])
    return result.reset_index()


def tiles(source, destination, layer, sql, minimum, maximum, simplify=None):
    temporary = destination.with_name(destination.stem+'.tmp.pmtiles')
    if temporary.exists(): temporary.unlink()
    command = ['ogr2ogr','-f','PMTiles',str(temporary),str(source),'-nln','social','-dialect','SQLITE','-sql',sql,
               '-t_srs','EPSG:4326','-dsco',f'MINZOOM={minimum}','-dsco',f'MAXZOOM={maximum}',
               '-dsco','MAX_FEATURES=1000000','-dsco','MAX_SIZE=10000000']
    if simplify: command += ['-simplify',str(simplify)]
    subprocess.run(command,check=True); temporary.replace(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path('config/project.toml'))
    parser.add_argument('--output',type=Path,default=Path('outputs/maps/website'))
    parser.add_argument('--work',type=Path,default=Path('.cache/map-update/build'))
    parser.add_argument('--reuse-prepared',action='store_true',help='Resume tiles only after checking the prepared database input fingerprints.')
    args = parser.parse_args(); ctx = Context(args.config)
    if ctx.municipality: raise WorkflowError('The public map requires a national bundle, with municipality empty.')
    bundle, manifest = load_bundle(ctx,names=['comparison_geometry'])
    indicator_report = json.loads(ctx.require(ctx.artifact('indicators','report.json')).read_text())
    if indicator_report.get('harmonisation_version') != manifest['version']: raise WorkflowError('Rerun indicators for the current harmonisation bundle.')
    inputs = {key:sha256(ctx.artifact('indicators',key+'.parquet')) for key in [*INDICATORS,'income']}
    contract = {'harmonisation_version':manifest['version'],'indicator_checksums':inputs,'export_policy':'merged-common-area-v1'}
    args.work.mkdir(parents=True,exist_ok=True); args.output.mkdir(parents=True,exist_ok=True)
    data = args.output/'data'; data.mkdir(exist_ok=True)
    source = args.work/'social.gpkg'; prepared = args.work/'prepared.json'
    suffix = 'common' + hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()[:12]
    if args.reuse_prepared:
        evidence = json.loads(prepared.read_text())
        if evidence['contract'] != contract or evidence.get('database_sha256') != sha256(source): raise WorkflowError('Prepared map inputs or database changed; use a fresh work folder.')
    else:
        if source.exists(): raise WorkflowError('Use a fresh work folder or --reuse-prepared for an interrupted tile build.')
        common = bundle['common_geometry_2022']; metrics = measure_fields(ctx,common)
        members = bundle['lookup_2022'][['id_2022','common_id']].copy(); members['code_muni']=members.id_2022.str[:7]
        members = members[['common_id','code_muni']].drop_duplicates()
        references = bundle.pop('comparison_geometry'); references=references[references.common_id.notna()][['id_2022','geometry']].copy()
        references['code_muni']=references.id_2022.str[:7]
        del bundle
        print('Preparing merged polygon database',len(metrics),flush=True)
        metrics.to_file(source,layer='social',driver='GPKG')
        regions = members.assign(state=members.code_muni.str[:2])
        state_to_region={code:region for region,codes in REGIONS.items() for code in codes}
        regions['region']=regions.state.map(state_to_region)
        if regions.region.isna().any(): raise WorkflowError('A source state has no map region.')
        regions=regions[['common_id','region']].drop_duplicates()
        with sqlite3.connect(source) as db:
            regions.to_sql('region_members',db,index=False); db.execute('CREATE INDEX regions_idx ON region_members(region,common_id)')
            db.execute('CREATE UNIQUE INDEX common_idx ON social(common_id)')
        bounds_frame=metrics[['common_id','geometry']].to_crs(4326)
        bounds = pd.DataFrame(bounds_frame.bounds).assign(common_id=metrics.common_id.to_numpy())
        regional_bounds = regions.merge(bounds,on='common_id').groupby('region').agg(minx=('minx','min'),miny=('miny','min'),maxx=('maxx','max'),maxy=('maxy','max'))
        searches=data/'id-search'; searches.mkdir(exist_ok=True)
        for shard,part in bounds.assign(shard=bounds.common_id.map(common_shard)).groupby('shard'):
            (searches/f'common-{shard}.json').write_text(json.dumps({r.common_id:[r.minx,r.miny,r.maxx,r.maxy] for r in part.itertuples()}))
        reference_bounds=references.to_crs(4326).bounds.assign(id_2022=references.id_2022.to_numpy())
        reference_bounds=reference_bounds.groupby('id_2022').agg(minx=('minx','min'),miny=('miny','min'),maxx=('maxx','max'),maxy=('maxy','max')).reset_index()
        for shard,part in reference_bounds.groupby(reference_bounds.id_2022.str[:2]):
            (searches/f'tract-{shard}.json').write_text(json.dumps({r.id_2022:[r.minx,r.miny,r.maxx,r.maxy] for r in part.itertuples()}))
        del bounds_frame,reference_bounds
        print('Preparing weighted municipality overview',flush=True)
        references.geometry=shapely.make_valid(shapely.simplify(references.geometry.array,500,preserve_topology=True))
        overview=references[['code_muni','geometry']].dissolve(by='code_muni',as_index=False)
        overview=overview.merge(overview_metrics(metrics,members),on='code_muni',validate='one_to_one')
        overview.to_file(source,layer='overview',driver='GPKG')
        items=[{'key':key,'label':v[0],'topic':v[1],'totalAreas':len(metrics),**aggregate(metrics,key)} for key,v in INDICATORS.items()]
        previous_summary=json.loads((data/'indicator-summaries.json').read_text())
        summary={'scope':'All matched common areas in Brazil; independent of map extent and selected layers.','indicators':items,'favelas':previous_summary['favelas']}
        (data/'indicator-summaries.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
        evidence={'contract':contract,'feature_count':len(metrics),'unique_common_ids':int(metrics.common_id.nunique()),
                  'overview_municipalities':len(overview),'regional_bounds':regional_bounds.T.to_dict('list'),
                  'database_sha256':sha256(source), 'population_coverage':manifest['population_coverage'],'regional_membership_counts':regions.groupby('region').size().to_dict()}
        prepared.write_text(json.dumps(evidence,indent=2)+'\n')
    for region in REGIONS:
        sql=f"SELECT * FROM social WHERE common_id IN (SELECT common_id FROM region_members WHERE region='{region}')"
        for tier,lo,hi,tolerance in [('mid',7,9,100),('detail',10,12,None)]:
            destination=data/f'social-{tier}-{region}-{suffix}.pmtiles'
            if args.reuse_prepared and destination.exists(): continue
            print('Building',tier,region,flush=True);tiles(source,destination,'social',sql,lo,hi,tolerance)
    print('Building municipality overview',flush=True)
    tiles(source,data/f'social-overview-{suffix}.pmtiles','overview','SELECT * FROM overview',2,6)
    public_manifest={**evidence,'archiveSuffix':suffix,'featureCount':evidence['feature_count'],'regions':list(REGIONS),'indicators':[{'key':k,'label':v[0],'topic':v[1]} for k,v in INDICATORS.items()]+[{'key':'income','label':'Household-head-weighted income','topic':'Income','minzoom':7}]}
    (data/'social.json').write_text(json.dumps(public_manifest,indent=2)+'\n')
    # Only browser source files are copied; README and build metadata are not public assets.
    for path in (ctx.root/'website').rglob('*'):
        if path.is_file() and path.suffix in ('.html','.js','.mjs','.css','.txt'):
            target=args.output/path.relative_to(ctx.root/'website');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    print(json.dumps({'output':str(args.output),'common_areas':evidence['feature_count'],'harmonisation_version':manifest['version']}),flush=True)

if __name__=='__main__': main()
