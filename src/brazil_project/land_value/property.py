"""Preserve the exploratory property notebook's exact dates and workbook sheets."""
import pandas as pd
import geopandas as gpd
import shapely
from brazil_project.io import WorkflowError


def run(ctx):
    book=ctx.require(ctx.path('land_value','workbook'))
    sheets=pd.read_excel(book,sheet_name=None)
    missing=[name for name in ['Annex I','Annex II','Annex III','Annex IV'] if name not in sheets]
    if missing: raise WorkflowError(f'Missing workbook sheets: {missing}')
    for name in ['Annex I','Annex II','Annex III','Annex IV']:
        ctx.write_table(sheets[name],'land-value',name.lower().replace(' ','_'))
    unavailable=[]
    for field in ['zone_file','property_file']:
        path=ctx.path('land_value','raw')/ctx.config['land_value'][field]
        if not path.exists():
            unavailable.append(str(path.relative_to(ctx.root)));continue
        frame=pd.read_csv(path)
        if 'GEOMETRIA' not in frame: raise WorkflowError(f'{path}: GEOMETRIA WKT missing')
        geo=gpd.GeoDataFrame(frame,geometry=shapely.from_wkt(frame.GEOMETRIA.to_numpy()),crs=31983)
        ctx.write_geo(geo,'land-value',field)
    report=ctx.report('land-value',{'workbook_sheets':list(sheets),'status':'exploratory','missing_exact_inputs':unavailable})
    if unavailable: raise WorkflowError('Land value workbook imported; exact original CSV inputs are absent: '+', '.join(unavailable)+'. Different dated snapshots have been preserved without substitution.')
    return report
