"""Project-relative paths and explicit stage artifacts."""
import json
import hashlib
from datetime import datetime, timezone
import os
from pathlib import Path
import pandas as pd
import geopandas as gpd

class WorkflowError(RuntimeError):
    pass

class Context:
    def __init__(self, path):
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        self.config_path = Path(path).resolve()
        with self.config_path.open('rb') as stream:
            self.config = tomllib.load(stream)
        self.root = (self.config_path.parent / self.config['project']['root']).resolve()
        self.intermediate = self.root / 'data/intermediate'
        self.municipality = self.config['project'].get('municipality', '')

    def path(self, section, key):
        return self.root / self.config[section][key]

    def artifact(self, stage, name):
        path = self.intermediate / stage / name
        if stage == 'harmonisation' and name.endswith('.parquet'):
            pointer = self.intermediate / stage / 'current.json'
            if pointer.exists():
                generation = json.loads(pointer.read_text())['generation']
                if len(generation) != 32 or any(c not in '0123456789abcdef' for c in generation):
                    raise WorkflowError('Invalid harmonisation generation')
                path = self.intermediate / stage / 'bundles' / generation / name
        # CONTRACT: Looking up an input must not create placeholder folders.
        return path

    def require(self, path):
        if not Path(path).is_file():
            raise WorkflowError(f'Missing input: {path}. Import the documented local cache or run the acquisition stage explicitly.')
        return path

    def write_table(self, frame, stage, name):
        path = self.artifact(stage, name + '.parquet')
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.tmp.parquet')
        frame.to_parquet(temp, index=False)
        os.replace(temp, path)
        return path

    def table(self, stage, name):
        return pd.read_parquet(self.require(self.artifact(stage, name + '.parquet')))

    def write_geo(self, frame, stage, name):
        return self.write_table(frame, stage, name)

    def geo(self, stage, name):
        return gpd.read_parquet(self.require(self.artifact(stage, name + '.parquet')))

    def report(self, stage, payload):
        path = self.artifact(stage, 'report.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {**payload, 'generated_at': datetime.now(timezone.utc).isoformat()}
        rendered=json.dumps(payload, indent=2, default=str) + '\n'
        temporary=path.with_suffix('.tmp.json')
        temporary.write_text(rendered)
        os.replace(temporary,path)
        if stage=='runs':
            history=path.parent/'history'
            history.mkdir(parents=True,exist_ok=True)
            (history/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.json')).write_text(rendered)
        return payload


def identifiers(values):
    if pd.api.types.is_numeric_dtype(values):
        return values.astype("Int64").astype("string")
    return values.astype("string")


def keys(frame, column):
    if frame[column].isna().any() or frame[column].duplicated().any():
        raise WorkflowError(f'{column} must be nonmissing and unique')
    return frame


def lookup_keys(frame, year):
    name = f'id_{year}'
    result = pd.DataFrame(frame[[name, 'common_id']]).drop_duplicates().copy()
    result[name] = identifiers(result[name])
    result['common_id'] = identifiers(result['common_id'])
    return keys(result, name)


def code_hashes(root):
    """Fingerprint the code that actually produces the census export."""
    root = Path(root)
    paths = [root / name for name in (
        'datasets/shared/brazil_project/io.py',
        'datasets/shared/brazil_project/acquisition/census.py',
        'datasets/shared/brazil_project/harmonisation/census.py',
        'datasets/shared/brazil_project/indicators/temporal.py',
        'datasets/shared/scripts/build_web_map.py',
        'datasets/shared/scripts/export_social_gpkg.py',
    )]
    result = {}
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError('Missing census implementation: ' + str(path))
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                digest.update(block)
        result[str(path.relative_to(root))] = digest.hexdigest()
    return result
