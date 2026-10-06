"""Original tract-level race exploration and regional comparison maps."""
import numpy as np
import pandas as pd
import geopandas as gpd
import folium
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from brazil_project.acquisition.census import read
from brazil_project.io import identifiers,WorkflowError

MUNICIPALITIES=['Belo Horizonte','Vespasiano','São José da Lapa','Confins','Lagoa Santa','Santa Luzia']


def run(ctx):
    # This exploratory map has its own original six-municipality scope.
    columns=', '.join("'"+name+"'" for name in MUNICIPALITIES)
    where=f'name_muni IN ({columns}) AND abbrev_state = \'MG\''
    original_scope=ctx.municipality
    ctx.municipality=''  # Read raw annual tables; map scope is defined by original municipal names.
    try:
        frames={year:gpd.read_file(ctx.require(ctx.path('census','tracts')),layer=str(year),where=where) for year in (2010,2022)}
        data10=read(ctx,2010,'Pessoa',['code_tract','pessoa03_V001','pessoa03_V003'])
        data22=read(ctx,2022,'Basico',['code_tract','V0001']).merge(read(ctx,2022,'Pessoas',['code_tract','raca_V01318']),on='code_tract',how='left',validate='one_to_one')
    finally:
        ctx.municipality=original_scope
    frames10={2010:(data10,'pessoa03_V001','pessoa03_V003'),2022:(data22,'V0001','raca_V01318')}
    mapping=None
    summaries={}
    for year,geometry in frames.items():
        geometry['code_tract']=identifiers(geometry.code_tract)
        data,pop,black=frames10[year]
        joined=geometry.merge(data,on='code_tract',how='inner',validate='many_to_one')
        joined['black_ratio']=joined[black]/joined[pop]  # Preserve original exploratory division, not temporal safeguards.
        joined=joined.rename(columns={pop:'pop',black:'black_pop'})
        ctx.write_geo(joined,'census-exploration',f'black_ratio_{year}')
        mapped=joined.copy()
        # Mapping libraries cannot serialize infinities; keep analytical values unchanged in artifacts.
        mapped['black_ratio']=mapped.black_ratio.replace([np.inf,-np.inf],np.nan)
        mapped['share_band']=pd.cut(mapped.black_ratio,[-1e-12,*np.arange(.05,.46,.05),np.inf],right=False).astype(str)
        mapping=mapped.to_crs(4326).explore(column='share_band',name=str(year),m=mapping,legend=True,style_kwds={'fillOpacity':1})
        bh=joined[joined.name_muni=='Belo Horizonte'].black_ratio.replace([np.inf,-np.inf],np.nan).dropna()
        fig,ax=plt.subplots(figsize=(6,5));ax.boxplot(bh);ax.set_title(f'Black population share in Belo Horizonte {year}');ax.set_ylabel('Population share')
        out=ctx.root/'outputs/figures/census-exploration';out.mkdir(parents=True,exist_ok=True)
        fig.tight_layout();fig.savefig(out/f'black_ratio_boxplot_{year}.png',dpi=160);plt.close(fig)
        summaries[str(year)]={'map_tracts':len(joined),'BH_summary':bh.describe().to_dict()}
    metro=list((ctx.root/'data/raw').rglob('infraurbana_viario_linhaverde.shp'))
    if metro:
        gpd.read_file(metro[0]).to_crs(4326).explore(m=mapping,name='Metro',color='green')
    folium.LayerControl().add_to(mapping)
    path=ctx.root/'outputs/maps/black_ratio_2010_2022.html';path.parent.mkdir(parents=True,exist_ok=True);mapping.save(path)
    return ctx.report('census-exploration',{'scope':MUNICIPALITIES,'annual':summaries,'metro_overlay':'included' if metro else 'missing original Linha Verde shapefile; not substituted'})
