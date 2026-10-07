"""Export the approved Obrasgov location derivative for the existing here.now map."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import geopandas as gpd
import pandas as pd
import shapely

from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint
from brazil_project.report_engine import require_producers


# COMPATIBILITY: These are the ten fields in the previous published archive.
PUBLIC_FIELDS=['id_projeto_investimento','desc_nome','tipo','subtipo','situacao','uf_principal',
               'organizacao_resp','vl_investimento_previsto_total','dt_inicial_prevista','dt_final_prevista']


def prepare(ctx):
    if ctx.municipality:
        raise WorkflowError('The public Obrasgov map requires national scope.')
    require_producers(ctx, 'obrasgov_preprocessing')
    report_path=ctx.require(ctx.artifact('obrasgov-primary-state-filter', 'report.json'))
    report=json.loads(report_path.read_text())
    source=ctx.require(ctx.artifact('obrasgov-primary-state-filter', 'map_components.parquet'))
    if report.get('status')!='completed' or fingerprint(source)!=report['output_sha256']['map_components']:
        raise WorkflowError('State-exclusion outputs are incomplete or changed; rerun obrasgov.')
    frame=gpd.read_parquet(source)
    if len(frame)!=report['map_components_after'] or not frame.component_id.is_unique:
        raise WorkflowError('Map component identifiers/counts differ from the approved output.')
    if not frame.final_map_eligible.all() or frame.primary_state_excluded.any():
        raise WorkflowError('An excluded component entered the website export.')
    if not frame.geom_type.isin(['Point','LineString']).all():
        raise WorkflowError('Only screened points and lines may enter the Obrasgov map.')
    # CONTRACT: Export original public project fields and component provenance;
    # retain detailed diagnostics in the local research audit, outside the site.
    original=ctx.require(ctx.path('location_qa','source'))
    columns=PUBLIC_FIELDS+['geometry']
    frame=frame[columns+['component_id','location_status','primary_state_check','source_row']].copy()
    return frame, report, {str(p):fingerprint(p) for p in (source, report_path, original)}


def run(ctx, output, work):
    implementation=fingerprint(Path(__file__))
    frame, report, inputs=prepare(ctx)
    if not shutil.which('ogr2ogr'):
        raise WorkflowError('Install GDAL with the PMTiles driver to build the website archive.')
    data=output/'data'
    if not (data/'stats.json').is_file():
        raise WorkflowError('Initialize the existing website snapshot before exporting Obrasgov.')
    work.mkdir(parents=True,exist_ok=True)
    source_hash=report['output_sha256']['map_components']
    filename='obras-screened-'+source_hash[:12]+'.pmtiles'
    with tempfile.TemporaryDirectory(dir=work) as directory:
        temporary=Path(directory);gpkg=temporary/'screened.gpkg'
        public=frame.drop(columns='source_row')
        public.to_file(gpkg,layer='projects_st',driver='GPKG',index=False)
        exchange=gpd.read_file(gpkg,layer='projects_st').set_index('component_id')
        expected=public.set_index('component_id').loc[exchange.index]
        if set(exchange.index)!=set(frame.component_id) or exchange.crs!=frame.crs or not (shapely.to_wkb(exchange.geometry.array)==shapely.to_wkb(expected.geometry.array)).all():
            raise WorkflowError('Prepared website geometry/identifiers differ from the research derivative.')
        pd.testing.assert_frame_equal(pd.DataFrame(exchange.drop(columns='geometry')),pd.DataFrame(expected.drop(columns='geometry')),check_dtype=False,check_exact=True)
        archive=temporary/filename
        subprocess.run(['ogr2ogr','-f','PMTiles',str(archive),str(gpkg),'-nln','projects_st',
                        '-t_srs','EPSG:4326','-dsco','MINZOOM=0','-dsco','MAXZOOM=13',
                        '-dsco','MAX_FEATURES=1000000','-dsco','MAX_SIZE=10000000'],check=True)
        if fingerprint(Path(__file__))!=implementation:raise WorkflowError('Exporter changed during build; rerun.')
        for path,digest in inputs.items():
            if fingerprint(Path(path))!=digest:raise WorkflowError('Research input changed during website build: '+path)
        staged=data/(filename+'.tmp');shutil.copyfile(archive,staged);staged.replace(data/filename)
    manifest={'archive':filename,'archiveSha256':fingerprint(data/filename),'sourceComponentSha256':source_hash,
              'sourceRecords':report['source_rows_preserved'],'mappedSourceRecords':int(frame.source_row.nunique()),
              'mapComponents':len(frame),'geometryCounts':frame.geom_type.value_counts().to_dict(),
              'locationScreenCounts':frame.location_status.value_counts().to_dict(),
              'stateExcludedComponents':report['excluded_components'],'newlyStateExcludedMapComponents':report['newly_excluded_map_components'],
              'policy':report['policy'],'coordinatesCorrected':report['coordinates_corrected']}
    stats=json.loads((data/'stats.json').read_text())
    obras=next(dataset for dataset in stats['datasets'] if dataset['key']=='obras')
    if obras['featureCount']!=manifest['sourceRecords']:
        raise WorkflowError('Frozen website source-record totals differ from the research snapshot.')
    obras.update(mappableFeatureCount=manifest['mappedSourceRecords'],mapComponentCount=len(frame),locationScreening=manifest)
    for name,payload in [('obras-location.json',manifest),('stats.json',stats)]:
        target=data/name;tmp=target.with_suffix('.tmp.json');tmp.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n');tmp.replace(target)
    for source in (ctx.root/'website').rglob('*'):
        if source.is_file() and source.suffix in ('.html','.js','.mjs','.css','.txt'):
            target=output/source.relative_to(ctx.root/'website');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    evidence={**manifest,'inputs':inputs,'scriptSha256':implementation,'publicFields':PUBLIC_FIELDS,
              'verification':{'prepared_identifiers_attributes_crs_wkb_exact':True},
              'limitations':['Vector tiles project, clip and quantize geometry for display. Eligible locations are not independently verified geocoding.','Record totals and type/date summaries retain all source rows; do not sum repeated component investment values.']}
    (work/'export-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return evidence


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path('project.toml'))
    parser.add_argument('--output',type=Path,default=Path('outputs/maps/website'))
    parser.add_argument('--work',type=Path,default=Path('.cache/website-location-update/build'))
    args=parser.parse_args();print(json.dumps(run(Context(args.config),args.output,args.work),indent=2))

if __name__=='__main__':main()
