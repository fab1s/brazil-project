"""Existing infrastructure snapshots, category translations, cleaning, and charts."""
import json
import textwrap
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from brazil_project.io import WorkflowError

SECTORS=dict(zip(['Transporte','Energia','Mineração','Petróleo e Gás','Outros','Recursos Hídricos','Nuclear/Radiativa'],
                 ['Transportation','Energy','Mining','Oil and Gas','Other','Water Resources','Nuclear/Radioactive']))


def clean_obrasgov(frame):
    result=frame.copy()
    result['geometry_type']=result.geom_type.str.upper()
    result['geometry_empty']=shapely.is_empty(result.geometry.array)
    result['geometry_valid']=shapely.is_valid(result.geometry.array)
    bounds=shapely.bounds(result.geometry.array)
    result['coordinate_problem']=(bounds[:,0]<-180)|(bounds[:,2]>180)|(bounds[:,1]<-90)|(bounds[:,3]>90)
    result=result[~result.geometry_empty&~result.coordinate_problem].copy()
    result.geometry=shapely.make_valid(result.geometry.array)
    return result


def counts(frame,columns):
    result=frame.dropna(subset=columns).groupby(columns).size().rename('projects').reset_index()
    result['share']=result.projects/result.projects.sum()
    return result.sort_values('projects',ascending=False,kind='stable').head(15)


def plot_counts(table,columns,title,path):
    labels=table[columns].astype(str).agg(' — '.join,axis=1)
    labels=['\n'.join(textwrap.wrap(label,48 if len(columns)>1 else 34)) for label in labels]
    fig,ax=plt.subplots(figsize=(13,9))
    y=np.arange(len(table));ax.barh(y,table.projects,color='#0B5FA5' if len(columns)==1 else '#0F766E')
    ax.set_yticks(y,labels);ax.invert_yaxis()
    for i,(_,row) in enumerate(table.iterrows()): ax.text(row.projects*1.01,i,f'{row.projects:,.0f} · {row.share:.1%}',va='center',fontsize=9)
    ax.set_xlim(0,table.projects.max()*1.3);ax.set_title(title,loc='left',pad=15);ax.set_xlabel('Number of projects');ax.grid(axis='x',alpha=.2)
    fig.text(.03,.02,'Source: GovObras. Percentages use all classified project records.',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(path,dpi=160,facecolor='white');plt.close(fig)


def run(ctx,source):
    acquired=ctx.artifact('acquire-'+source,'projects.parquet')
    acquisition_report=ctx.artifact('acquire-'+source,'report.json')
    use_acquired=acquired.exists() and acquisition_report.exists() and json.loads(acquisition_report.read_text()).get('status')=='completed'
    frame=gpd.read_parquet(acquired) if use_acquired else gpd.read_file(ctx.require(ctx.path('infrastructure',source)))
    if frame.crs is None or frame.crs.to_epsg()!=4674:
        raise WorkflowError(f'{source} requires the original EPSG:4674 coordinate system')
    destination=ctx.root/'outputs/figures'/source
    destination.mkdir(parents=True,exist_ok=True)
    if source=='ibama':
        if 'tp_setor' not in frame: raise WorkflowError('IBAMA tp_setor missing')
        frame['tp_sector_en']=frame.tp_setor.map(SECTORS)
        frame['tp_setor_en']=frame['tp_sector_en']  # COMPATIBILITY: alternate original R script spelling.
        ctx.write_geo(frame,'ibama','licensed_projects')
        categories=frame.groupby('tp_sector_en',dropna=False).size().rename('projects').reset_index()
        ctx.write_table(categories,'ibama','sector_counts')
        mapping=frame.to_crs(4326).explore(column='tp_sector_en',name='IBAMA licensed projects',legend=True)
        out=ctx.root/'outputs/maps/ibama.html';out.parent.mkdir(parents=True,exist_ok=True);mapping.save(out)
        return ctx.report(source,{'records':len(frame),'unknown_sectors':int(frame.tp_sector_en.isna().sum()),'source':'acquired' if use_acquired else 'copied_snapshot'})
    translations=json.loads((ctx.root/'code/config/obrasgov_translations.json').read_text())
    for field,target,kind in [('tipo','type_en','type'),('subtipo','subtype_en','subtype')]:
        if field not in frame: raise WorkflowError(f'Obrasgov {field} missing')
        frame[target]=frame[field].map(translations[kind])
    for name,columns,title in [('type_counts',['type_en'],'GovObras projects by type'),('type_subtype_counts',['type_en','subtype_en'],'GovObras projects by type and subtype')]:
        table=counts(frame,columns);ctx.write_table(table,source,name)
        if not table.empty: plot_counts(table,columns,title,destination/(name+'.png'))
    cleaned=clean_obrasgov(frame)
    ctx.write_geo(frame,source,'projects')
    ctx.write_geo(cleaned,source,'projects_clean')
    baseline=ctx.root/'data/processed/obrasgov/projects_st_clean.gpkg'
    count=None
    if baseline.exists():
        import sqlite3
        with sqlite3.connect(f'file:{baseline}?mode=ro',uri=True) as connection:
            table=connection.execute('SELECT table_name FROM gpkg_contents').fetchone()[0]
            count=connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    return ctx.report(source,{'records':len(frame),'cleaned_records':len(cleaned),'removed':len(frame)-len(cleaned),
                              'baseline_cleaned_records':count,'count_matches_baseline':len(cleaned)==count,
                              'source':'acquired' if use_acquired else 'copied_snapshot'})
