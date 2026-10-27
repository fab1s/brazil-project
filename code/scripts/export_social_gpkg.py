"""Readable GIS export using the existing national map calculations."""
from datetime import datetime, timezone
import json
import hashlib
import os
from pathlib import Path
import runpy
import sqlite3
import tempfile

import geopandas as gpd
import pandas as pd
import shapely

from brazil_project.harmonisation.census import load_bundle, sha256
from brazil_project.io import WorkflowError, keys, code_hashes

WEB = runpy.run_path(str(Path(__file__).with_name('build_web_map.py')))
INDICATORS = WEB['INDICATORS']


def field_definitions(columns):
    definitions = []

    def add(original, readable, unit, description):
        if original in columns:
            definitions.append(dict(original_field=original, readable_field=readable,
                                    unit=unit, description=description))

    add('common_id', 'common_id', 'identifier', 'Original comparison-group identifier; preserve as text.')
    add('code_muni', 'municipality_code', 'identifier', 'IBGE municipality code for the display overview; complete groups may cross municipality boundaries.')
    add('relationship', 'tract_relationship', 'category', 'Relationship between 2010 and 2022 tract memberships.')
    for year in (2010, 2022):
        add(f'n_{year}', f'tracts_{year}', 'tracts', 'Number of distinct member tracts in the complete comparison group.')
        for key in INDICATORS:
            if key == 'population_density':
                add(f'{key}_{year}', f'population_density_{year}', 'people/km2', 'Population divided by saved equal-area common geometry area.')
                add(f'{key}_n{year}', f'total_population_{year}', 'people', 'Population used for density, retaining the original density validity mask.')
                add(f'{key}_d{year}', f'area_km2_{year}', 'km2', 'Saved EPSG:6933 equal-area denominator; geometry itself remains EPSG:5880.')
            else:
                add(f'{key}_{year}', f'{key}_share_{year}', 'fraction', 'Original proportion; 0.10 means 10%.')
                if key in ('black', 'brown', 'black_brown'):
                    numerator = f'{key}_population_{year}'
                    denominator = f'population_for_{key}_{year}'
                    noun, unit = 'residents', 'people'
                elif key == 'literacy':
                    numerator = f'literate_15plus_{year}'
                    denominator = f'population_15plus_{year}'
                    noun, unit = 'residents aged 15 or older', 'people'
                else:
                    numerator = f'{key}_households_{year}'
                    denominator = f'households_for_{key}_{year}'
                    noun, unit = 'households', 'households'
                add(f'{key}_n{year}', numerator, unit, f'Original summed numerator counting {noun}; missing-component rules are unchanged.')
                add(f'{key}_d{year}', denominator, unit, f'Total {noun} used for this indicator, retaining its own validity and missingness mask.')
        add(f'income_{year}', f'income_mean_brl_{year}', 'BRL at July 2022 prices', 'Original household-head-weighted mean; 2010 is inflation adjusted and year-specific income definitions remain different.')
        income_fields = [
            ('heads', 'heads_used', 'household heads', 'Usable household-head weights contributing to the original income mean.'),
            ('tracts_used', 'tracts_used', 'tracts', 'Tracts contributing usable income and weights.'),
            ('missing_weights', 'tracts_missing_weights', 'tracts', 'Original missing household-head weight diagnostic.'),
            ('complete', 'inputs_complete', 'flag', 'Original income input-completeness flag; a saved mean alone does not establish completeness.'),
            ('tracts_total', 'tracts_total', 'tracts', 'Original income-aggregation tract count diagnostic.'),
        ]
        for old, new, unit, description in income_fields:
            add(f'income_{old}_{year}', f'income_{new}_{year}', unit, description)
    for key in INDICATORS:
        density = key == 'population_density'
        add(f'{key}_change', f'{key}_{"change_pct" if density else "change_pp"}',
            'percent' if density else 'percentage points',
            'Original relative density change, 100*(2022/2010-1).' if density else 'Original 2022 minus 2010 share, multiplied by 100.')
    add('income_change', 'income_change_pct', 'percent', 'Original relative change in inflation-comparable saved income means.')
    add('income_change_brl', 'income_change_brl', 'BRL at July 2022 prices', 'Original 2022 minus inflation-adjusted 2010 income mean.')
    return pd.DataFrame(definitions, columns=['original_field', 'readable_field', 'unit', 'description'])


