"""Positive-area correspondence and versioned, complete common-area artifacts."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

import geopandas as gpd
import pandas as pd
import networkx as nx
import numpy as np
import shapely
from brazil_project.io import WorkflowError, keys, lookup_keys, identifiers

POLICY = 'positive-area-common-geometry-v1'


def prepare(frame, year, crs=5880, grid=1e-6):
    result = frame[['code_tract', frame.geometry.name]].rename(columns={'code_tract': f'id_{year}'}).to_crs(crs)
    result[f'id_{year}'] = identifiers(result[f'id_{year}'])
    if result[f'id_{year}'].isna().any():
        raise WorkflowError('Missing tract identifier')
    # INVARIANT: all source pieces remain available; only the derived group layer is dissolved.
    result.geometry = shapely.make_valid(shapely.set_precision(result.geometry.array, grid, mode='pointwise'))
    return result.reset_index(drop=True)


def largest_overlap(source, target, source_id, target_id):
    left, right = target.sindex.query(source.geometry, predicate='intersects')
    overlap = shapely.area(shapely.intersection(source.geometry.array[left], target.geometry.array[right]))
    candidates = pd.DataFrame({'left': left, 'right': right, 'area': overlap})
    # METHOD CHANGE: edge/point contacts cannot establish a polygon correspondence.
    candidates = candidates[np.isfinite(candidates.area) & (candidates.area > 0)]
    chosen = candidates.sort_values(['left', 'area', 'right'], ascending=[True, False, True]).drop_duplicates('left')
    return pd.DataFrame({source_id: source.iloc[chosen.left][source_id].to_numpy(),
                         target_id: target.iloc[chosen.right][target_id].to_numpy()})


def grouped_crosswalk(crosswalk, original=None):
    crosswalk = crosswalk[['id_2010', 'id_2022']].drop_duplicates().copy()
    for year in (2010, 2022):
        crosswalk[f'id_{year}'] = identifiers(crosswalk[f'id_{year}'])
    if crosswalk.isna().any().any():
        raise WorkflowError('Crosswalk contains missing tract IDs')
    graph = nx.Graph()
    graph.add_edges_from(zip('y2010_' + crosswalk.id_2010, 'y2022_' + crosswalk.id_2022))
    original_nodes = {}
    if original is not None:
        for cid, part in original.groupby('common_id'):
            original_nodes[frozenset(['y2010_' + v for v in part.id_2010.unique()] +
                                     ['y2022_' + v for v in part.id_2022.unique()])] = str(cid)
    membership = {}
    for component in nx.connected_components(graph):
        # Stable member-derived IDs for new/changed groups; preserve unchanged baseline IDs.
        cid = original_nodes.get(frozenset(component))
        if cid is None:
            cid = 'g_' + hashlib.sha256('\n'.join(sorted(component)).encode()).hexdigest()[:24]
        membership.update({node: cid for node in component})
    crosswalk['common_id'] = ('y2010_' + crosswalk.id_2010).map(membership).astype('string')
    sizes = crosswalk.groupby('common_id', sort=False).agg(n_2010=('id_2010', 'nunique'), n_2022=('id_2022', 'nunique')).reset_index()
    sizes['relationship'] = np.select([(sizes.n_2010 == 1) & (sizes.n_2022 == 1),
                                      (sizes.n_2010 == 1) & (sizes.n_2022 > 1),
                                      (sizes.n_2010 > 1) & (sizes.n_2022 == 1)],
                                     ['1:1', '2010_to_2022_split', '2010_to_2022_merge'], default='many_to_many')
    lookups = [crosswalk[[f'id_{year}', 'common_id']].drop_duplicates().merge(sizes, on='common_id', validate='many_to_one') for year in (2010, 2022)]
    return crosswalk, *lookups, sizes


def attach_base(t2022, lookup):
    base = t2022.merge(lookup, on='id_2022', how='left', validate='many_to_one')
    base['base_id'] = 't2022_' + base.id_2022
    base['part_id'] = base.base_id + '_part_' + (base.groupby('id_2022').cumcount() + 1).astype(str)
    keys(base, 'part_id')
    return base


def correspondence(t2010, t2022):
    fwd = largest_overlap(t2022, t2010, 'id_2022', 'id_2010')
    bwd = largest_overlap(t2010, t2022, 'id_2010', 'id_2022')
    crosswalk, l2010, l2022, sizes = grouped_crosswalk(pd.concat([fwd[['id_2010', 'id_2022']], bwd], ignore_index=True))
    return crosswalk, l2010, l2022, sizes, attach_base(t2022, l2022)


def scope_where(ctx, id_column):
    if not ctx.municipality:
        return None
    if len(ctx.municipality) != 7 or not ctx.municipality.isdigit():
        raise WorkflowError('municipality must be a seven-digit IBGE municipality code')
    return f'CAST("{id_column}" AS TEXT) LIKE \'{ctx.municipality}%\''


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def input_version(ctx, mode):
    cfg = ctx.config['census']
    names = ['tracts'] if mode == 'recomputed_python' else ['tracts', 'baseline_lookup', 'baseline_geometry', 'baseline_group_sizes']
    cache = ctx.root / 'data/intermediate/harmonisation_cache'
    cache.mkdir(parents=True, exist_ok=True)
    checksum_file = cache / 'input_checksums.json'
    records = json.loads(checksum_file.read_text()) if checksum_file.exists() else {}
    inputs = {}
    for name in names:
        path = ctx.require(ctx.path('census', name)); stat = path.stat()
        signature = [stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns]
        previous = records.get(str(path), {})
        digest = previous.get('sha256') if previous.get('signature') == signature else sha256(path)
        records[str(path)] = {'signature': signature, 'sha256': digest}
        inputs[name] = digest
    tmp = checksum_file.with_name('input_checksums.' + uuid.uuid4().hex + '.tmp')
    tmp.write_text(json.dumps(records, indent=2) + '\n'); os.replace(tmp, checksum_file)
    contract = {'policy': POLICY, 'mode': mode, 'inputs': inputs, 'crs': cfg['crs'], 'precision_grid': cfg['precision_grid']}
    version = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
    return version, contract


def read_ids(path, year, ids=None, layer=None, baseline=False):
    column = f'id_{year}' if baseline else 'code_tract'
    if ids is None:
        result = gpd.read_file(path, layer=layer, columns=[column])
    elif not len(ids):
        import pyogrio
        info = pyogrio.read_info(path, layer=layer)
        result = gpd.GeoDataFrame({column: pd.Series(dtype='string')}, geometry=gpd.GeoSeries([], crs=info['crs']))
    else:
        pieces = []
        values = sorted(set(str(v) for v in ids))
        if not all(v.isdigit() for v in values):
            raise WorkflowError('Invalid census tract identifiers')
        for start in range(0, len(values), 15000):
            # Numeric comparison handles both numeric and numeric-text GeoPackage fields.
            where = f'"{column}" IN (' + ','.join(values[start:start+15000]) + ')'
            pieces.append(gpd.read_file(path, layer=layer, where=where, columns=[column]))
        result = pd.concat(pieces, ignore_index=True)
    if baseline:
        result = result.rename(columns={column: f'id_{year}'})
        result[f'id_{year}'] = identifiers(result[f'id_{year}'])
        return result
    return result


def raw_ids(ctx, year):
    frame = gpd.read_file(ctx.require(ctx.path('census', 'tracts')), layer=str(year), columns=['code_tract'], ignore_geometry=True)
    return identifiers(frame.code_tract).drop_duplicates().reset_index(drop=True)


def positive_baseline_edges(ctx, original):
    cfg = ctx.config['census']; accepted = []; rejected = []
    old_ids = original.id_2010.unique()
    for start in range(0, len(old_ids), 10000):
        edges = original[original.id_2010.isin(old_ids[start:start+10000])][['id_2010', 'id_2022']].drop_duplicates()
        old = prepare(read_ids(ctx.path('census', 'tracts'), 2010, edges.id_2010, '2010'), 2010, cfg['crs'], cfg['precision_grid'])
        new = read_ids(ctx.path('census', 'baseline_geometry'), 2022, edges.id_2022, baseline=True).to_crs(cfg['crs'])
        if not set(edges.id_2010).issubset(set(old.id_2010)) or not set(edges.id_2022).issubset(set(new.id_2022)):
            raise WorkflowError('Baseline crosswalk references geometry absent from the source inputs')
        pairs = edges.merge(pd.DataFrame({'id_2010': old.id_2010, 'old_geom': old.geometry.array}), on='id_2010').merge(
            pd.DataFrame({'id_2022': new.id_2022, 'new_geom': shapely.make_valid(new.geometry.array)}), on='id_2022')
        area = shapely.area(shapely.intersection(pairs.old_geom.to_numpy(), pairs.new_geom.to_numpy()))
        pairs['positive'] = np.isfinite(area) & (area > 0)
        good = pairs.groupby(['id_2010', 'id_2022']).positive.any().reset_index()
        accepted.append(good[good.positive][['id_2010', 'id_2022']])
        bad = good[~good.positive][['id_2010', 'id_2022']].copy()
        bad['reason'] = 'no_positive_polygon_overlap'
        rejected.append(bad)
    empty = pd.DataFrame(columns=['id_2010', 'id_2022'])
    return pd.concat(accepted, ignore_index=True) if accepted else empty, pd.concat(rejected, ignore_index=True) if rejected else empty.assign(reason=pd.Series(dtype='string'))


def source_correspondence(ctx, mode, version):
    """Recompute globally; imported scopes select complete original national components."""
    cfg = ctx.config['census']
    cache = ctx.root / 'data/intermediate/harmonisation_cache' / version
    original = None
    selection = 'national'
    if mode == 'validated_original_correspondence':
        original = gpd.read_file(ctx.path('census', 'baseline_lookup'), layer='2010', ignore_geometry=True)
        for column in ['id_2010', 'id_2022', 'common_id']:
            original[column] = identifiers(original[column])
        if original.common_id.isna().any():
            raise WorkflowError('Imported crosswalk has missing common IDs')
        expected_2022 = lookup_keys(original, 2022)
        lookup_keys(original, 2010)
        imported_2022 = gpd.read_file(ctx.path('census', 'baseline_lookup'), layer='2022', ignore_geometry=True)
        actual_2022 = lookup_keys(imported_2022, 2022)
        if set(map(tuple, expected_2022.to_numpy())) != set(map(tuple, actual_2022.to_numpy())):
            raise WorkflowError('Imported year lookups disagree on group membership')
        original_sizes = pd.read_csv(ctx.path('census', 'baseline_group_sizes'), dtype={'common_id': 'string'})
        keys(original_sizes, 'common_id')
        for year in (2010, 2022):
            counts = lookup_keys(original, year).groupby('common_id')[f'id_{year}'].nunique()
            expected = original_sizes.set_index('common_id')[f'n_{year}']
            if set(counts.index) != set(expected.index) or not np.array_equal(counts.reindex(expected.index).to_numpy(), expected.to_numpy()):
                raise WorkflowError('Imported group counts disagree with the original lookup memberships')
        if ctx.municipality:
            display = gpd.read_file(ctx.path('census', 'baseline_geometry'), where=scope_where(ctx, 'id_2022'), ignore_geometry=True)
            selected = set(identifiers(display.common_id).dropna())
            original = original[original.common_id.isin(selected)]
            # Removing edges cannot merge original components, so complete component selection is safe.
            selection = hashlib.sha256('\n'.join(sorted(selected)).encode()).hexdigest()
    cache = cache / selection
    if (cache / 'complete.json').exists():
        completed = json.loads((cache / 'complete.json').read_text())
        if completed.get('version') != version or completed.get('selection') != selection:
            raise WorkflowError('Correspondence cache contract mismatch; remove generated cache: ' + str(cache))
        if 'checksums' not in completed:
            (cache / 'complete.json').unlink()
            return source_correspondence(ctx, mode, version)
        for name, digest in completed['checksums'].items():
            if sha256(cache / (name + '.parquet')) != digest:
                raise WorkflowError('Correspondence cache changed; remove this generated cache and rerun: ' + str(cache))
        return [pd.read_parquet(cache / (name + '.parquet')) for name in ['crosswalk', 'lookup_2010', 'lookup_2022', 'group_sizes', 'rejected_edges']], cache
    if mode == 'recomputed_python':
        # INVARIANT: locality never filters geometry before global matching.
        years = [prepare(read_ids(ctx.path('census', 'tracts'), year, layer=str(year)), year, cfg['crs'], cfg['precision_grid']) for year in (2010, 2022)]
        cross, l10, l22, sizes, _ = correspondence(*years)
        rejected = pd.DataFrame(columns=['id_2010', 'id_2022', 'reason'])
    else:
        valid, rejected = positive_baseline_edges(ctx, original)
        cross, l10, l22, sizes = grouped_crosswalk(valid, original)
    cache.mkdir(parents=True, exist_ok=True)
    for name, frame in zip(['crosswalk', 'lookup_2010', 'lookup_2022', 'group_sizes', 'rejected_edges'], [cross, l10, l22, sizes, rejected]):
        temp = cache / (name + '.' + uuid.uuid4().hex + '.tmp.parquet')
        frame.to_parquet(temp, index=False); os.replace(temp, cache / (name + '.parquet'))
    checksums = {name: sha256(cache / (name + '.parquet')) for name in ['crosswalk', 'lookup_2010', 'lookup_2022', 'group_sizes', 'rejected_edges']}
    temp = cache / ('complete.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps({'version': version, 'selection': selection, 'checksums': checksums})); os.replace(temp, cache / 'complete.json')
    return [cross, l10, l22, sizes, rejected], cache


def dissolved_common_geometry(base, sizes):
    matched = base[base.common_id.notna()][['common_id', 'geometry']].copy()
    matched.geometry = shapely.make_valid(matched.geometry.array)
    result = matched.dissolve(by='common_id', as_index=False).merge(sizes, on='common_id', validate='one_to_one')
    # COMPATIBILITY: transform individual prepared pieces before their equal-area union.
    # Projecting the display union instead changes the numerical density denominator.
    area_geometry = matched.to_crs(6933).dissolve(by='common_id')
    result['area_km2'] = result.common_id.map(area_geometry.area / 1e6)
    keys(result, 'common_id')
    if result.geometry.isna().any() or result.geometry.is_empty.any() or not np.isfinite(result.area_km2).all() or (result.area_km2 <= 0).any():
        raise WorkflowError('A matched common area has no usable polygon geometry')
    return result


def footprint_diagnostics(old, common):
    previous = old[['common_id', 'geometry']].dissolve(by='common_id', as_index=False).rename_geometry('old_geometry')
    joined = pd.DataFrame(common[['common_id', 'geometry']]).merge(pd.DataFrame(previous), on='common_id', validate='one_to_one')
    union = shapely.area(shapely.union(joined.old_geometry.to_numpy(), joined.geometry.to_numpy()))
    difference = shapely.area(shapely.symmetric_difference(joined.old_geometry.to_numpy(), joined.geometry.to_numpy()))
    return pd.DataFrame({'common_id': joined.common_id, 'footprint_difference_fraction': difference / union,
                         'area_2010_km2': shapely.area(joined.old_geometry.to_numpy()) / 1e6,
                         'area_2022_projected_km2': shapely.area(joined.geometry.to_numpy()) / 1e6})


def coverage(ctx, inventories, lookups):
    from brazil_project.acquisition.census import filename
    reports = {}
    for year in (2010, 2022):
        inventory = inventories[year]
        matched = set(lookups[year][f'id_{year}'])
        excluded = set(inventory.tract_id)
        report = {'matched_tract_ids': len(matched), 'unmatched_tract_ids': len(excluded), 'measures': {}}
        for measure, dataset, column in [('population', 'Pessoa' if year == 2010 else 'Basico', 'pessoa03_V001' if year == 2010 else 'V0001'),
                                          ('households', 'Domicilio', 'domicilio01_V002' if year == 2010 else 'domicilio01_V00001')]:
            path = ctx.path('census', 'tables') / filename(year, dataset, ctx.config['census']['release'])
            if not path.exists():
                inventory[measure] = np.nan
                report['measures'][measure] = {'status': 'source_unavailable', 'source': str(path.relative_to(ctx.root))}
                continue
            import pyarrow.parquet as pq
            if column not in pq.read_schema(path).names:
                inventory[measure] = np.nan
                report['measures'][measure] = {'status': 'source_missing_column', 'column': column}
                continue
            frame = pd.read_parquet(path, columns=['code_tract', column])
            frame.code_tract = identifiers(frame.code_tract); keys(frame, 'code_tract')
            values = pd.to_numeric(frame.set_index('code_tract')[column], errors='coerce')
            valid = values.where(np.isfinite(values) & (values >= 0))
            inventory[measure] = inventory.tract_id.map(valid)
            m = valid.reindex(sorted(matched)); u = valid.reindex(sorted(excluded))
            total = pd.concat([m, u]).sum(min_count=1)
            missing = m.isna().any() or u.isna().any()
            report['measures'][measure] = {'status': 'partial' if missing else 'complete',
                'matched_known_total': 0.0 if not len(m) else (None if m.notna().sum() == 0 else float(m.sum())),
                'unmatched_known_total': 0.0 if not len(u) else (None if u.notna().sum() == 0 else float(u.sum())),
                'matched_missing_values': int(m.isna().sum()), 'unmatched_missing_values': int(u.isna().sum()),
                'unmatched_share_of_known_total': float(u.sum() / total) if pd.notna(total) and total > 0 else None}
        reports[str(year)] = report
    return reports


def publish_bundle(ctx, frames, metadata):
    folder = ctx.intermediate / 'harmonisation'; bundles = folder / 'bundles'
    bundles.mkdir(parents=True, exist_ok=True)
    generation = uuid.uuid4().hex
    destination = bundles / generation
    # CONTRACT: the pointer changes only after every artifact and its checksum are saved.
    with tempfile.TemporaryDirectory(dir=bundles) as temporary:
        temporary = Path(temporary); checksums = {}
        for name, frame in frames.items():
            frame = frame.copy(); frame['harmonisation_version'] = metadata['version']
            path = temporary / (name + '.parquet'); frame.to_parquet(path, index=False)
            checksums[name] = sha256(path)
        manifest = {**metadata, 'generation': generation, 'checksums': checksums}
        (temporary / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        os.replace(temporary, destination)
    pointer = folder / ('current.' + generation + '.tmp')
    pointer.write_text(json.dumps({'generation': generation, 'version': metadata['version']}) + '\n')
    os.replace(pointer, folder / 'current.json')
    return manifest


def load_bundle(ctx, names=None):
    folder = ctx.intermediate / 'harmonisation'
    pointer = folder / 'current.json'
    if not pointer.exists():
        raise WorkflowError('No versioned harmonisation bundle. Run brazil-project run harmonisation first.')
    active = json.loads(ctx.require(pointer).read_text())
    generation = active['generation']
    if len(generation) != 32 or any(c not in '0123456789abcdef' for c in generation):
        raise WorkflowError('Invalid harmonisation generation')
    bundle = folder / 'bundles' / generation
    manifest = json.loads(ctx.require(bundle / 'manifest.json').read_text())
    if manifest['version'] != active['version'] or manifest['policy'] != POLICY:
        raise WorkflowError('Harmonisation bundle version mismatch; rerun harmonisation')
    expected_mode = 'recomputed_python' if ctx.config['census'].get('recompute_harmonisation', False) else 'validated_original_correspondence'
    source_version, _ = input_version(ctx, expected_mode)
    if manifest['scope'] != (ctx.municipality or 'Brazil') or manifest['mode'] != expected_mode or manifest['source_version'] != source_version:
        raise WorkflowError('Harmonisation scope, mode, or source inputs changed; rerun harmonisation')
    required = {'lookup_2010', 'lookup_2022', 'group_sizes', 'common_geometry_2022'}
    requested = required | set(names) if names is not None else None
    frames = {}
    for name, expected in manifest['checksums'].items():
        path = ctx.require(bundle / (name + '.parquet'))
        if sha256(path) != expected:
            raise WorkflowError(f'Harmonisation artifact changed: {name}; rerun harmonisation')
        if requested is not None and name not in requested:
            continue
        if name in ['base_geometry_2022', 'comparison_geometry', 'common_geometry_2022', 'unmatched_geometry_2010', 'unmatched_geometry_2022']:
            frame = gpd.read_parquet(path)
        else:
            frame = pd.read_parquet(path)
        if len(frame) and not frame.harmonisation_version.eq(manifest['version']).all():
            raise WorkflowError('Incompatible harmonisation artifact version')
        frames[name] = frame.drop(columns='harmonisation_version')
    for year in (2010, 2022):
        lookup_keys(frames[f'lookup_{year}'], year)
    common = frames['common_geometry_2022']; sizes = frames['group_sizes']; keys(common, 'common_id'); keys(sizes, 'common_id')
    if set(common.common_id) != set(sizes.common_id):
        raise WorkflowError('Common geometry and group memberships disagree')
    for year in (2010, 2022):
        lookup = lookup_keys(frames[f'lookup_{year}'], year)
        counts = lookup.groupby('common_id')[f'id_{year}'].nunique().reindex(sizes.common_id)
        if counts.isna().any() or not np.array_equal(counts.to_numpy(), sizes[f'n_{year}'].to_numpy()):
            raise WorkflowError('Group-size metadata disagrees with tract memberships')
    return frames, manifest


def run(ctx):
    cfg = ctx.config['census']; scope_where(ctx, 'code_tract')
    mode = 'recomputed_python' if cfg.get('recompute_harmonisation', False) else 'validated_original_correspondence'
    raw = {year: raw_ids(ctx, year) for year in (2010, 2022)}
    if ctx.municipality and not raw[2022].str.startswith(ctx.municipality).any():
        raise WorkflowError('No 2022 source tracts found for municipality ' + ctx.municipality)
    source_version, contract = input_version(ctx, mode)
    (cross, l10, l22, sizes, rejected), cache = source_correspondence(ctx, mode, source_version)
    global_matched = {2010: set(l10.id_2010), 2022: set(l22.id_2022)}
    inventories = {}
    for year in (2010, 2022):
        ids = raw[year][~raw[year].isin(global_matched[year])]
        if ctx.municipality:
            # Imported candidate scopes consist of complete original groups; unrelated source IDs are not unmatched.
            if mode == 'validated_original_correspondence':
                original_lookup = gpd.read_file(ctx.path('census', 'baseline_lookup'), layer=str(year), ignore_geometry=True)
                originally_matched = set(identifiers(original_lookup[f'id_{year}']))
                failed = set(rejected[f'id_{year}']) - global_matched[year]
                ids = ids[~ids.isin(originally_matched) | ids.isin(failed)]
            ids = ids[ids.str.startswith(ctx.municipality) | ids.isin(failed)] if mode == 'validated_original_correspondence' else ids[ids.str.startswith(ctx.municipality)]
        inventories[year] = pd.DataFrame({'tract_id': ids.to_numpy(), 'year': year, 'reason': 'no_positive_area_correspondence'})
    if ctx.municipality:
        selected = set(l22.loc[l22.id_2022.str.startswith(ctx.municipality), 'common_id'])
        cross = cross[cross.common_id.isin(selected)]; l10 = l10[l10.common_id.isin(selected)]; l22 = l22[l22.common_id.isin(selected)]; sizes = sizes[sizes.common_id.isin(selected)]
    lookups = {2010: l10, 2022: l22}
    for year in (2010, 2022):
        lookup_keys(lookups[year], year)
    if mode == 'validated_original_correspondence':
        source = read_ids(ctx.path('census', 'baseline_geometry'), 2022,
                          list(l22.id_2022) + list(inventories[2022].tract_id) if ctx.municipality else None, baseline=True).to_crs(cfg['crs'])
    else:
        source = prepare(read_ids(ctx.path('census', 'tracts'), 2022,
                                 list(l22.id_2022) + list(inventories[2022].tract_id) if ctx.municipality else None, '2022'), 2022, cfg['crs'], cfg['precision_grid'])
    full_base = attach_base(source, l22)
    display = full_base[full_base.id_2022.str.startswith(ctx.municipality)].copy() if ctx.municipality else full_base.copy()
    common = dissolved_common_geometry(full_base, sizes)
    old = prepare(read_ids(ctx.path('census', 'tracts'), 2010, list(l10.id_2010) + list(inventories[2010].tract_id), '2010'), 2010, cfg['crs'], cfg['precision_grid'])
    old = old.merge(l10[['id_2010', 'common_id']], on='id_2010', how='left', validate='many_to_one')
    diagnostics = footprint_diagnostics(old[old.common_id.notna()], common)
    common = common.merge(diagnostics, on='common_id', validate='one_to_one')
    excluded = {2010: old[old.id_2010.isin(inventories[2010].tract_id)].copy(),
                2022: full_base[full_base.id_2022.isin(inventories[2022].tract_id)].copy()}
    for year, geometry in excluded.items():
        geometry['reason'] = 'no_positive_area_correspondence'
        geometry['geometry_empty_or_missing'] = geometry.geometry.isna() | geometry.geometry.is_empty
    population_coverage = coverage(ctx, inventories, lookups)
    groups_version = hashlib.sha256(pd.util.hash_pandas_object(cross.sort_values(['id_2010', 'id_2022']), index=False).values.tobytes()).hexdigest()
    version = hashlib.sha256((source_version + (ctx.municipality or 'national') + groups_version).encode()).hexdigest()
    frames = {'crosswalk': cross, 'lookup_2010': l10, 'lookup_2022': l22, 'group_sizes': sizes,
              'base_geometry_2022': display, 'comparison_geometry': full_base,
              'common_geometry_2022': common, 'footprint_diagnostics': diagnostics, 'rejected_edges': rejected,
              'unmatched_2010': inventories[2010], 'unmatched_2022': inventories[2022],
              'unmatched_geometry_2010': excluded[2010], 'unmatched_geometry_2022': excluded[2022]}
    metadata = {'version': version, 'source_version': source_version, 'policy': POLICY, 'mode': mode,
                'scope': ctx.municipality or 'Brazil', 'source_contract': contract, 'population_coverage': population_coverage,
                'assumption': 'Boundary differences are assumed not to materially change the inhabited population; not independently verified.'}
    manifest = publish_bundle(ctx, frames, metadata)
    return ctx.report('harmonisation', {**metadata, 'generation': manifest['generation'], 'tracts_2022': len(display), 'groups': len(sizes),
        'duplicate_base_ids': int(display.id_2022.duplicated().sum()), 'common_geometry_features': len(common),
        'rejected_edges': len(rejected), 'unmatched': {str(y): len(inventories[y]) for y in (2010, 2022)},
        'footprint_difference_above_10pct': int((diagnostics.footprint_difference_fraction > .1).sum())})
