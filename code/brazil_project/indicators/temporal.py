"""Annual common-area estimates translated from the temporal comparison notebook."""
import re
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from brazil_project.io import WorkflowError, keys, lookup_keys
from brazil_project.acquisition.census import read


def safe_ratio(numerator, denominator):
    return numerator.div(denominator.where(denominator > 0))


def aggregate(data, lookup, year, preserve_missing=(), lookup_first=False):
    id_column = f'id_{year}'
    keys(data, id_column)
    lookup = lookup_keys(lookup, year).dropna(subset=['common_id'])
    joined = lookup.merge(data, on=id_column, how='left', validate='one_to_one') if lookup_first else data.merge(lookup, on=id_column, how='left', validate='one_to_one')
    columns = [c for c in data.columns if c != id_column]
    grouped = joined.dropna(subset=['common_id']).groupby('common_id', sort=False)
    totals = grouped[columns].sum(min_count=0)
    for column in preserve_missing:
        totals[column] = grouped[column].sum(min_count=1)
    return totals.reset_index()


def count_frame(frame, year, denominator, numerator, denominator_name, numerator_name, coalesce=False):
    keys(frame, 'code_tract')
    selected = frame[numerator]
    if coalesce:
        values = selected.fillna(0).sum(axis=1)
    elif len(numerator) == 1:
        values = selected.iloc[:, 0]
    else:
        values = selected.sum(axis=1)
    return pd.DataFrame({f'id_{year}': frame.code_tract, f'{denominator_name}_{year}': frame[denominator],
                         f'{numerator_name}_{year}': values})


def annual_ratio(frame, lookup, year, denominator_name, numerator_name, ratio_name, preserve=False, lookup_first=False):
    denominator = f'{denominator_name}_{year}'
    totals = aggregate(frame, lookup, year, [denominator] if preserve else [], lookup_first)
    totals[f'{ratio_name}_ratio_{year}'] = safe_ratio(totals[f'{numerator_name}_{year}'], totals[denominator])
    return totals


def income_column(frame, code):
    columns = [c for c in frame if re.search(r'(^|_)' + re.escape(code) + r'$', c, flags=re.I)]
    if len(columns) != 1:
        raise WorkflowError(f'Expected one income column ending in {code}, found {columns}')
    return columns[0]


def income_aggregate(frame, lookup, year):
    keys(frame, f'id_{year}')
    annual = lookup_keys(lookup, year).dropna(subset=['common_id']).merge(frame, on=f'id_{year}', how='left', validate='one_to_one')
    valid_weight = np.isfinite(annual.heads) & (annual.heads >= 0)
    valid_mean = np.isfinite(annual.mean_income) & (annual.mean_income >= 0)
    usable = valid_weight & (annual.heads > 0) & valid_mean
    annual = annual.assign(n=1, n_used=usable.astype(int), missing_weights=(~valid_weight).astype(int),
                           missing_means=(valid_weight & (annual.heads > 0) & ~valid_mean).astype(int),
                           heads_used=annual.heads.where(usable, 0), weighted_sum=(annual.heads * annual.mean_income).where(usable, 0))
    totals = annual.groupby('common_id', sort=False)[['n', 'n_used', 'missing_weights', 'missing_means', 'heads_used', 'weighted_sum']].sum().reset_index()
    totals['complete'] = (totals.missing_weights == 0) & (totals.missing_means == 0)
    totals['tract_coverage_pct'] = 100 * totals.n_used / totals.n
    totals['income'] = safe_ratio(totals.weighted_sum, totals.heads_used)
    return totals.rename(columns={c: f'{c}_{year}' for c in totals if c != 'common_id'})


def prepare_income(frame, year):
    def col(code):
        return pd.to_numeric(frame[income_column(frame, code)], errors='coerce')
    if year == 2010:
        recipients, total = col('V021'), col('V022')
        mean = (total / recipients).where(np.isfinite(recipients) & (recipients > 0) & np.isfinite(total) & (total >= 0))
        heads = col('V020')
    else:
        heads, mean = col('V06001'), col('V06004')
    return pd.DataFrame({f'id_{year}': frame.code_tract, 'heads': heads, 'mean_income': mean})