def _shared_name(originals, year):
    names = set(originals)
    if f'population_density_n{year}' in names:
        return f'total_population_{year}'
    if f'n_{year}' in names:
        return f'tracts_{year}'
    if names <= {f'{race}_d{year}' for race in ('black', 'brown', 'black_brown')}:
        return f'population_for_race_{year}'
    if names and all(name.endswith(f'_d{year}') for name in names):
        return f'households_{year}'
    raise WorkflowError('Unrecognised duplicate measures: ' + ', '.join(originals))


def simplify_fields(frame):
    dictionary = field_definitions(frame.columns)
    attributes = [name for name in frame.columns if name != frame.geometry.name]
    if set(attributes) != set(dictionary.original_field) or len(attributes) != len(dictionary):
        raise WorkflowError('Unmapped source fields in GeoPackage; review names before export.')
    definitions = dictionary.set_index('original_field')
    groups = []
    candidates = {}
    for original in attributes:
        series = frame[original]
        unit = definitions.loc[original, 'unit']
        digest = hashlib.sha256(pd.util.hash_pandas_object(series, index=False).values.tobytes()).hexdigest()
        match = next((group for group in candidates.get((unit, digest), [])
                      if series.equals(frame[group[0]])), None)
        if match is None:
            match = [original]
            groups.append(match)
            candidates.setdefault((unit, digest), []).append(match)
        else:
            match.append(original)
    names = {}
    for group in groups:
        if len(group) == 1:
            english = definitions.loc[group[0], 'readable_field']
        else:
            year = next((year for year in (2010, 2022) if all(str(year) in field for field in group)), None)
            if year is None:
                raise WorkflowError('Duplicate fields span incompatible years: ' + ', '.join(group))
            english = _shared_name(group, year)
        if english in names.values():
            raise WorkflowError('Readable field name collision: ' + english)
        names.update({original: english for original in group})
    dictionary['readable_field'] = dictionary.original_field.map(names)
    # INVARIANT: Collapse only columns whose unit, values and null positions match exactly.
    result = pd.DataFrame({names[group[0]]: frame[group[0]] for group in groups}, index=frame.index)
    result[frame.geometry.name] = frame.geometry
    return gpd.GeoDataFrame(result, geometry=frame.geometry.name, crs=frame.crs), dictionary


def verify_simplified(expected, actual, dictionary):
    if expected.crs != actual.crs or len(expected) != len(actual):
        raise WorkflowError('GeoPackage CRS or feature count changed.')
    for row in dictionary.itertuples(index=False):
        try:
            pd.testing.assert_series_equal(expected[row.original_field].reset_index(drop=True),
                                           actual[row.readable_field].reset_index(drop=True),
                                           check_names=False, check_dtype=False, check_exact=True)
        except AssertionError as error:
            raise WorkflowError('Original field changed in simplified export: ' + row.original_field) from error
    if not (expected.geometry.to_wkb().to_numpy() == actual.geometry.to_wkb().to_numpy()).all():
        raise WorkflowError('GeoPackage geometry changed.')


def verify_frame(expected, actual, original_columns=None, allow_multipart_promotion=False):
    if expected.crs != actual.crs or len(expected) != len(actual):
        raise WorkflowError('GeoPackage CRS or feature count changed.')
    columns = list(expected.columns if original_columns is None else original_columns)
    geometry = expected.geometry.name
    attributes = [name for name in columns if name != geometry]
    try:
        pd.testing.assert_frame_equal(expected[attributes].reset_index(drop=True),
                                      actual[attributes].reset_index(drop=True),
                                      check_dtype=False, check_exact=True)
    except AssertionError as error:
        raise WorkflowError('GeoPackage attribute values or missingness changed: ' + str(error)) from error
    same_wkb = expected.geometry.to_wkb().to_numpy() == actual.geometry.to_wkb().to_numpy()
    if not same_wkb.all():
        if not allow_multipart_promotion or not shapely.equals(
                expected.geometry.array.to_numpy()[~same_wkb],
                actual.geometry.array.to_numpy()[~same_wkb]).all():
            raise WorkflowError('GeoPackage geometry changed.')


