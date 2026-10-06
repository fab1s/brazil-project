"""Retain the original spherical overview through an isolated R adapter."""
import pandas as pd
import geopandas as gpd
import folium
from brazil_project.io import identifiers
from brazil_project.io import WorkflowError


def run(ctx):
    import shutil
    import subprocess
    runtime=shutil.which('Rscript')
    if not runtime: raise WorkflowError('Overview requires R sf/S2 for original spherical topology. Restore renv.lock with code/scripts/r/restore.R.')
    code=ctx.municipality or '3106200'
    out=ctx.artifact('overview','report.json').parent
    out.mkdir(parents=True,exist_ok=True)
    result=subprocess.run([runtime,str(ctx.root/'code/scripts/r/overview.R'),str(ctx.root),str(ctx.require(ctx.path('census','tracts'))),str(out),code],cwd=ctx.root)
    if result.returncode: raise WorkflowError('R spherical overview failed; restore renv.lock and inspect the original geometry data')
    counts={}
    for year in (2010,2022):
        csv=ctx.require(out/f'change_summary_2000_{year}.csv')
        summary=pd.read_csv(csv,dtype={'code_tract_2000':'string'})
        ctx.write_table(summary,'overview',f'change_summary_2000_{year}')
        counts[str(year)]=summary.change_type.value_counts().to_dict()
        ctx.require(out/f'intersections_2000_{year}.gpkg')
    destination=ctx.root/'outputs/maps/overview'
    destination.mkdir(parents=True,exist_ok=True)
    for tract in ['310620025610001','310620005650306','310620005620021','310620005620008']:
        old=gpd.read_file(ctx.path('census','tracts'),layer='2000_urban',where=f"CAST(code_tract AS TEXT) = '{tract}'")
        if old.empty: continue
        mapping=old.to_crs(4326).explore(name='2000 tract',color='red',style_kwds={'fillOpacity':.4})
        for year,color in [(2010,'orange'),(2022,'steelblue')]:
            overlaps=gpd.read_file(out/f'intersections_2000_{year}.gpkg',where=f"CAST(code_tract_2000 AS TEXT) = '{tract}'")
            eligible=identifiers(overlaps.loc[overlaps.overlap_pct>.05,'code_tract_new']).dropna().unique()
            if len(eligible):
                where='CAST(code_tract AS TEXT) IN ('+','.join("'"+v+"'" for v in eligible)+')'
                geometry=gpd.read_file(ctx.path('census','tracts'),layer=str(year),where=where)
                geometry.to_crs(4326).explore(m=mapping,name=f'{year} tracts (>5%)',color=color,style_kwds={'fillOpacity':.4})
        folium.LayerControl().add_to(mapping);mapping.save(destination/(tract+'.html'))
    return ctx.report('overview',{'municipality':code,'adapter':'R sf/S2','classification_counts':counts,'reason':'preserve original geographic intersection and area semantics'})
