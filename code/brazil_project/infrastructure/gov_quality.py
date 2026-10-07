"""Read-only national Obrasgov/census quality audit; no coordinate or method fixes.

This new methodological diagnostic consumes verified frozen artifacts, not a
claim that their old processing producers match the current whole package.
"""
from datetime import date
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from brazil_project.io import WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint
from brazil_project.report_engine import report_lock

STAGE = 'gov-data-quality'
POLICY = 'national-quality-audit-v1'


def audit_locations(source, components, shared_threshold=25):
    """Audit every component; identify exact point-coordinate sharing by project ID.

    INVARIANT: A shared coordinate is a review signal, not a geocoding correction,
    exclusion or proof of an administrative address. Counts explicitly distinguish
    source rows, projects, components and coordinate sites.
    """
    if not isinstance(shared_threshold, int) or shared_threshold < 2:
        raise WorkflowError('shared_coordinate_threshold must be an integer >= 2.')
    required = {'component_id', 'source_row', 'project_id', 'geometry', 'geometry_type',
                'location_status', 'map_eligible', 'primary_state_excluded', 'final_map_eligible'}
    if not required.issubset(components):
        raise WorkflowError('Frozen component audit lacks: '+', '.join(sorted(required-set(components))))
    if components.crs is None or components.crs.to_epsg() != 4674:
        raise WorkflowError('Component coordinates must have declared EPSG:4674; do not infer CRS.')
    if components.component_id.isna().any() or components.component_id.duplicated().any():
        raise WorkflowError('Component IDs must be unique and nonmissing.')
    if 'id_projeto_investimento' not in source or source.id_projeto_investimento.isna().any():
        raise WorkflowError('Source project IDs must be present; missing IDs cannot be silently removed.')
    ids = source.id_projeto_investimento.astype(str).reset_index(drop=True)
    ix = pd.to_numeric(components.source_row, errors='coerce')
    if (ix.isna().any() or (ix % 1).ne(0).any() or (ix < 0).any() or (ix >= len(source)).any()):
        raise WorkflowError('Component source rows do not index the exact frozen source.')
    if set(ix.astype(int)) != set(range(len(source))):
        raise WorkflowError('Component audit must account for every original source row.')
    if not np.array_equal(ids.iloc[ix.astype(int)].to_numpy(), components.project_id.astype(str).to_numpy()):
        raise WorkflowError('Component project IDs disagree with source-row identities.')
    for flag in ('map_eligible', 'primary_state_excluded', 'final_map_eligible'):
        if components[flag].isna().any() or not components[flag].isin([True, False]).all():
            raise WorkflowError('Missing or invalid eligibility flag: '+flag)
    expected = components.map_eligible.astype(bool) & ~components.primary_state_excluded.astype(bool)
    if not expected.eq(components.final_map_eligible).all():
        raise WorkflowError('Final eligibility does not preserve the approved policy.')

    work = components.copy()
    work['project_id'] = work.project_id.astype(str)
    for flag in ('map_eligible', 'primary_state_excluded', 'final_map_eligible'):
        work[flag] = work[flag].astype(bool)
    actual_types = work.geometry.geom_type.fillna('Missing')
    if not actual_types.eq(work.geometry_type.fillna('Missing')).all():
        raise WorkflowError('Recorded geometry types disagree with actual geometry.')
    point_mask = actual_types.eq('Point') & work.geometry.notna() & ~work.geometry.is_empty
    points = work.loc[point_mask].copy()
    points['longitude'] = points.geometry.x
    points['latitude'] = points.geometry.y
    valid = (np.isfinite(points.longitude) & np.isfinite(points.latitude)
             & points.longitude.between(-180, 180) & points.latitude.between(-90, 90))
    invalid_points = int((~valid).sum())
    points = points.loc[valid].copy()
    # WHY: Exact supplied x/y coordinates, not rounded bins or snapped network
    # nodes; deduplication here removes taxonomy/component repetition only.
    points['coordinate_key'] = [float(x if x else 0).hex()+'|'+float(y if y else 0).hex()
                                for x, y in zip(points.longitude, points.latitude)]
    unique = points.drop_duplicates(['project_id', 'coordinate_key']).copy()
    sites = unique.groupby('coordinate_key', sort=True).agg(
        longitude=('longitude', 'first'), latitude=('latitude', 'first'),
        distinct_projects=('project_id', 'nunique')).reset_index()
    component_counts = points.groupby('coordinate_key').size()
    sites['point_components'] = sites.coordinate_key.map(component_counts).astype(int)
    eligible_unique = points.loc[points.final_map_eligible].drop_duplicates(['project_id', 'coordinate_key'])
    eligible_sites = eligible_unique.groupby('coordinate_key').project_id.nunique()
    sites['eligible_distinct_projects'] = sites.coordinate_key.map(eligible_sites).fillna(0).astype(int)
    sites['review_shared_coordinate'] = sites.distinct_projects >= shared_threshold
    sites = sites.sort_values(['distinct_projects', 'coordinate_key'], ascending=[False, True]).reset_index(drop=True)
    unique['site_project_count'] = unique.coordinate_key.map(sites.set_index('coordinate_key').distinct_projects)
    unique['shared_coordinate'] = unique.site_project_count >= shared_threshold

    projects = pd.DataFrame({'project_id': sorted(set(ids))})
    states = source.assign(project_id=ids.to_numpy()).groupby('project_id').uf_principal.agg(
        lambda values: '|'.join(sorted(set(str(v).strip().upper() for v in values.dropna() if str(v).strip()))))
    projects['state'] = projects.project_id.map(states).fillna('')
    projects['state'] = projects.state.replace('', 'Missing')
    projects.loc[projects.state.str.contains('|', regex=False), 'state'] = 'Conflicting'
    checks = {
        'has_valid_point': set(unique.project_id),
        'has_eligible_point': set(eligible_unique.project_id),
        'has_shared_point': set(unique.loc[unique.shared_coordinate, 'project_id']),
        'has_nonshared_point': set(unique.loc[~unique.shared_coordinate, 'project_id']),
        'has_eligible_nonshared_point': set(eligible_unique.loc[
            eligible_unique.coordinate_key.map(sites.set_index('coordinate_key').distinct_projects).lt(shared_threshold), 'project_id']),
        'has_line': set(work.loc[actual_types.isin(['LineString', 'LinearRing']), 'project_id']),
        'has_polygon': set(work.loc[actual_types.eq('Polygon'), 'project_id']),
        'has_no_eligible_component': set(ids)-set(work.loc[work.final_map_eligible, 'project_id']),
    }
    for flag, members in checks.items():
        projects[flag] = projects.project_id.isin(members)
    projects['only_shared_valid_points'] = projects.has_valid_point & ~projects.has_nonshared_point
    projects['only_shared_eligible_points'] = projects.has_eligible_point & ~projects.has_eligible_nonshared_point
    by_state = projects.groupby('state').agg(
        distinct_projects=('project_id', 'size'), valid_point_projects=('has_valid_point', 'sum'),
        eligible_point_projects=('has_eligible_point', 'sum'), shared_point_projects=('has_shared_point', 'sum'),
        only_shared_point_projects=('only_shared_valid_points', 'sum'),
        eligible_nonshared_point_projects=('has_eligible_nonshared_point', 'sum'),
        no_eligible_component_projects=('has_no_eligible_component', 'sum')).reset_index()
    by_state['shared_point_pct'] = (100*by_state.shared_point_projects/by_state.valid_point_projects.where(by_state.valid_point_projects>0))
    by_state['only_shared_point_pct'] = (100*by_state.only_shared_point_projects/by_state.valid_point_projects.where(by_state.valid_point_projects>0))
    rows = []
    for threshold in sorted(set([2, 5, 10, 25, 50, 100, shared_threshold])):
        selected = set(sites.loc[sites.distinct_projects >= threshold, 'coordinate_key'])
        members = unique.loc[unique.coordinate_key.isin(selected)]
        count = members.project_id.nunique()
        rows.append({'Distinct projects at one exact coordinate': threshold,
                     'Coordinate sites meeting threshold': len(selected),
                     'Projects with at least one such point': count,
                     'Share of valid-point projects (%)': 100*count/len(checks['has_valid_point']) if checks['has_valid_point'] else np.nan})
    summary = [
        ('Original source rows', len(source), 'source rows'),
        ('Distinct original projects', len(projects), 'project IDs'),
        ('All decomposed geometries', len(work), 'components'),
        ('Point geometries', int(actual_types.eq('Point').sum()), 'components'),
        ('Finite world-range point coordinates', len(points), 'components'),
        ('Distinct exact coordinate sites', len(sites), 'coordinate sites'),
        ('Projects with a valid point', len(checks['has_valid_point']), 'project IDs'),
        ('Projects with an eligible point after existing rules', len(checks['has_eligible_point']), 'project IDs'),
        ('Projects with at least one shared-coordinate point', len(checks['has_shared_point']), 'project IDs'),
        ('Projects whose valid points are all shared', int(projects.only_shared_valid_points.sum()), 'project IDs'),
        ('Projects with an eligible nonshared point', len(checks['has_eligible_nonshared_point']), 'project IDs'),
        ('Existing baseline map-eligible components', int(work.map_eligible.sum()), 'components'),
        ('Existing primary-state exclusions', int(work.primary_state_excluded.sum()), 'components'),
        ('Existing final map-eligible components', int(work.final_map_eligible.sum()), 'components'),
    ]
    geometry = work.groupby(['geometry_type', 'location_status'], dropna=False).agg(
        components=('component_id', 'size'), distinct_projects=('project_id', 'nunique'),
        eligible_components=('final_map_eligible', 'sum')).reset_index()
    examples = []
    # CONTRACT: Examples are source text for manual review, not automatic location
    # truth inferred from a place name. Preserve all records in local audit tables.
    for key in sites.head(12).coordinate_key:
        sample = points.loc[points.coordinate_key.eq(key), ['project_id', 'source_row']].drop_duplicates('project_id').head(3)
        site = sites.loc[sites.coordinate_key.eq(key)].iloc[0]
        for _, row in sample.iterrows():
            original = source.iloc[int(row.source_row)]
            examples.append({'longitude': site.longitude, 'latitude': site.latitude,
                             'distinct_projects_at_coordinate': int(site.distinct_projects),
                             'project_id': row.project_id, 'reported_state': original.get('uf_principal'),
                             'project_name': original.get('desc_nome'), 'reported_type': original.get('tipo'),
                             'responsible_organisation': original.get('organizacao_resp'),
                             'interpretation': 'Unverified shared source coordinate; review provider record.'})
    metadata = {'shared_coordinate_threshold': shared_threshold,
                'valid_point_components': len(points), 'invalid_nonempty_point_components': invalid_points,
                'distinct_coordinate_sites': len(sites), 'valid_point_projects': len(checks['has_valid_point']),
                'eligible_point_projects': len(checks['has_eligible_point']),
                'shared_point_projects': len(checks['has_shared_point']),
                'only_shared_point_projects': int(projects.only_shared_valid_points.sum()),
                'eligible_nonshared_point_projects': len(checks['has_eligible_nonshared_point']),
                'max_projects_at_one_coordinate': int(sites.distinct_projects.max()) if len(sites) else 0,
                'point_coordinates_corrected': 0, 'new_exclusions': 0,
                'shared_coordinates_are_review_flags_not_confirmed_errors': True}
    return {'tables': {'location_summary': pd.DataFrame(summary, columns=['Measure', 'Count', 'Unit']),
                       'location_by_state': by_state, 'geometry_summary': geometry,
                       'coordinate_sites': sites, 'shared_coordinate_by_state': by_state,
                       'shared_coordinate_thresholds': pd.DataFrame(rows),
                       'point_project_coverage': projects, 'location_examples': pd.DataFrame(examples)},
            'metadata': metadata}