def run(ctx, output, source=None):
    if ctx.municipality:
        raise WorkflowError('This export requires the national configuration, with municipality empty.')
    output = Path(output).resolve()
    if output.exists():
        raise WorkflowError('Refusing to overwrite an existing file: ' + str(output))
    source = Path(source or ctx.root / '.cache/map-update/build/social.gpkg').resolve()
    prepared = source.with_name('prepared.json')
    source_record = json.loads(ctx.require(prepared).read_text())
    ctx.require(source)
    original_code = Path(__file__).with_name('build_web_map.py')
    before = {str(p): sha256(p) for p in (ctx.config_path, source, prepared, original_code, Path(__file__))}
    package_code = code_hashes(ctx.root)
    # CONTRACT: Revalidate the exact census inputs and original exporter below;
    # unrelated report/quality-audit code may change after the map build.
    print('Verifying complete national bundle and original export inputs', flush=True)
    bundle, manifest = load_bundle(ctx, names=[])
    checksums = {key: sha256(ctx.artifact('indicators', key + '.parquet')) for key in [*INDICATORS, 'income']}
    contract = source_record['contract']
    if (contract.get('harmonisation_version') != manifest['version'] or
            contract.get('indicator_checksums') != checksums or
            contract.get('export_policy') != 'merged-common-area-v1' or
            source_record['database_sha256'] != before[str(source)]):
        raise WorkflowError('Prepared map database differs from current validated inputs; rebuild it first.')
    metrics = WEB['measure_fields'](ctx, bundle['common_geometry_2022'])
    original_social = gpd.read_file(source, layer='social')
    keys(metrics, 'common_id')
    # COMPATIBILITY: GeoPackage promotes Polygon members to MultiPolygon in a mixed layer.
    verify_frame(metrics, original_social, allow_multipart_promotion=True)
    del bundle, metrics
    layers = {'social': original_social, 'overview': gpd.read_file(source, layer='overview')}
    provenance = dict(exported_at=datetime.now(timezone.utc).isoformat(), scope='Brazil',
                      original_inputs=before, contract=contract, indicator_checksums=checksums,
                      policy='single-english-field-per-distinct-measure-v2',
                      original_code='code/scripts/build_web_map.py:measure_fields; overview_metrics',
                      limitations=['No recalculation of research methods, missingness, CRS or group identifiers.',
                                   'Shares are fractions; share changes are percentage points; density/income changes are relative percent.',
                                   'Source field codes are mapped in field_dictionary; exact equal fields share one English column.',
                                   'Different indicator masks are retained as distinct columns even when observed values agree.',
                                   'The municipality overview includes complete cross-boundary groups and simplified display geometry.',
                                   'Software parity does not establish independent scientific validation.'])
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = output.with_suffix('.gpkg.lock')
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    try:
        with tempfile.TemporaryDirectory(prefix='.social-export-', dir=output.parent) as temporary:
            staged = Path(temporary) / 'social.gpkg'
            dictionaries = []
            for name, frame in layers.items():
                print('Writing concise English fields:', name, len(frame), flush=True)
                concise, dictionary = simplify_fields(frame)
                concise.to_file(staged, layer=name, driver='GPKG', index=False)
                actual = gpd.read_file(staged, layer=name)
                verify_simplified(frame, actual, dictionary)
                dictionary.insert(0, 'layer', name)
                dictionaries.append(dictionary)
                provenance.setdefault('layers', {})[name] = dict(features=len(frame), original_fields=len(frame.columns)-1,
                                                               english_fields=len(concise.columns)-1,
                                                               exactly_redundant_fields_removed=len(frame.columns)-len(concise.columns),
                                                               original_values_missingness_geometry_crs_exact=True)
                del concise, actual
            dictionary = pd.concat(dictionaries, ignore_index=True)
            dictionary = dictionary.rename(columns={'original_field':'original_column','readable_field':'english_column'})
            with sqlite3.connect(staged) as db:
                dictionary.to_sql('field_dictionary', db, index=False)
                pd.DataFrame([{'key': key, 'value': json.dumps(value, ensure_ascii=False)} for key, value in provenance.items()]).to_sql('export_metadata', db, index=False)
                for table, description in [('field_dictionary', 'Original columns, English columns, units and meanings.'),
                                           ('export_metadata', 'Export provenance, exact-value checks and limitations.')]:
                    db.execute('INSERT INTO gpkg_contents (table_name, data_type, identifier, description) VALUES (?, ?, ?, ?)',
                               (table, 'attributes', table, description))
                if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                    raise WorkflowError('GeoPackage integrity check failed.')
            for path, expected in before.items():
                if sha256(path) != expected:
                    raise WorkflowError('An export input changed during execution: ' + path)
            if code_hashes(ctx.root) != package_code:
                raise WorkflowError('Processing code changed during export; rerun.')
            for key, expected in checksums.items():
                if sha256(ctx.artifact('indicators', key+'.parquet')) != expected:
                    raise WorkflowError('Indicator input changed during export: ' + key)
            # CONTRACT: Publish a completely verified file without replacing existing user data.
            os.link(staged, output)
    finally:
        lock.unlink()
    return dict(output=str(output), sha256=sha256(output), **provenance)
