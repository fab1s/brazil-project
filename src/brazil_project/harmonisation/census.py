"""Bidirectional largest-overlap correspondence preserving prepared 2022 geometry."""
import geopandas as gpd
import pandas as pd
import networkx as nx
import numpy as np
import shapely
from brazil_project.io import WorkflowError, keys, lookup_keys, identifiers


def prepare(frame, year, crs=5880, grid=1e-6):
    result = frame[['code_tract', frame.geometry.name]].rename(columns={'code_tract': f'id_{year}'}).to_crs(crs)
    result[f'id_{year}'] = identifiers(result[f'id_{year}'])
    if result[f'id_{year}'].isna().any(): raise WorkflowError('Missing tract identifier')
    # Original geometry rows, including duplicate IDs, remain present.
    # INVARIANT: validity/precision preparation precedes correspondence; no dissolve.
    result.geometry = shapely.make_valid(shapely.set_precision(result.geometry.array, grid, mode="pointwise"))
    return result.reset_index(drop=True)


def largest_overlap(source, target, source_id, target_id):
    left, right = target.sindex.query(source.geometry, predicate='intersects')
    if len(left) == 0:
        return pd.DataFrame(columns=[source_id, target_id])
    overlap = shapely.area(shapely.intersection(source.geometry.array[left], target.geometry.array[right]))
    candidates = pd.DataFrame({'left': left, 'right': right, 'area': overlap})
    # COMPATIBILITY: equal overlaps choose the first target in original row order.
    chosen = candidates.sort_values(['left', 'area', 'right'], ascending=[True, False, True]).drop_duplicates('left')
    return pd.DataFrame({source_id: source.iloc[chosen.left][source_id].to_numpy(),
                         target_id: target.iloc[chosen.right][target_id].to_numpy()})


def correspondence(t2010, t2022):
    fwd = largest_overlap(t2022, t2010, 'id_2022', 'id_2010')
    bwd = largest_overlap(t2010, t2022, 'id_2010', 'id_2022')
    crosswalk = pd.concat([fwd[['id_2010', 'id_2022']], bwd], ignore_index=True).drop_duplicates()
    graph = nx.Graph()
    # igraph numbers components using vertex encounter order; membership is authoritative.
    graph.add_nodes_from('y2010_' + crosswalk.id_2010.astype(str))
    graph.add_nodes_from('y2022_' + crosswalk.id_2022.astype(str))
    graph.add_edges_from(zip('y2010_' + crosswalk.id_2010.astype(str), 'y2022_' + crosswalk.id_2022.astype(str)))
    membership = {node: str(i) for i, component in enumerate(nx.connected_components(graph), 1) for node in component}
    crosswalk['common_id'] = ('y2010_' + crosswalk.id_2010.astype(str)).map(membership).astype('string')
    sizes = crosswalk.groupby('common_id', sort=False).agg(n_2010=('id_2010', 'nunique'), n_2022=('id_2022', 'nunique')).reset_index()
    sizes['relationship'] = np.select([(sizes.n_2010 == 1) & (sizes.n_2022 == 1),
                                      (sizes.n_2010 == 1) & (sizes.n_2022 > 1),
                                      (sizes.n_2010 > 1) & (sizes.n_2022 == 1)],
                                     ['1:1', '2010_to_2022_split', '2010_to_2022_merge'], default='many_to_many')
    l2010 = crosswalk.merge(sizes, on='common_id', validate='many_to_one')
    l2022 = crosswalk[['id_2022', 'common_id']].drop_duplicates().merge(sizes, on='common_id', validate='many_to_one')
    base = t2022.merge(l2022, on='id_2022', how='left', validate='many_to_one')
    base['base_id'] = 't2022_' + base.id_2022
    return crosswalk, l2010, l2022, sizes, base


def scope_where(ctx, id_column):
    if not ctx.municipality:
        return None
    if not ctx.municipality.isdigit():
        raise WorkflowError('municipality must be an IBGE numeric municipality code')
    return f'CAST("{id_column}" AS TEXT) LIKE \'{ctx.municipality}%\''


def run(ctx):
    cfg = ctx.config['census']
    if cfg.get('recompute_harmonisation', False):
        path = ctx.require(ctx.path('census', 'tracts'))
        years = [prepare(gpd.read_file(path, layer=str(year), where=scope_where(ctx, 'code_tract')), year,
                         cfg['crs'], cfg['precision_grid']) for year in (2010, 2022)]
        crosswalk, l2010, l2022, sizes, base = correspondence(*years)
        ctx.write_table(crosswalk, 'harmonisation', 'crosswalk')
        mode = 'recomputed_python_unverified_until_parity_check'
    else:
        path = ctx.require(ctx.path('census', 'baseline_lookup'))
        base = gpd.read_file(ctx.require(ctx.path('census', 'baseline_geometry')), where=scope_where(ctx, 'id_2022'))
        # INVARIANT: include every tract of a selected common area, including cross-municipality groups.
        selected = set(identifiers(base.common_id).dropna())
        l2010 = gpd.read_file(path, layer='2010', ignore_geometry=True)
        l2022 = gpd.read_file(path, layer='2022', ignore_geometry=True)
        if ctx.municipality:
            l2010 = l2010[identifiers(l2010.common_id).isin(selected)]
            l2022 = l2022[identifiers(l2022.common_id).isin(selected)]
            # Density uses the full common-area geometry, then displays selected tracts only.
            full_base = gpd.read_file(ctx.require(ctx.path('census', 'baseline_geometry')), where='common_id IN (' + ','.join(selected) + ')')
            full_base['common_id'] = identifiers(full_base.common_id)
            ctx.write_geo(full_base, 'harmonisation', 'comparison_geometry')
        sizes = pd.read_csv(ctx.require(ctx.path('census', 'baseline_group_sizes')), dtype={'common_id': 'string'})
        sizes = sizes[sizes.common_id.isin(identifiers(l2022.common_id))]
        mode = 'copied_original_correspondence'
    for year, lookup in [(2010, l2010), (2022, l2022)]:
        lookup = lookup.copy()
        lookup[f'id_{year}'] = identifiers(lookup[f'id_{year}'])
        lookup['common_id'] = identifiers(lookup.common_id)
        lookup_keys(lookup, year)
        ctx.write_table(pd.DataFrame(lookup), 'harmonisation', f'lookup_{year}')
    base['common_id'] = identifiers(base.common_id)
    base['id_2022'] = identifiers(base.id_2022)
    sizes['common_id'] = sizes.common_id.astype('string')
    # COMPATIBILITY: imported baseline contains duplicate tract geometries; preserve and report.
    ctx.write_geo(base, 'harmonisation', 'base_geometry_2022')
    ctx.write_table(sizes, 'harmonisation', 'group_sizes')
    return ctx.report('harmonisation', {'mode': mode, 'tracts_2022': len(base), 'groups': len(sizes), 'scope': ctx.municipality or 'Brazil', 'duplicate_base_ids': int(base.id_2022.duplicated().sum())})
