"""Render an overview of saved point eligibility; never move source coordinates."""
import argparse
import json
from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint


def verified_plot_inputs(ctx):
    report=json.loads(ctx.require(ctx.artifact('obrasgov-location-qa','report.json')).read_text())
    if report.get('status')!='completed':
        raise WorkflowError('Plot requires completed location QA; rerun the stage and verify it first.')
    component=ctx.require(ctx.artifact('obrasgov-location-qa','component_audit.parquet'))
    source=ctx.require(ctx.path('location_qa','source'))
    reference=report['contract']['references']['municipalities']
    municipalities=ctx.require(ctx.path('location_qa','references')/reference['path'])
    for path,expected in [(component,report['output_fingerprints']['component_audit']),
                          (source,report['contract']['source_sha256']),(municipalities,reference['sha256'])]:
        if fingerprint(path)!=expected:
            raise WorkflowError('Plot input changed since verified QA: '+str(path))
    return component,municipalities


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',default='project.toml');a=p.parse_args()
    ctx=Context(a.config)
    component,municipalities=verified_plot_inputs(ctx)
    points=gpd.read_parquet(component)
    points=points[points.geom_type.eq('Point') & ~points.out_of_range & ~points.nonfinite_coordinates & ~points.invalid_geometry & ~points.empty_geometry].copy()
    mun=gpd.read_file('zip://'+str(municipalities)).to_crs(4674)
    mun.geometry=mun.geometry.simplify(.03,preserve_topology=True)
    fig,ax=plt.subplots(figsize=(12,11))
    mun.plot(ax=ax,color='#e6eee7',edgecolor='#ffffff',linewidth=.12)
    ordinary=points[points.location_status.eq('eligible_unverified')]
    review=points[points.map_eligible & ~points.location_status.eq('eligible_unverified')]
    quarantined=points[~points.map_eligible]
    for data,color,size,label in [(ordinary,'#76938d',1,'Eligible; coordinates not independently verified'),(review,'#1479b8',9,'Retained locations requiring review'),(quarantined,'#c54737',12,'Quarantined suspicious locations')]:
        ax.scatter(data.geometry.x,data.geometry.y,s=size,c=color,alpha=.7 if size>1 else .2,label=label,rasterized=True)
    ax.set_xlim(-80,-25);ax.set_ylim(-40,10);ax.set_aspect(1/np.cos(np.deg2rad(15)))
    ax.set_xlabel('Longitude');ax.set_ylabel('Latitude');ax.set_title('Obrasgov location screening — point components',loc='left',pad=16)
    legend=ax.legend(loc='lower left',frameon=True,facecolor='white',fontsize=9)
    for handle in legend.legend_handles: handle.set_alpha(1)
    fig.text(.1,.015,'Original point coordinates. Missing, invalid and out-of-range points and all lines/polygons are omitted from this overview.\nViewport: 80°W–25°W, 40°S–10°N. Reference: IBGE municipalities 2022; outlines simplified only for display. Flags require review.',fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1))
    out=ctx.root/'outputs/figures/obrasgov-location-qa';out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/'location-screening.png',dpi=160,facecolor='white');plt.close(fig)
    print(out/'location-screening.png')


if __name__=='__main__':main()