def verify_frozen_inputs(ctx):
    """Verify the complete saved QA/filter lineage without rerunning screening.

    COMPATIBILITY: A quality audit deliberately inspects the existing frozen
    snapshot. Do not require an old national producer's whole-package code hash
    to match newly added audit code; bind all its declared source/output bytes
    and relevant QA implementation hashes instead, and record this distinction.
    """
    required = [ctx.root/'data/intermediate/obrasgov-location-qa/report.json',
                ctx.root/'data/intermediate/obrasgov-primary-state-filter/report.json']
    qa, filtered = [json.loads(ctx.require(p).read_text()) for p in required]
    if qa.get('status') != 'completed' or filtered.get('status') != 'completed':
        raise WorkflowError('National data-quality audit requires completed frozen QA and primary-state filter artifacts. Run obrasgov explicitly first.')
    if qa['contract'].get('policy_version') != '1.0' or filtered.get('policy') != 'exclude_entirely_outside_primary_state_v1':
        raise WorkflowError('Frozen quality policies differ from the documented approved national policies.')
    expected = {p: fingerprint(p) for p in required}
    def bind(path, digest):
        path = Path(path).resolve()
        if path in expected and expected[path] != digest:
            raise WorkflowError('Contradictory frozen fingerprints for '+str(path))
        expected[path] = digest
    source = ctx.require(ctx.path('location_qa', 'source'))
    bind(source, qa['contract']['source_sha256'])
    bind(ctx.root/'code/brazil_project/infrastructure/location_qa.py', qa['contract']['code_sha256'])
    bind(ctx.root/'code/scripts/filter_obras_primary_state.py', filtered['script_sha256'])
    for record in qa['contract']['references'].values():
        p = (ctx.path('location_qa', 'references')/record['path']).resolve()
        if not p.is_relative_to(ctx.root):
            raise WorkflowError('Frozen reference path escapes the project: '+record['path'])
        bind(p, record['sha256'])
    for name, digest in qa.get('output_fingerprints', {}).items():
        bind(ctx.root/'data/intermediate/obrasgov-location-qa'/(name+'.parquet'), digest)
    for relative, digest in filtered['inputs'].items():
        p = (ctx.root/relative).resolve()
        if not p.is_relative_to(ctx.root):
            raise WorkflowError('Frozen manifest path escapes the project: '+relative)
        bind(p, digest)
    for name, digest in filtered['output_sha256'].items():
        bind(ctx.root/'data/intermediate/obrasgov-primary-state-filter'/(name+'.parquet'), digest)
    component = ctx.root/'data/intermediate/obrasgov-primary-state-filter/component_audit.parquet'
    if filtered['inputs'].get('data/processed/obrasgov/projects_st.gpkg') != qa['contract']['source_sha256'] and ctx.path('location_qa', 'source') == ctx.root/'data/processed/obrasgov/projects_st.gpkg':
        raise WorkflowError('QA and filter source fingerprints differ.')
    for p, digest in expected.items():
        if fingerprint(ctx.require(p)) != digest:
            raise WorkflowError('Frozen source/artifact changed; rerun its documented processing stage: '+str(p))
    return source, component, expected, qa, filtered


