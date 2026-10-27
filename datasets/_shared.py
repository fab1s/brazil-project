"""Small local-output checks shared by the four readable dataset notebooks."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_stage(project, stage):
    executable = project / ".venv/bin/python"
    if not executable.is_file():
        raise FileNotFoundError("Install the locked environment using the root README first.")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(project / "datasets/shared") + os.pathsep + environment.get("PYTHONPATH", "")
    command = [str(executable), "-m", "brazil_project.cli", "run", stage,
               "--config", str(project / "datasets/project.toml")]
    subprocess.run(command, cwd=project, env=environment, check=True)


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
    """Publish a self-contained, checked GeoPackage beside its notebook."""
    source = Path(source).resolve(strict=True)
    folder = Path(notebook_folder)
    target = folder / "final.gpkg"
    receipt = folder / ".final-gpkg.json"
    relative_source = os.path.relpath(source, start=folder)
    expected = sha256(source)
    def write_receipt():
        temporary_receipt = receipt.with_suffix(".tmp.json")
        temporary_receipt.write_text(json.dumps({"source": relative_source, "sha256": expected}) + "\n")
        os.replace(temporary_receipt, receipt)
    if target.is_symlink():
        if target.resolve() != source:
            raise FileExistsError("A different final.gpkg link already exists: " + str(target))
    elif target.exists():
        current = sha256(target)
        if receipt.exists():
            saved = json.loads(receipt.read_text())
            if saved.get("sha256") != current or saved.get("source") != relative_source:
                if current == expected:
                    # RECOVERY: Publication may have finished before its receipt.
                    write_receipt()
                    return target
                raise FileExistsError("The local final.gpkg changed outside this pipeline: " + str(target))
        elif current != expected:
            raise FileExistsError("An unrelated final.gpkg already exists: " + str(target))
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
