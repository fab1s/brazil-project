"""Compare the Python projected geometry engine to the original R reference."""
import argparse
import geopandas as gpd
import pandas as pd
import numpy as np
import shapely
from brazil_project.io import Context
from brazil_project.harmonisation.census import prepare,correspondence


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',default='config/project.toml')
    parser.add_argument('--municipality',default='3106200')
    args=parser.parse_args()
    if not args.municipality.isdigit(): parser.error('municipality must be numeric')
    ctx=Context(args.config);ctx.municipality=args.municipality;ctx.intermediate=ctx.intermediate/('municipality_'+args.municipality)
    frames=[prepare(gpd.read_file(ctx.path('census','tracts'),layer=str(year),where=f'CAST(code_tract AS TEXT) LIKE \'{args.municipality}%\''),year,
                    ctx.config['census']['crs'],ctx.config['census']['precision_grid']) for year in (2010,2022)]
    cross,l10,_,groups,base=correspondence(*frames)
    ctx.write_table(cross,'harmonisation_python_reference','crosswalk')
    ctx.write_geo(base,'harmonisation_python_reference','base')
    folder=ctx.intermediate/'harmonisation_reference'
    expected=pd.read_csv(ctx.require(folder/'crosswalk.csv'),dtype={'id_2010':'string','id_2022':'string'})
    edge=lambda f:set(zip(f.id_2010.astype(str),f.id_2022.astype(str)))
    a,b=edge(cross),edge(expected)
    old_groups=pd.read_csv(ctx.require(folder/'crosswalk_grouped.csv'),dtype={'id_2010':'string','id_2022':'string','common_id':'string'})
    partitions=lambda f:{frozenset(zip(g.id_2010.astype(str),g.id_2022.astype(str))) for _,g in f.groupby('common_id')}
    reference=gpd.read_file(ctx.require(folder/'base.gpkg'))
    distance=shapely.hausdorff_distance(base.geometry.array,reference.geometry.array)
    grid=ctx.config['census']['precision_grid']
    report={'crosswalk_matches':a==b,'python_only_edges':len(a-b),'R_only_edges':len(b-a),
            'partition_matches':partitions(l10)==partitions(old_groups),'geometry_boundary_tolerance_m':grid,
            'maximum_geometry_boundary_distance_m':float(np.nanmax(distance)),
            'geometry_matches':bool(np.isfinite(distance).all() and (distance<=grid).all()),
            'python_rows':len(base),'R_rows':len(reference),'scope':args.municipality}
    report['passed']=report['crosswalk_matches'] and report['partition_matches'] and report['geometry_matches'] and len(base)==len(reference)
    print(ctx.report('verification-harmonisation',report))
    if not report['passed']: raise SystemExit(1)

if __name__=='__main__':main()