def write_location_figures(tables, metadata, municipalities, outdir):
    """Visualise national location completeness and exact-coordinate sharing."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    figures = {}
    def save(fig, name):
        fig.savefig(outdir/name, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig); figures[name] = outdir/name
    sites = tables['coordinate_sites']
    extent = sites.longitude.between(-80, -25) & sites.latitude.between(-40, 10)
    visible = sites.loc[extent]
    shared = visible.loc[visible.review_shared_coordinate]
    fig, ax = plt.subplots(figsize=(10, 10))
    display = municipalities.to_crs(4674).copy()
    display.geometry = display.geometry.simplify(.025, preserve_topology=True)
    display.plot(ax=ax, color='#e9efeb', edgecolor='white', linewidth=.1)
    ax.scatter(visible.longitude, visible.latitude, s=1, alpha=.15, c='#617e78', rasterized=True, label='Distinct source coordinate sites')
    ax.scatter(shared.longitude, shared.latitude, s=8+8*np.log10(shared.distinct_projects),
               alpha=.65, c='#c54b36', rasterized=True,
               label=f'At least {metadata["shared_coordinate_threshold"]} project IDs at one coordinate')
    ax.set(xlim=(-80, -25), ylim=(-40, 10), xlabel='Longitude (degrees)', ylabel='Latitude (degrees)',
           title='National Obrasgov point-coordinate sharing\nReview signals; original coordinates unchanged')
    ax.legend(loc='lower left', fontsize=8)
    ax.set_aspect(1.05)
    fig.text(.12, .025, f'All finite world-range point sites, including existing quarantined sites. {int((~extent).sum()):,} sites outside this viewport omitted.\nLines, polygons, empty and invalid points omitted. Shared coordinates do not establish an error or a facility location.', fontsize=8)
    save(fig, 'location-overview.png')

    states = tables['shared_coordinate_by_state'].sort_values('shared_point_pct')
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.barh(states.state, states.shared_point_pct, color='#526f80', label='At least one shared point')
    ax.barh(states.state, states.only_shared_point_pct, color='#ba6349', label='All valid points shared')
    ax.set(xlim=(0, 100), xlabel='Distinct valid-point projects (%)',
           title=f'Projects using coordinates shared by ≥{metadata["shared_coordinate_threshold"]} project IDs')
    ax.legend(loc='lower right', fontsize=8)
    save(fig, 'shared-coordinates-by-state.png')

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    thresholds = tables['shared_coordinate_thresholds']
    axes[0].plot(thresholds['Distinct projects at one exact coordinate'], thresholds['Share of valid-point projects (%)'], 'o-', color='#526f80')
    axes[0].set(xscale='log', xlabel='Distinct project IDs sharing one exact coordinate', ylabel='Projects with ≥1 such point (%)', title='Sensitivity to the review threshold')
    if len(sites):
        axes[1].hist(np.log10(sites.distinct_projects), bins=25, color='#ba6349')
        axes[1].set(yscale='log', xlabel='log10(distinct project IDs per coordinate)', ylabel='Coordinate sites (log scale)', title='Exact coordinate multiplicity')
    fig.suptitle('Coordinate concentration: distinct projects and distinct sites have different denominators')
    fig.tight_layout()
    save(fig, 'shared-coordinate-distribution.png')

    summary = tables['location_summary']
    labels = ['Distinct original projects', 'Projects with a valid point',
              'Projects with an eligible point after existing rules', 'Projects with an eligible nonshared point']
    counts = [int(summary.loc[summary.Measure.eq(n), 'Count'].iloc[0]) for n in labels]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.barh(['All project IDs', 'At least one finite world-range point', 'At least one existing map-eligible point',
             f'At least one eligible point shared by <{metadata["shared_coordinate_threshold"]} IDs'], counts, color='#526f80')
    for i, value in enumerate(counts):
        ax.text(value, i, f' {value:,}', va='center', fontsize=9)
    ax.set(xlim=(0, max(counts)*1.16), xlabel='Distinct project IDs', title='Point-distance study coverage: a quality review, not a new filter')
    save(fig, 'point-project-coverage.png')
    return figures


def run(ctx):
    """Publish national audit tables/figures only; original data remain immutable."""
    if ctx.municipality:
        raise WorkflowError('gov-data-quality is national-only; omit --municipality.')
    from brazil_project.infrastructure.gov_quality_attributes import audit_attributes, write_attribute_figures
    from brazil_project.infrastructure.gov_quality_census import audit_census, write_census_figures
    cfg = ctx.config.get('gov_quality', {})
    as_of = cfg.get('as_of_date')
    try:
        date.fromisoformat(as_of)
    except (TypeError, ValueError):
        raise WorkflowError('gov_quality.as_of_date must be an explicit ISO date YYYY-MM-DD.')
    with report_lock(ctx.root/'.cache/processing-locks/gov-data-quality.lock'):
        print('Verifying frozen national source and location-QA artifacts', flush=True)
        source_path, component_path, expected, qa, filtered = verify_frozen_inputs(ctx)
        source = (gpd.read_parquet(source_path).drop(columns='geometry') if source_path.suffix == '.parquet'
                  else pd.DataFrame(gpd.read_file(source_path, ignore_geometry=True)))
        source = source.reset_index(drop=True)
        parts = gpd.read_parquet(component_path)
        print('Auditing national project identities, categories, dates and investments', flush=True)
        attributes = audit_attributes(source, as_of)
        print('Auditing source coordinates and exact-coordinate concentration', flush=True)
        locations = audit_locations(source, parts, cfg.get('shared_coordinate_threshold', 25))
        print('Auditing census coverage and income/race linkage prerequisites', flush=True)
        census = audit_census(ctx)
        tables = {**attributes['tables'], **locations['tables'], **census['tables']}
        for record in census['metadata']['input_fingerprints']:
            expected[ctx.root/record['path']] = record['sha256']
        constraints = [
            ('Point proximity', 'Exploratory only', 'Shared coordinates and remaining positional uncertainty require provider review; no service interpretation.'),
            ('Network distance', 'Not computed', 'No network acquisition or routing is performed by this audit.'),
            ('Investment-weighted distance', 'Hold for quality review', 'Planned values, repeated IDs and tiny amounts are not realised investment.'),
            ('Historical investment effects', 'Not supported by this snapshot alone', 'Registration/planned dates do not replace verified actual construction or opening dates.'),
            ('Income-adjusted racial comparison', 'Neighbourhood-level only', 'Area mean income is not the joint distribution of individual race and income.'),
            ('Coordinate/category corrections', 'Not performed', 'Review flags are retained; verified provider evidence is required for corrections.'),
        ]
        tables['linkage_constraints'] = pd.DataFrame(constraints, columns=['Proposed use', 'Readiness', 'Reason'])
        # CONTRACT: Remove completion first. An interrupted write cannot masquerade
        # as a new coherent audit; Markdown publication remains independently protected.
        ctx.artifact(STAGE, 'report.json').unlink(missing_ok=True)
        outputs = {}
        for name, frame in tables.items():
            if len(frame):
                p = ctx.write_table(frame, STAGE, name)
                outputs[str(p.relative_to(ctx.root))] = fingerprint(p)
        outdir = ctx.root/'outputs/figures/gov-data-quality'
        municipalities_path = ctx.require(ctx.path('location_qa', 'references')/qa['contract']['references']['municipalities']['path'])
        figures = write_location_figures(locations['tables'], locations['metadata'],
                                        gpd.read_file('zip://'+str(municipalities_path)), outdir)
        figures.update(write_attribute_figures(attributes['tables'], attributes['metadata'], outdir))
        figures.update(write_census_figures(census['tables'], census['metadata'], outdir))
        figures = {name: Path(path) for name, path in figures.items()}
        for p, digest in expected.items():
            if fingerprint(p) != digest:
                raise WorkflowError('Frozen quality-audit input changed during execution: '+str(p))
        table_names = [n for n, frame in tables.items() if len(frame)]
        warnings = ['Shared source coordinates do not certify individual infrastructure locations.',
                    'Current registered project locations and 2010/2022 census demographics have different observation times.',
                    'Income and racial composition are aggregate measures; no individual or causal inference is validated.',
                    'No coordinates, categories, budgets, dates, census values or approved exclusions were changed.']
        result = {'status': 'completed', 'scientific_status': 'diagnostic screening; provider and methodological review required',
                  'policy': POLICY, 'scope': 'Brazil', 'as_of_date': as_of,
                  'source_rows': len(source), 'distinct_projects': int(source.id_projeto_investimento.nunique()),
                  'geometry_components': len(parts), 'tables': table_names,
                  'attributes': attributes['metadata'], 'locations': locations['metadata'], 'census': census['metadata'],
                  'figures': {n: str(p.relative_to(ctx.root)) for n, p in figures.items()},
                  'figure_sha256': {n: fingerprint(p) for n, p in figures.items()},
                  'output_sha256': outputs,
                  'contract': {'source': str(source_path.relative_to(ctx.root)),
                               'source_sha256': fingerprint(source_path),
                               'component_source': str(component_path.relative_to(ctx.root)),
                               'inputs': {str(p.relative_to(ctx.root)): h for p, h in expected.items()},
                               'frozen_qa_contract': qa['contract'],
                               'frozen_state_filter_policy': filtered['policy'],
                               'input_mode': 'verified preserved national artifacts; no acquisition or upstream recomputation'},
                  'warnings': warnings, 'new_exclusions': 0, 'source_coordinates_corrected': 0,
                  'analytical_models_fitted': False, 'network_acquired': False, 'public_map_updated': False}
        return ctx.report(STAGE, result)
