"""Check complete Obrasgov geometry against its primary state; never filter data."""
import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.location_qa import fingerprint
from scripts.plot_location_qa import verified_plot_inputs


def check_states(parts, states):
    """Boundary-inclusive containment of original components, without tolerances."""
    if parts.crs is None or states.crs is None or parts.crs != states.crs:
        raise WorkflowError('State checks require matching declared coordinate systems.')
    if states.SIGLA_UF.duplicated().any():
        raise WorkflowError('State reference must contain one dissolved geometry per UF.')
    result = parts[['source_row', 'component_id', 'project_id', 'declared_uf', 'geometry_type']].copy()
    result['primary_state_check'] = 'not_assessable_geometry'
    geometry = parts.geometry.array
    usable = ~shapely.is_missing(geometry) & ~shapely.is_empty(geometry) & shapely.is_valid(geometry)
    xy, indices = shapely.get_coordinates(geometry, return_index=True)
    bad = ~np.isfinite(xy).all(axis=1) | (np.abs(xy[:, 0]) > 180) | (np.abs(xy[:, 1]) > 90)
    usable[np.unique(indices[bad])] = False
    known = parts.declared_uf.isin(states.SIGLA_UF)
    result.loc[usable & ~known, 'primary_state_check'] = 'unknown_or_missing_primary_state'
    for _, state in states.iterrows():
        selected = usable & parts.declared_uf.eq(state.SIGLA_UF).to_numpy()
        if not selected.any():
            continue
        shapely.prepare(state.geometry)
        inside = shapely.covers(state.geometry, geometry[selected])
        touches = shapely.intersects(state.geometry, geometry[selected])
        result.loc[selected, 'primary_state_check'] = np.where(inside, 'fully_inside', np.where(touches, 'partly_inside_or_boundary_contact', 'entirely_outside'))
    # WHY: Retain all candidate states on shared boundaries and cross-state paths.
    hits = gpd.sjoin(states[['SIGLA_UF', 'geometry']], parts.loc[usable, ['geometry']], predicate='intersects')
    memberships = hits.groupby('index_right').SIGLA_UF.agg(lambda values: '|'.join(sorted(set(values))))
    result['intersected_states'] = memberships.reindex(result.index, fill_value='')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='project.toml')
    args = parser.parse_args()
    ctx = Context(args.config)
    return run(ctx)


def run(ctx):
    component, reference = verified_plot_inputs(ctx)
    input_hashes = {str(path.relative_to(ctx.root)): fingerprint(path) for path in (component, reference, ctx.path('location_qa', 'source'))}
    parts = gpd.read_parquet(component).reset_index(drop=True)
    municipalities = gpd.read_file('zip://' + str(reference)).to_crs(parts.crs)
    print('Dissolving original IBGE municipalities into 27 state boundaries', flush=True)
    states = municipalities[['SIGLA_UF', 'geometry']].dissolve(by='SIGLA_UF').reset_index()
    if not states.geometry.is_valid.all():
        raise WorkflowError('Invalid dissolved state boundary; review reference without silently repairing it.')
    print('Checking every original point, line and polygon component', flush=True)
    checked = check_states(parts, states)
    for relative, expected in input_hashes.items():
        if fingerprint(ctx.root / relative) != expected:
            raise WorkflowError('Input changed during state check: ' + relative)
    output = ctx.root / 'outputs/tables/obrasgov-primary-state'
    output.mkdir(parents=True, exist_ok=True)
    # CONTRACT: Absence of a completed summary marks interrupted publication.
    (output / 'summary.json').unlink(missing_ok=True)
    checked.to_csv(output / 'components.csv.tmp', index=False)
    (output / 'components.csv.tmp').replace(output / 'components.csv')
    by_state = pd.crosstab(checked.declared_uf, checked.primary_state_check)
    by_state.to_csv(output / 'by-state.csv')
    by_type = pd.crosstab(checked.geometry_type, checked.primary_state_check)
    by_type.to_csv(output / 'by-geometry.csv')
    import matplotlib.pyplot as plt
    bars = by_state.reindex(columns=['entirely_outside', 'partly_inside_or_boundary_contact'], fill_value=0)
    bars = bars.loc[bars.sum(axis=1).gt(0)]
    bars = bars.sort_values('entirely_outside')
    fig, ax = plt.subplots(figsize=(10, 9))
    bars.plot.barh(stacked=True, ax=ax, color=['#c54737', '#1479b8'])
    ax.set_title('Obrasgov geometry versus reported primary state', loc='left', pad=15)
    ax.set_xlabel('Original geometry components (not unique projects)')
    ax.set_ylabel('Reported uf_principal')
    ax.legend(['Entirely outside primary state', 'Partly inside or boundary contact'], loc='lower right', fontsize=9)
    fig.text(.08, .015, 'Diagnostic only: no filtering or coordinate changes. Complete points, lines and polygons; IBGE 2022 boundaries.\nMissing/invalid geometry and unknown states omitted. Multi-state/offshore projects require interpretation.', fontsize=9)
    fig.tight_layout(rect=(0, .055, 1, 1))
    figure = ctx.root / 'outputs/figures/obrasgov-location-qa/primary-state-check.png'
    figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure, dpi=150, facecolor='white')
    plt.close(fig)
    outside = checked[checked.primary_state_check.eq('entirely_outside')]
    summary = {
        'status': 'completed',
        'mode': 'diagnostic_only_no_filtering',
        'reference': 'IBGE municipalities 2022 dissolved by SIGLA_UF; original resolution',
        'predicate': 'covers for fully_inside; intersects for partly_inside_or_boundary_contact; no buffer or coordinate correction',
        'inputs': input_hashes, 'script_sha256': fingerprint(Path(__file__)),
        'source_rows': int(checked.source_row.nunique()), 'components': len(checked),
        'component_counts': checked.primary_state_check.value_counts().to_dict(),
        'affected_source_rows': {key: int(group.source_row.nunique()) for key, group in checked.groupby('primary_state_check')},
        'affected_distinct_project_ids': {key: int(group.project_id.nunique()) for key, group in checked.groupby('primary_state_check')},
        'counts_by_state': by_state.to_dict(orient='index'),
        'counts_by_geometry': by_type.to_dict(orient='index'),
        'entirely_outside_intersecting_other_states': int(outside.intersected_states.ne('').sum()),
        'entirely_outside_intersecting_no_state': int(outside.intersected_states.eq('').sum()),
        'figure': {'path': str(figure.relative_to(ctx.root)), 'sha256': fingerprint(figure)},
        'output_sha256': {name: fingerprint(output / name) for name in ('components.csv', 'by-state.csv', 'by-geometry.csv')},
        'limitations': ['Primary state may describe a lead state in a multi-state project.', 'IBGE 2022 administrative territory is not an offshore licensing boundary.', 'Exact boundary differences can produce partial or outside results.', 'Source rows/project IDs may have multiple components and occur in multiple categories.'],
    }
    (output / 'summary.json.tmp').write_text(json.dumps(summary, indent=2) + '\n')
    (output / 'summary.json.tmp').replace(output / 'summary.json')
    print(json.dumps(summary['component_counts'], indent=2))
    print(output)
    return summary


if __name__ == '__main__':
    main()
