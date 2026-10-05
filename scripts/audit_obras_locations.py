"""Read-only screening examples; boxes are not a national coastline classifier."""
import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('data/processed/obrasgov/projects_st.gpkg'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    frame = gpd.read_file(args.input, columns=['id_projeto_investimento', 'desc_nome', 'tipo', 'uf_principal'])
    if frame.crs is None or frame.crs.to_epsg() != 4674:
        raise ValueError('Screening requires declared EPSG:4674; do not infer or relabel CRS.')
    bounds = frame.bounds
    out_of_range = ((bounds.minx < -180) | (bounds.maxx > 180) | (bounds.miny < -90) | (bounds.maxy > 90))
    # CONTRACT: One-level extraction covers MultiPoints, not all nested collections.
    parts, indices = shapely.get_parts(frame.geometry.array, return_index=True)
    is_point = shapely.get_type_id(parts) == 0
    points = pd.DataFrame(frame.iloc[indices[is_point]].drop(columns='geometry')).reset_index(drop=True)
    points['lon'] = shapely.get_x(parts[is_point])
    points['lat'] = shapely.get_y(parts[is_point])
    valid = np.isfinite(points.lon) & np.isfinite(points.lat) & points.lon.between(-180, 180) & points.lat.between(-90, 90)
    points = points[valid]
    # WHY: These illustrative offshore boxes establish errors worth reviewing;
    # they must never be used as an automatic deletion or correction rule.
    selected = points[((points.lon > -37) & (points.lat < -15)) | ((points.lon > -47) & (points.lat < -25))]
    digest = hashlib.sha256()
    with args.input.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    result = {
        'source': str(args.input), 'source_sha256': digest.hexdigest(),
        'source_crs': str(frame.crs), 'source_records': len(frame),
        'geometry_type_counts': frame.geom_type.value_counts().to_dict(),
        'out_of_range_geometry_bounds_records': int(out_of_range.sum()),
        'bounds': frame.total_bounds.tolist(),
        'extraction': 'one-level get_parts; nested collection completeness not established',
        'valid_point_components': len(points),
        'illustrative_boxes': '(lon > -37 and lat < -15) OR (lon > -47 and lat < -25)',
        'illustrative_offshore_box_points': len(selected),
        'distinct_projects_in_boxes': int(selected.id_projeto_investimento.nunique()),
        'national_offshore_count': None,
        'examples': json.loads(selected.head(18).to_json(orient='records', force_ascii=False)),
        'records_modified': False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"Screened {len(frame)} records: {len(selected)} illustrative offshore point components, {result['distinct_projects_in_boxes']} projects. No records changed.")


if __name__ == '__main__':
    main()
