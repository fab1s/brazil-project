"""Read the preserved local IBGE census tables used by the four-file handoff.

Historical R acquisition code and its pinned environment remain on the archive
branch. The focused dataset pipeline never downloads data.
"""

import pandas as pd
from brazil_project.io import identifiers


def filename(year, dataset, release):
    return f'{year}_tracts_{dataset}_{release}.parquet'


def read(ctx, year, dataset, columns=None):
    path = ctx.require(ctx.path('census', 'tables') / filename(year, dataset, ctx.config['census']['release']))
    import pyarrow.parquet as pq
    import pyarrow as pa
    schema = pq.read_schema(path)
    filters = None
    lookup_path = ctx.artifact('harmonisation', f'lookup_{year}.parquet')
    requested = None
    if ctx.municipality and lookup_path.exists():
        requested = pd.read_parquet(lookup_path)[f'id_{year}'].dropna().unique().tolist()
        field = schema.field('code_tract').type
        values = requested if pa.types.is_string(field) else [int(v) for v in requested]
        filters = [('code_tract', 'in', values)]
    frame = pd.read_parquet(path, columns=columns, filters=filters)
    frame['code_tract'] = identifiers(frame.code_tract)
    if ctx.municipality and requested is None:
        frame = frame[frame.code_tract.str.startswith(ctx.municipality)]
    return frame.reset_index(drop=True)
