"""Small local-output checks shared by the four readable dataset notebooks."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import sys


FINAL_FILENAMES = {
    "census": "census_comparison_areas_2010_2022.gpkg",
    "obrasgov": "obrasgov_screened_locations.gpkg",
    "ibama": "ibama_licensed_projects.gpkg",
    "communities": "ibge_favelas_communities_2022.gpkg",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def notebook_context(dataset):
    """Set up one national notebook without exposing path plumbing in its cells."""
    sys.path[:0] = [str(PROJECT_ROOT / 'datasets/shared'), str(PROJECT_ROOT / 'datasets'),
                    str(PROJECT_ROOT / 'datasets' / dataset)]
    os.environ.setdefault('MPLCONFIGDIR', str(PROJECT_ROOT / '.cache/matplotlib'))
    from brazil_project.io import Context, WorkflowError
    ctx = Context(PROJECT_ROOT / 'datasets/project.toml')
    if ctx.municipality:
        raise WorkflowError('These four notebooks require national scope; clear project.municipality.')
    ctx.notebook_from_saved = os.environ.get('BRAZIL_NOTEBOOK_FROM_SAVED', '0') == '1'
    return ctx


def process_stage(ctx, stage):
    """The notebook owns stage order; saved mode only refreshes its evidence."""
    if ctx.notebook_from_saved:
        print('Using saved ' + stage + ' outputs')
        return
    from brazil_project.cli import dispatch
    from contextlib import redirect_stdout, redirect_stderr
    from io import StringIO
    log = StringIO()
    completed = False
    try:
        with redirect_stdout(log), redirect_stderr(log):
            dispatch(ctx, stage)
        completed = True
    finally:
        # PRESENTATION: retain diagnostic logs locally; cells show the analytical evidence.
        output = log.getvalue().replace(str(ctx.root) + os.sep, '')
        if output:
            path = ctx.root / 'outputs/logs/notebooks' / (stage + '.txt')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output)
        if completed:
            print('Completed ' + stage)
        elif output:
            print('Stage failed; see ' + str(path.relative_to(ctx.root)))


def sql_table(path, query, params=()):
    """Read a small, explicit result table without modifying the GeoPackage."""
    import pandas as pd
    with sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True) as connection:
        return pd.read_sql_query(query, connection, params=params)


def geopackage_inventory(path):
    """Describe source layers without loading every geometry."""
    import pandas as pd
    import pyogrio
    rows = []
    for name, geometry in pyogrio.list_layers(path):
        info = pyogrio.read_info(path, layer=name)
        rows.append({'Layer': name, 'Rows': info['features'], 'Geometry': geometry,
                     'CRS': info['crs']})
    return pd.DataFrame(rows)


def show_final(ctx, result):
    """Keep transfer details together after the processing explanation."""
    from IPython.display import display
    import pandas as pd
    display(pd.DataFrame([{'File': str(Path(result['file']).relative_to(ctx.root)),
                           'Layer': result['layer'], 'Features': result['features'],
                           'CRS': 'EPSG:' + str(result['epsg'])}]))
    print('SHA-256:', result['sha256'])


def show_figure(figure):
    from IPython.display import display
    import matplotlib.pyplot as plt
    display(figure)
    plt.close(figure)


def show_image(ctx, relative):
    from IPython.display import Image, display
    display(Image(filename=str(ctx.require(ctx.root / relative))))


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def baseline_checksum(project, source):
    relative = str(Path(source).resolve().relative_to(project.resolve()))
    # CONTRACT: These preserved source files are exact, inventoried baselines.
    baselines = {
        "data/processed/ibama/licensed_projects_st.gpkg": (78471168, "0df410feb5e5aaa975851107fc501c408d2ed7ceb15a72e21a573462e0773863"),
        "data/processed/ibge/Data/favelas_2022.gpkg": (16105472, "aec748dc609a00eb89e652b7c289c7728255d209286e1d58be2fa881e4d2e9f0"),
    }
    if relative not in baselines:
        raise ValueError("No preserved-baseline inventory entry: " + relative)
    size, expected = baselines[relative]
    if size != Path(source).stat().st_size or expected != sha256(source):
        raise ValueError("Preserved baseline differs from the inventory: " + relative)
    return expected


def geopackage_summary(path, layer, expected_crs=None, unique_key=None):
    path = Path(path).resolve(strict=True)
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("GeoPackage integrity check failed: " + str(path))
        layers = {name: (kind, count) for name, kind, count in connection.execute(
            "SELECT table_name, data_type, COALESCE(srs_id, 0) FROM gpkg_contents")}
        if layer not in layers or layers[layer][0] != "features":
            raise ValueError("Missing spatial layer: " + layer)
        crs = connection.execute("SELECT srs_id FROM gpkg_geometry_columns WHERE table_name=?", (layer,)).fetchone()[0]
        if expected_crs is not None and crs != expected_crs:
            raise ValueError(f"Expected EPSG:{expected_crs}; found EPSG:{crs}.")
        quoted = '"' + layer.replace('"', '""') + '"'
        count = connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
        if unique_key is not None:
            key = '"' + unique_key.replace('"', '""') + '"'
            distinct, missing = connection.execute(
                f"SELECT COUNT(DISTINCT {key}), SUM({key} IS NULL) FROM {quoted}").fetchone()
            if distinct != count or missing:
                raise ValueError(f"{unique_key} must be complete and unique in {layer}.")
    return {"file": str(path), "layer": layer, "features": count,
            "epsg": crs, "bytes": path.stat().st_size, "sha256": sha256(path)}


def local_copy(notebook_folder, source):
    """Publish the descriptively named, checked GeoPackage beside its notebook."""
    source = Path(source).resolve(strict=True)
    folder = Path(notebook_folder)
    target = folder / FINAL_FILENAMES[folder.name]
    legacy = folder / "final.gpkg"
    receipt = folder / ".final-gpkg.json"
    relative_source = os.path.relpath(source, start=folder)
    expected = sha256(source)
    def write_receipt():
        temporary_receipt = receipt.with_suffix(".tmp.json")
        temporary_receipt.write_text(json.dumps({"source": relative_source, "sha256": expected}) + "\n")
        os.replace(temporary_receipt, receipt)
    if legacy.exists() and not target.exists():
        # COMPATIBILITY: Rename only an exact, previously checked deliverable.
        # This avoids copying large GeoPackages and preserves their bytes.
        if legacy.is_symlink() or not receipt.exists():
            raise FileExistsError("Unverified legacy final.gpkg: " + str(legacy))
        saved = json.loads(receipt.read_text())
        if saved.get("sha256") != expected or sha256(legacy) != expected:
            raise FileExistsError("Legacy final.gpkg differs from the checked producer: " + str(legacy))
        os.replace(legacy, target)
        write_receipt()
        return target
    if target.is_symlink():
        if target.resolve() != source:
            raise FileExistsError("A different final GeoPackage link already exists: " + str(target))
    elif target.exists():
        current = sha256(target)
        if receipt.exists():
            saved = json.loads(receipt.read_text())
            if saved.get("sha256") != current:
                if current == expected:
                    # RECOVERY: Publication may have finished before its receipt.
                    write_receipt()
                    return target
                raise FileExistsError("The local final GeoPackage changed outside this pipeline: " + str(target))
            # COMPATIBILITY: A checked prior producer may be replaced after an
            # export-policy change; its receipt still proves the old bytes.
        elif current != expected:
            raise FileExistsError("An unrelated final GeoPackage already exists: " + str(target))
        if current == expected:
            write_receipt()
            return target
    with tempfile.NamedTemporaryFile(prefix=".final-", suffix=".gpkg", dir=folder, delete=False) as stream:
        staged = Path(stream.name)
    try:
        shutil.copyfile(source, staged)
        if sha256(staged) != expected or sha256(source) != expected:
            raise ValueError("GeoPackage changed or copied incompletely; previous final remains intact.")
        os.replace(staged, target)
        write_receipt()
    finally:
        staged.unlink(missing_ok=True)
    return target
