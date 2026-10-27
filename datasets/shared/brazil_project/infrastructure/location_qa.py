"""Conservative Obrasgov location diagnostics, separate from snapshot translation."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from brazil_project.io import WorkflowError

POLICY_VERSION = '1.0'
MARINE_PATTERN = r'\b(offshore|portuari\w*|dragagem|derrocamento|hidrovia\w*|navegacao|maritim\w*|quebra.mar|molhe|plataforma.*petroleo)\b'


def fingerprint(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value or '').lower()) if not unicodedata.combining(c))


def atomic_parts(geometry):
    if geometry is None or geometry.is_empty:
        return [geometry]
    if geometry.geom_type.startswith('Multi') or geometry.geom_type == 'GeometryCollection':
        return [part for item in geometry.geoms for part in atomic_parts(item)]
    return [geometry]


def decompose(frame):
    rows = []
    for source_row, (_, record) in enumerate(frame.iterrows()):
        description = ' '.join(text_value(record.get(c, '')) for c in ('desc_nome','desc_projeto','desc_funcao_social'))
        marine = bool(re.search(MARINE_PATTERN, normalize(description)))
        for ordinal, geometry in enumerate(atomic_parts(record.geometry)):
            rows.append({'source_row': source_row, 'component_id': f'{source_row}:{ordinal}',
                         'project_id': str(record.id_projeto_investimento),
                         'declared_uf': text_value(record.get('uf_principal')).upper().strip(),
                         'declared_municipality': text_value(record.get('codigo_municipio')).strip(),
                         'marine_signal': marine, 'geometry': geometry})
    return gpd.GeoDataFrame(rows, crs=frame.crs)


def joined_memberships(frame, key, columns):
    """Join distinct candidate codes, avoiding per-row callbacks for single hits."""
    unique = frame[[key, *columns]].drop_duplicates()
    result = unique.drop_duplicates(key).set_index(key)[columns].astype(str)
    multiple = unique[key].duplicated(keep=False)
    if multiple.any():
        combined = unique.loc[multiple].groupby(key)[columns].agg(lambda values: '|'.join(sorted(set(v for v in values.astype(str) if v))))
        result.loc[combined.index, columns] = combined
    return result


def text_value(value):
    return '' if value is None or pd.isna(value) else str(value)


def evaluate_samples(samples, municipalities, land, coastline, coast_tolerance_m, border_tolerance_m):
    """Return sample flags; boundary contacts retain all administrative candidates."""
    samples = samples.to_crs(4674).reset_index(drop=True)
    muni = municipalities.to_crs(4674).reset_index(drop=True)
    if 'CD_MUN' not in muni or 'SIGLA_UF' not in muni:
        raise WorkflowError('Municipal reference requires CD_MUN and SIGLA_UF.')
    # WHY: Query prepared reference polygons against the point tree; querying
    # each point against unsimplified national polygons repeats costly scans.
    print('Checking administrative coverage', flush=True)
    hits = gpd.sjoin(muni[['CD_MUN','SIGLA_UF','geometry']], samples[['geometry']], how='inner', predicate='intersects')
    sets = joined_memberships(hits, 'index_right', ['CD_MUN','SIGLA_UF'])
    result = pd.DataFrame(index=samples.index)
    result['municipalities'] = sets.CD_MUN.reindex(result.index, fill_value='')
    result['states'] = sets.SIGLA_UF.reindex(result.index, fill_value='')
    result['in_brazil'] = result.municipalities.ne('')
    print('Checking land and coastline', flush=True)
    land_hits = gpd.sjoin(land.to_crs(4674)[['geometry']], samples[['geometry']], how='inner', predicate='intersects')
    result['on_land'] = result.index.isin(land_hits.index_right)
    metric = samples.to_crs(5880)
    coast = coastline.to_crs(4674).copy()
    coast.geometry = shapely.intersection(coast.geometry.array, shapely.box(-85,-45,-20,15))
    coast = coast[~coast.geometry.is_empty].to_crs(5880)
    # WHY: Index individual line segments so a nearest-point query does not
    # repeatedly scan a continent-length polyline. Distances remain identical.
    coast_parts = [part for geom in coast.geometry for part in atomic_parts(geom) if part.geom_type in ('LineString','LinearRing')]
    xy, indices = shapely.get_coordinates(coast_parts, return_index=True)
    adjacent = indices[:-1] == indices[1:]
    segments = shapely.linestrings(np.stack([xy[:-1][adjacent], xy[1:][adjacent]], axis=1))
    coast_segments = gpd.GeoDataFrame(geometry=segments, crs=5880)
    nearest = gpd.sjoin_nearest(metric[['geometry']], coast_segments, how='left', distance_col='distance')
    print('Checking distance to mapped Brazilian territory', flush=True)
    result['coast_distance_m'] = nearest.groupby(level=0).distance.min().reindex(result.index)
    result['country_distance_m'] = 0.0
    outside = result.index[~result.in_brazil]
    if len(outside):
        # WHY: Municipal polygons include mapped islands and give the distance
        # to actual covered territory; a bounding box is never a land mask.
        near = gpd.sjoin_nearest(metric.loc[outside,['geometry']], muni.to_crs(5880)[['geometry']], how='left', distance_col='distance')
        result.loc[outside, 'country_distance_m'] = near.groupby(level=0).distance.min().reindex(outside)
    result['offshore'] = ~result.in_brazil & ~result.on_land
    result['far_offshore'] = result.offshore & (result.coast_distance_m > coast_tolerance_m) & (result.country_distance_m > coast_tolerance_m)
    result['foreign_land'] = ~result.in_brazil & result.on_land & (result.country_distance_m > border_tolerance_m)
    return result


def audit(frame, municipalities, land, coastline, coast_tolerance_m=5000, border_tolerance_m=1000, sample_spacing_m=1000, max_line_samples=250):
    if frame.crs is None or frame.crs.to_epsg() != 4674:
        raise WorkflowError('Obrasgov QA requires declared EPSG:4674; do not infer or overwrite source CRS.')
    if frame.id_projeto_investimento.isna().any():
        raise WorkflowError('Missing project ID; establish source provenance before location QA.')
    if min(coast_tolerance_m, border_tolerance_m, sample_spacing_m) <= 0 or max_line_samples < 2:
        raise WorkflowError('QA distances must be positive and max_line_samples must be at least two.')
    print('Decomposing source geometry recursively', flush=True)
    parts = decompose(frame)
    parts['geometry_type'] = parts.geom_type.fillna('Missing')
    parts['missing_geometry'] = parts.geometry.isna()
    parts['empty_geometry'] = shapely.is_empty(parts.geometry.array)
    coords = shapely.get_coordinates(parts.geometry.array, return_index=True)
    parts['nonfinite_coordinates'] = False
    parts['out_of_range'] = False
    parts['equal_axes'] = False
    if len(coords[0]):
        xy, ix = coords
        for field, condition in [('nonfinite_coordinates', ~np.isfinite(xy).all(axis=1)),
                                 ('out_of_range',(np.abs(xy[:,0])>180)|(np.abs(xy[:,1])>90)),
                                 ('equal_axes',np.isclose(xy[:,0],xy[:,1],rtol=0,atol=1e-8))]:
            parts.loc[np.unique(ix[condition]),field] = True
    parts['invalid_geometry'] = ~shapely.is_valid(parts.geometry.array) & ~parts.missing_geometry & ~parts.empty_geometry
    bad = parts[['missing_geometry','empty_geometry','nonfinite_coordinates','out_of_range','invalid_geometry']].any(axis=1)
    parts['polygon_excluded'] = parts.geometry_type.eq('Polygon')
    parts['outside_screening_extent'] = False
    parts['sampling_capped'] = False
    samples = []
    for index, row in parts.loc[~bad & ~parts.polygon_excluded].iterrows():
        geom = row.geometry
        if geom.geom_type == 'Point':
            points = [geom]
        elif geom.geom_type in ('LineString','LinearRing'):
            projected = gpd.GeoSeries([geom],crs=4674).to_crs(5880).iloc[0]
            if not np.isfinite(shapely.get_coordinates(projected)).all():
                parts.loc[index,'outside_screening_extent'] = True
                continue
            requested = max(2, int(np.ceil(projected.length/sample_spacing_m))+1)
            parts.loc[index,'sampling_capped'] = requested > max_line_samples
            positions = np.linspace(0,projected.length,min(requested,max_line_samples))
            interpolated = gpd.GeoSeries([projected.interpolate(v) for v in positions],crs=5880).to_crs(4674)
            # INVARIANT: Assess every original vertex as well as the sampled path.
            points = [shapely.Point(x,y) for x,y in shapely.get_coordinates(geom)] + list(interpolated)
        else:
            parts.loc[index,'outside_screening_extent'] = True
            continue
        for point in points:
            if not (-80 <= point.x <= -25 and -40 <= point.y <= 10):
                parts.loc[index,'outside_screening_extent'] = True
            else:
                samples.append({'component_index':index,'geometry':point})
    defaults = {'sample_count':0,'outside_brazil_samples':0,'offshore_samples':0,'far_offshore_samples':0,'foreign_land_samples':0,
                'uf_mismatch_samples':0,'municipality_mismatch_samples':0,
                'coast_distance_max_m':np.nan,'country_distance_max_m':np.nan,'intersected_municipalities':''}
    for key,value in defaults.items():
        parts[key] = value
    if samples:
        sf = gpd.GeoDataFrame(samples,crs=4674)
        flags = evaluate_samples(sf,municipalities,land,coastline,coast_tolerance_m,border_tolerance_m)
        flags['component_index'] = sf.component_index.to_numpy()
        declared = parts.loc[sf.component_index,'declared_uf'].to_numpy()
        flags['uf_mismatch'] = [bool(uf and states and uf not in states.split('|')) for uf,states in zip(declared,flags.states)]
        declared_muni = parts.loc[sf.component_index,'declared_municipality'].to_numpy()
        flags['municipality_mismatch'] = [bool(code and codes and code not in codes.split('|')) for code,codes in zip(declared_muni,flags.municipalities)]
        grouped = flags.groupby('component_index')
        summaries = pd.DataFrame({'sample_count':grouped.size(),'outside_brazil_samples':grouped.in_brazil.agg('size')-grouped.in_brazil.sum(),'offshore_samples':grouped.offshore.sum(),
            'far_offshore_samples':grouped.far_offshore.sum(),'foreign_land_samples':grouped.foreign_land.sum(),
            'uf_mismatch_samples':grouped.uf_mismatch.sum(),'municipality_mismatch_samples':grouped.municipality_mismatch.sum(),
            'coast_distance_max_m':grouped.coast_distance_m.max(),'country_distance_max_m':grouped.country_distance_m.max(),
            'intersected_municipalities':joined_memberships(flags, 'component_index', ['municipalities']).municipalities.map(lambda codes: '|'.join(sorted(set(codes.split('|')) - {''})))})
        for column in summaries:
            parts.loc[summaries.index,column] = summaries[column]
    print('Classifying component eligibility', flush=True)
    statuses, all_reasons, eligible = [], [], []
    for index,row in parts.iterrows():
        reasons = [field for field in ('missing_geometry','empty_geometry','nonfinite_coordinates','out_of_range','invalid_geometry','outside_screening_extent') if row[field]]
        if row.polygon_excluded:
            status = 'polygon_display_excluded'
        elif reasons:
            status = 'quarantined_invalid_location'
        elif row.foreign_land_samples:
            reasons.append('foreign_land');status = 'quarantined_outside_brazil'
        elif row.far_offshore_samples and not row.marine_signal:
            reasons.append('far_offshore');status = 'quarantined_offshore'
        elif row.offshore_samples and row.marine_signal:
            reasons.append('marine_description_signal');status = 'possible_marine_review'
        elif row.offshore_samples:
            reasons.append('coastal_uncertainty');status = 'coastal_review'
        elif row.outside_brazil_samples:
            reasons.append('border_uncertainty');status = 'border_review'
        elif row.uf_mismatch_samples or row.municipality_mismatch_samples or row.equal_axes or row.sampling_capped:
            status = 'administrative_or_coordinate_review'
        else:
            status = 'eligible_unverified'
        if row.uf_mismatch_samples: reasons.append('uf_mismatch')
        if row.municipality_mismatch_samples: reasons.append('municipality_mismatch')
        if row.equal_axes: reasons.append('equal_coordinate_axes')
        if row.sampling_capped: reasons.append('line_sampling_capped')
        statuses.append(status);all_reasons.append('|'.join(reasons))
        eligible.append(status in ('eligible_unverified','possible_marine_review','coastal_review','border_review','administrative_or_coordinate_review'))
    parts['location_status'] = statuses
    parts['reasons'] = all_reasons
    parts['map_eligible'] = eligible
    return parts


def run(ctx):
    cfg = ctx.config['location_qa']
    if ctx.municipality:
        raise WorkflowError('Location QA is national; omit --municipality and use a national project config.')
    source = ctx.require(ctx.path('location_qa','source'))
    root = ctx.path('location_qa','references')
    if not (root/'manifest.json').is_file():
        raise WorkflowError('Missing local references manifest.json. Run .venv/bin/python datasets/shared/scripts/acquire_location_references.py explicitly, then rerun QA.')
    manifest = json.loads((root/'manifest.json').read_text())
    references = {}
    for name in ('municipalities','land','coastline'):
        entry = manifest[name]; path = ctx.require(root/entry['path'])
        if fingerprint(path) != entry['sha256']:
            raise WorkflowError('Reference checksum changed; explicitly reacquire: '+str(path))
        references[name] = gpd.read_file('zip://'+str(path))
    frame = gpd.read_parquet(source) if source.suffix=='.parquet' else gpd.read_file(source)
    missing_columns = {'id_projeto_investimento','vl_investimento_previsto_total'} - set(frame.columns)
    if missing_columns:
        raise WorkflowError('Obrasgov QA source missing required fields: '+', '.join(sorted(missing_columns)))
    source_hash = fingerprint(source)
    options = {key:cfg[key] for key in ('coast_tolerance_m','border_tolerance_m','sample_spacing_m','max_line_samples')}
    parts = audit(frame, **references, **options)
    stage = 'obrasgov-location-qa'
    original = frame.copy(); original['source_row'] = np.arange(len(frame))
    grouped = parts.groupby('source_row')
    original['component_count'] = grouped.size().reindex(original.source_row).to_numpy()
    original['eligible_components'] = grouped.map_eligible.sum().reindex(original.source_row).to_numpy()
    original['location_statuses'] = grouped.location_status.agg(lambda v:'|'.join(sorted(set(v)))).reindex(original.source_row).to_numpy()
    original['location_coverage'] = np.where(original.eligible_components.eq(0),'no_eligible_location',np.where(original.eligible_components.eq(original.component_count),'all_components_eligible','mixed_components'))
    print('Writing complete audit and map derivatives', flush=True)
    ctx.write_geo(original,stage,'source_audit')
    ctx.write_geo(parts,stage,'component_audit')
    attributes = pd.DataFrame(frame.drop(columns='geometry')).reset_index(drop=True); attributes['source_row'] = attributes.index
    export = parts.merge(attributes,on='source_row',validate='many_to_one')
    clean = export[export.map_eligible].copy()
    quarantine = export[export.location_status.str.startswith('quarantined_')].copy()
    ctx.write_geo(clean,stage,'map_components')
    ctx.write_geo(quarantine,stage,'quarantined_components')
    review = pd.DataFrame(export[export.location_status.ne('eligible_unverified')].drop(columns='geometry'))
    ctx.write_table(review,stage,'review_table')
    out = ctx.root/'outputs/maps/obrasgov-location-qa';out.mkdir(parents=True,exist_ok=True)
    temp = out/'locations.tmp.gpkg';temp.unlink(missing_ok=True)
    clean.to_file(temp,layer='map_components',driver='GPKG')
    if len(quarantine): quarantine.to_file(temp,layer='quarantined_components',driver='GPKG')
    temp.replace(out/'locations.gpkg')
    review.to_csv(out/'review.csv',index=False)
    money = pd.to_numeric(original.vl_investimento_previsto_total,errors='coerce')
    investments = {}
    for key,index in original.groupby('location_coverage').groups.items():
        values = money.loc[index]
        investments[key] = {'source_rows':len(index),'known_investment_brl':float(values.sum(min_count=1)) if values.notna().any() else None,'missing_investment_rows':int(values.isna().sum())}
    budget = pd.DataFrame({'project_id':frame.id_projeto_investimento,'amount':money})
    budget_groups = budget.groupby('project_id').amount
    distinct_amounts = budget_groups.nunique()
    consistent = budget_groups.first().loc[distinct_amounts.eq(1)]
    project_budgets = {'distinct_project_ids':int(budget.project_id.nunique()),
                      'consistent_amount_project_ids':len(consistent),
                      'conflicting_amount_project_ids':int(distinct_amounts.gt(1).sum()),
                      'all_missing_amount_project_ids':int(distinct_amounts.eq(0).sum()),
                      'consistent_project_amount_brl':float(consistent.sum(min_count=1)) if len(consistent) else None,
                      'source_row_sum_is_not_unique_project_budget':True}
    assert len(original) == len(frame) and parts.component_id.is_unique
    assert len(clean)+len(quarantine)+int(parts.polygon_excluded.sum()) == len(parts)
    if fingerprint(source) != source_hash:
        raise WorkflowError('Source changed during QA run; do not use this output.')
    contract = {'policy_version':POLICY_VERSION,'source_sha256':source_hash,'references':manifest,'parameters':options,'code_sha256':fingerprint(__file__)}
    result = {'status':'completed','contract':contract,'source_records':len(frame),'duplicate_project_id_rows':int(frame.id_projeto_investimento.duplicated().sum()),
        'components':len(parts),'map_components':len(clean),'quarantined_components':len(quarantine),
        'component_status_counts':parts.location_status.value_counts().to_dict(),
        'quarantined_source_rows':int(quarantine.source_row.nunique()),'quarantined_project_ids':int(quarantine.project_id.nunique()),
        'offshore_project_ids':int(parts.loc[parts.offshore_samples.gt(0),'project_id'].nunique()),
        'far_offshore_project_ids':int(parts.loc[parts.far_offshore_samples.gt(0),'project_id'].nunique()),
        'unique_project_budget_diagnostic':project_budgets,
        'offshore_components':int(parts.offshore_samples.gt(0).sum()),'far_offshore_components':int(parts.far_offshore_samples.gt(0).sum()),
        'investment_by_source_row_coverage':investments,'source_unchanged':True,'coordinates_corrected':0,
        'municipality_code_check_available':bool(parts.declared_municipality.ne('').any()),
        'limitations':['Generalized coastline and land mask; small unmapped islands can be flagged.','Marine descriptions indicate review, not verified marine validity.','Line paths are sampled; all source vertices are checked.','Retained locations are eligible, not independently validated.','Source rows include duplicate project IDs; row investment totals are not unique-project budgets.'],
        'output_fingerprints':{name:fingerprint(ctx.artifact(stage,name+'.parquet')) for name in ('source_audit','component_audit','map_components','quarantined_components','review_table')}}
    return ctx.report(stage,result)
