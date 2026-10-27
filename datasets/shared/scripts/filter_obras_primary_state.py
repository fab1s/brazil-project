"""Exclude entirely outside primary-state components from a separate map derivative.

Run after check_obras_primary_state.py. Original research inputs, the diagnostic
and baseline location QA stay intact; excluded geometry remains auditable.
"""
import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint

STATUSES = {'fully_inside', 'partly_inside_or_boundary_contact', 'entirely_outside',
            'not_assessable_geometry', 'unknown_or_missing_primary_state'}


def apply_filter(components, checks):
    """Preserve every component and record the policy as explicit booleans."""
    if components.component_id.duplicated().any() or checks.component_id.duplicated().any():
        raise WorkflowError('Duplicate component IDs; rerun verified preprocessing.')
    if set(components.component_id) != set(checks.component_id):
        raise WorkflowError('State diagnostic does not cover the exact component bundle.')
    if not set(checks.primary_state_check).issubset(STATUSES):
        raise WorkflowError('Unknown state-check classification; review the diagnostic contract.')
    # CONTRACT: Join stable component IDs, never project IDs (which can repeat).
    result = components.merge(checks[['component_id', 'primary_state_check', 'intersected_states']],
                              on='component_id', validate='one_to_one')
    # WHY: The researcher explicitly requested all entirely-outside components,
    # including other-state and offshore locations; marine signals do not exempt them.
    result['primary_state_excluded'] = result.primary_state_check.eq('entirely_outside')
    result['exclusion_reason'] = result.primary_state_excluded.map({True: 'entirely_outside_reported_primary_state', False: ''})
    # INVARIANT: Keep the baseline decision intact and never reintroduce its
    # quarantined locations or polygons. Partial/boundary hits are not excluded here.
    result['final_map_eligible'] = result.map_eligible & ~result.primary_state_excluded
    return result


def verified_inputs(ctx):
    diagnostic = ctx.root / 'outputs/tables/obrasgov-primary-state'
    summary_path = ctx.require(diagnostic / 'summary.json')
    summary = json.loads(summary_path.read_text())
    report_path = ctx.require(ctx.artifact('obrasgov-location-qa', 'report.json'))
    report = json.loads(report_path.read_text())
    if summary.get('status') != 'completed' or report.get('status') != 'completed':
        raise WorkflowError('Require completed state diagnostic and baseline location QA.')
    expected = {ctx.root / relative: value for relative, value in summary['inputs'].items()}
    expected.update({diagnostic / name: value for name, value in summary['output_sha256'].items()})
    component = ctx.require(ctx.artifact('obrasgov-location-qa', 'component_audit.parquet'))
    source = ctx.require(ctx.path('location_qa', 'source'))
    if expected.get(component) != report['output_fingerprints']['component_audit'] or expected.get(source) != report['contract']['source_sha256']:
        raise WorkflowError('Diagnostic and baseline QA use different inputs; rerun the state check.')
    expected[Path(__file__).with_name('check_obras_primary_state.py')] = summary['script_sha256']
    for path, value in expected.items():
        if fingerprint(ctx.require(path)) != value:
            raise WorkflowError('Changed state-check input/output; rerun diagnostic: ' + str(path))
    # WHY: Record producer manifests themselves so interruption/concurrent input
    # replacement cannot be mistaken for a coherent filter run.
    expected[summary_path] = fingerprint(summary_path)
    expected[report_path] = fingerprint(report_path)
    return component, source, diagnostic / 'components.csv', expected, report


def plot_comparison(export, municipalities, path):
    """Show original valid point locations before/after the additional state rule."""
    before = export[export.map_eligible & export.geometry_type.eq('Point')]
    after = before[before.final_map_eligible]
    removed = before[before.primary_state_excluded]
    display = municipalities.to_crs(export.crs).copy()
    display.geometry = display.geometry.simplify(.03, preserve_topology=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 8), sharex=True, sharey=True)
    for ax, points, title in zip(axes, [before, after], ['Before state exclusion', 'After state exclusion']):
        display.plot(ax=ax, color='#edf1ec', edgecolor='white', linewidth=.1)
        ax.scatter(points.geometry.x, points.geometry.y, s=1, color='#76938d', alpha=.2, rasterized=True)
        ax.set(xlim=(-80, -25), ylim=(-40, 10), xlabel='Longitude', title=f'{title}\n{len(points):,} point components')
        ax.set_aspect(1.035)
    axes[0].scatter(removed.geometry.x, removed.geometry.y, s=8, color='#c54737', alpha=.7, label=f'{len(removed):,} points newly excluded', rasterized=True)
    axes[0].legend(loc='lower left', fontsize=9)
    axes[0].set_ylabel('Latitude')
    fig.suptitle('Obrasgov: removal of components entirely outside their primary state', fontsize=14)
    fig.text(.07, .015, 'Original coordinates; point-only illustration within the national viewport. Lines/polygons omitted.\nBaseline eligibility is preserved; partially intersecting primary-state components remain. Boundary simplification is for display only.', fontsize=9)
    fig.tight_layout(rect=(0, .065, 1, .95))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, facecolor='white')
    plt.close(fig)
    return {'before_point_components': len(before), 'after_point_components': len(after), 'newly_excluded_point_components': len(removed)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='datasets/project.toml')
    args = parser.parse_args()
    ctx = Context(args.config)
    return run(ctx)