def source_columns(year, dataset):
    columns = {'code_tract'}
    if (year, dataset) == (2010, 'Pessoa'):
        columns |= {'pessoa03_V001','pessoa03_V003','pessoa03_V005'}
        columns |= {f'pessoa13_V{i:03}' for i in range(49,135)} | {f'pessoa01_V{i:03}' for i in range(12,78)}
    elif (year, dataset) == (2022, 'Pessoas'):
        columns |= {'raca_V01318','raca_V01320'}
        columns |= {f'alfabetizacao_V{i:05}' for i in range(644,657)} | {f'alfabetizacao_V{i:05}' for i in range(748,761)}
    elif dataset == 'Basico':
        columns.add('V0001')
    elif (year, dataset) == (2010, 'Domicilio'):
        columns |= {f'domicilio01_V{i:03}' for i in [2,3,4,5,12,17,18,19,20,21,23,35]}
    elif (year, dataset) == (2022, 'Domicilio'):
        columns |= {'situacao'} | {f'domicilio01_V{i:05}' for i in [1,47,48,49]}
        columns |= {f'domicilio02_V{i:05}' for i in [111,307,308,309,310,311,312,313,314,397,398]}
    return sorted(columns)


def run(ctx):
    from brazil_project.harmonisation.census import load_bundle
    bundle, manifest = load_bundle(ctx, names=[])
    lookups = {year: bundle[f'lookup_{year}'] for year in (2010, 2022)}
    sizes = bundle['group_sizes']
    base = bundle['common_geometry_2022']
    tables = {(year,dataset): read(ctx,year,dataset,source_columns(year,dataset))
              for year,dataset in [(2010,'Pessoa'),(2010,'Domicilio'),(2022,'Basico'),(2022,'Pessoas'),(2022,'Domicilio')]}
    for (year,dataset), table in tables.items():
        keys(table,'code_tract')
        ctx.write_table(table,'census',f'{year}_{dataset.lower()}')
    pop10=tables[2010,'Pessoa']
    pop22=tables[2022,'Basico'].merge(tables[2022,'Pessoas'],on='code_tract',how='left',validate='one_to_one')
    reports = {'harmonisation_version': manifest['version'], 'spatial_unit': 'common_id'}
    def save(name, annual, ratio=True):
        result=annual[2010].merge(annual[2022],on='common_id',how='outer',validate='one_to_one')
        if ratio:
            result[f'{name}_ratio_change']=result[f'{name}_ratio_2022']-result[f'{name}_ratio_2010']
            result[f'{name}_ratio_change_pp']=100*result[f'{name}_ratio_change']
        result=result.merge(sizes,on='common_id',how='left',validate='one_to_one')
        ctx.write_table(result,'indicators',name)
        for year,value in annual.items(): ctx.write_table(value,'indicators',f'{name}_{year}_common')
        # GeoParquet keeps the original base geometry and avoids modifying baseline GeoPackages.
        attributes=result.drop(columns=['n_2010','n_2022','relationship'],errors='ignore')
        ctx.write_geo(base.merge(attributes,on='common_id',how='left',validate='many_to_one'),'indicators',name+'_sf')
        reports[name]={'common_areas':len(result),'missing_change':int(result.filter(regex='change$').isna().sum().sum())}
        return result
    for name, cols10,cols22 in [('black',['pessoa03_V003'],['raca_V01318']),('brown',['pessoa03_V005'],['raca_V01320']),('black_brown',['pessoa03_V003','pessoa03_V005'],['raca_V01318','raca_V01320'])]:
        annual={}
        for year,frame,den,cols in [(2010,pop10,'pessoa03_V001',cols10),(2022,pop22,'V0001',cols22)]:
            data=count_frame(frame,year,den,cols,'pop',name+'_pop',name=='black_brown')
            annual[year]=annual_ratio(data,lookups[year],year,'pop',name+'_pop',name)
        save(name,annual)
    annual={}
    for year,frame,den,nums in [(2010,pop10,[f'pessoa13_V{i:03}' for i in range(49,135)],[f'pessoa01_V{i:03}' for i in range(12,78)]),
                                (2022,tables[2022,'Pessoas'],[f'alfabetizacao_V{i:05}' for i in range(644,657)],[f'alfabetizacao_V{i:05}' for i in range(748,761)])]:
        data=pd.DataFrame({f'id_{year}':frame.code_tract,f'pop_15plus_{year}':frame[den].sum(axis=1),f'literate_15plus_{year}':frame[nums].sum(axis=1)})
        annual[year]=annual_ratio(data,lookups[year],year,'pop_15plus','literate_15plus','literacy')
    save('literacy',annual)
    definitions={
        'rudimentary_sanitation':(['domicilio01_V019','domicilio01_V020','domicilio01_V021'],['domicilio02_V00312','domicilio02_V00313','domicilio02_V00314']),
        'water_network':(['domicilio01_V012'],['domicilio02_V00111']),
        'waste_collection':(['domicilio01_V035'],['domicilio02_V00397','domicilio02_V00398']),
        'sewer_septic':(['domicilio01_V017','domicilio01_V018'],['domicilio02_V00309','domicilio02_V00310','domicilio02_V00311']),
        'houses':(['domicilio01_V003'],['domicilio01_V00047']),
        'village_condo':(['domicilio01_V004'],['domicilio01_V00048']),
        'apartments':(['domicilio01_V005'],['domicilio01_V00049'])}
    for name,(cols10,cols22) in definitions.items():
        annual={}
        numerator=name if name in ['houses','village_condo','apartments'] else name+'_households'
        housing=name in ['houses','village_condo','apartments']
        for year,cols,den in [(2010,cols10,'domicilio01_V002'),(2022,cols22,'domicilio01_V00001')]:
            data=count_frame(tables[year,'Domicilio'],year,den,cols,'households',numerator,len(cols)>1)
            annual[year]=annual_ratio(data,lookups[year],year,'households',numerator,name,housing,housing)
        save(name,annual)
    annual={year:income_aggregate(prepare_income(read(ctx,year,'ResponsavelRenda'),year),lookups[year],year) for year in (2010,2022)}
    inflation=ctx.config['census']['inflation_2022']/ctx.config['census']['inflation_2010']
    if not np.isfinite(inflation) or inflation<=0: raise WorkflowError('Inflation factor must be finite and positive')
    annual[2010]['income_2010_nominal']=annual[2010].income_2010
    annual[2010]['income_2010']*=inflation
    income=save('income',annual,False)
    income['valid_income_change']=np.isfinite(income.income_2010)&np.isfinite(income.income_2022)
    income['valid_income_change_pct']=income.valid_income_change&(income.income_2010>0)
    income['income_change_brl']=income.income_2022-income.income_2010
    income['income_change_pct']=(100*(income.income_2022/income.income_2010-1)).where(income.valid_income_change_pct)
    ctx.write_table(income,'indicators','income')
    ctx.write_geo(base.merge(income.drop(columns=['n_2010','n_2022','relationship'],errors='ignore'),on='common_id',how='left',validate='many_to_one'),'indicators','income_sf')
    population={}
    for year,frame,den in [(2010,pop10,'pessoa03_V001'),(2022,pop22,'V0001')]:
        population[year]=aggregate(pd.DataFrame({f'id_{year}':frame.code_tract,f'pop_{year}':frame[den]}),lookups[year],year,[f'pop_{year}'])
    # CONTRACT: the saved area and group geometry belong to the validated active bundle.
    areas = base[['common_id', 'area_km2']]
    density=population[2010].merge(population[2022],on='common_id',how='outer',validate='one_to_one').merge(areas,on='common_id',how='left',validate='one_to_one')
    for year in (2010,2022): density[f'population_density_{year}']=safe_ratio(density[f'pop_{year}'],density.area_km2)
    density['population_density_change']=density.population_density_2022-density.population_density_2010
    density['population_density_change_pct']=(100*(density.population_density_2022/density.population_density_2010-1)).where(density.population_density_2010>0)
    ctx.write_table(density,'indicators','population_density')
    ctx.write_geo(base.merge(density.drop(columns='area_km2'),on='common_id',how='left',validate='many_to_one'),'indicators','population_density_sf')
    reports['population_density']={'common_areas':len(density)}
    return ctx.report('indicators',reports)