def run(ctx):
    component, source, diagnostic, expected, producer = verified_inputs(ctx)
    ref = producer['contract']['references']['municipalities']
    municipality_path = ctx.require(ctx.path('location_qa', 'references') / ref['path'])
    if expected.get(municipality_path) != ref['sha256'] or fingerprint(municipality_path) != ref['sha256']:
        raise WorkflowError('Configured municipal reference differs from state diagnostic; rerun with matching references.')
    parts = gpd.read_parquet(component)
    checks = pd.read_csv(diagnostic, keep_default_na=False, dtype={'component_id': str})
    audited = apply_filter(parts, checks)
    original = gpd.read_parquet(source) if source.suffix == '.parquet' else gpd.read_file(source)
    attributes = pd.DataFrame(original.drop(columns='geometry')).reset_index(drop=True)
    attributes['source_row'] = attributes.index
    export = audited.merge(attributes, on='source_row', validate='many_to_one')
    excluded = export[export.primary_state_excluded].copy()
    kept = export[~export.primary_state_excluded].copy()
    clean = export[export.final_map_eligible].copy()
    stage = 'obrasgov-primary-state-filter'
    report_path = ctx.artifact(stage, 'report.json')
    # CONTRACT: No completed report remains if publication is interrupted.
    report_path.unlink(missing_ok=True)
    for name, frame in [('component_audit', export), ('filtered_components', kept),
                        ('excluded_components', excluded), ('map_components', clean)]:
        ctx.write_geo(frame, stage, name)
    out = ctx.root / 'outputs/maps/obrasgov-primary-state-filter'
    out.mkdir(parents=True, exist_ok=True)
    temporary = out / 'locations.tmp.gpkg'
    temporary.unlink(missing_ok=True)
    clean.to_file(temporary, layer='map_components', driver='GPKG')
    if len(excluded):
        excluded.to_file(temporary, layer='excluded_primary_state', driver='GPKG')
    temporary.replace(out / 'locations.gpkg')
    excluded.drop(columns='geometry').to_csv(out / 'exclusions.csv', index=False)
    figure = ctx.root / 'outputs/figures/obrasgov-location-qa/primary-state-filter.png'
    figure_counts = plot_comparison(export, gpd.read_file('zip://' + str(municipality_path)), figure)
    # INVARIANT: Verify exported identities and geometry, not just row counts.
    for layer, frame in [('map_components', clean), ('excluded_primary_state', excluded)]:
        if not len(frame):
            continue
        exchange = gpd.read_file(out / 'locations.gpkg', layer=layer).set_index('component_id')
        wanted = frame.set_index('component_id')
        if set(exchange.index) != set(wanted.index) or exchange.crs != frame.crs:
            raise WorkflowError('GeoPackage identity/CRS verification failed: ' + layer)
        if not (shapely.to_wkb(exchange.loc[wanted.index].geometry.array) == shapely.to_wkb(wanted.geometry.array)).all():
            raise WorkflowError('GeoPackage altered original component geometry: ' + layer)
    for path, value in expected.items():
        if fingerprint(path) != value:
            raise WorkflowError('Input changed during filtering: ' + str(path))
    fingerprints = {name: fingerprint(ctx.artifact(stage, name + '.parquet')) for name in
                    ('component_audit', 'filtered_components', 'excluded_components', 'map_components')}
    report = {'status': 'completed', 'policy': 'exclude_entirely_outside_primary_state_v1',
              'script_sha256': fingerprint(Path(__file__)),
              'inputs': {str(path.relative_to(ctx.root)): value for path, value in expected.items()},
              'components_before': len(export), 'components_after_state_rule': len(kept),
              'excluded_components': len(excluded), 'excluded_source_rows': int(excluded.source_row.nunique()),
              'excluded_distinct_project_ids': int(excluded.project_id.nunique()),
              'map_components_before': int(export.map_eligible.sum()), 'map_components_after': len(clean),
              'newly_excluded_map_components': int(excluded.map_eligible.sum()),
              'already_absent_from_baseline_map': int((~excluded.map_eligible).sum()),
              'excluded_by_geometry': excluded.geometry_type.value_counts().to_dict(),
              'source_rows_preserved': len(original), 'coordinates_corrected': 0,
              'output_sha256': fingerprints,
              'gis_outputs': {name: fingerprint(out / name) for name in ('locations.gpkg', 'exclusions.csv')},
              'figure': {'path': str(figure.relative_to(ctx.root)), 'sha256': fingerprint(figure), **figure_counts},
              'verification': {'gpkg_map_and_exclusion_identity_crs_and_wkb_exact': True},
              'public_map_updated': False,
              'limitations': ['Primary state can describe a multi-state project; exclusion is a researcher-approved display policy.', 'No original records or investment totals deleted; do not sum repeated component investments.', 'Concurrent runs unsupported; require completed report and matching artifact hashes.']}
    ctx.report(stage, report)
    print(json.dumps({key: report[key] for key in ('excluded_components', 'components_after_state_rule', 'map_components_before', 'map_components_after', 'newly_excluded_map_components')}, indent=2))


if __name__ == '__main__':
    main()
