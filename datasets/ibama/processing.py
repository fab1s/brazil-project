"""Check the IBAMA translation against the preserved GeoPackage baseline."""

import json
import os
from pathlib import Path
import sqlite3
import tempfile

import geopandas as gpd
import pandas as pd
import pyogrio
import shapely

from _shared import baseline_checksum, geopackage_summary, local_copy, run_stage
from english_export import export, verify_export
from brazil_project.io import Context, WorkflowError


def verify_translation(ctx):
    """The current Python result must reproduce every preserved baseline field."""
    source = ctx.require(ctx.path("infrastructure", "ibama"))
    baseline_checksum(ctx.root, source)
    report = json.loads(ctx.require(ctx.artifact("ibama", "report.json")).read_text())
    if report.get("source") != "copied_snapshot":
        raise WorkflowError("This handoff targets the preserved website-era IBAMA snapshot, not new acquisition.")
    baseline = gpd.read_file(source)
    active = gpd.read_parquet(ctx.require(ctx.artifact("ibama", "licensed_projects.parquet")))
    if len(active) != len(baseline) or active.crs != baseline.crs:
        raise WorkflowError("IBAMA translation differs in row count or CRS.")
    for column in baseline.columns.drop("geometry"):
        try:
            pd.testing.assert_series_equal(active[column].reset_index(drop=True),
                                           baseline[column].reset_index(drop=True), check_dtype=False)
        except AssertionError as error:
            raise WorkflowError("IBAMA baseline field changed: " + column) from error
    if not (shapely.to_wkb(active.geometry.array) == shapely.to_wkb(baseline.geometry.array)).all():
        raise WorkflowError("IBAMA geometry differs from the preserved baseline.")
    return source


def build(project):
    run_stage(project, "ibama")
    ctx = Context(project / "datasets/project.toml")
    source = verify_translation(ctx)
    destination = project / "outputs/maps/notebook-exports/ibama.gpkg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".ibama-", suffix=".gpkg", dir=destination.parent, delete=False) as temp:
        staged = Path(temp.name)
    staged.unlink()
    try:
        export(source, staged, "ibama", baseline_checksum(project, source))
        geopackage_summary(staged, "licensed_projects_st", expected_crs=4674, unique_key="record_id")
        verify_export(source, staged, "ibama", baseline_checksum(project, source))
        os.replace(staged, destination)
    finally:
        staged.unlink(missing_ok=True)
    local_copy(project / "datasets/ibama", destination)
    return inspect_final(project)


def inspect_final(project, preview=False):
    ctx = Context(project / "datasets/project.toml")
    source = ctx.require(ctx.path("infrastructure", "ibama"))
    baseline = baseline_checksum(project, source)
    path = project / "outputs/maps/notebook-exports/ibama.gpkg"
    if preview and not path.exists():
        raise WorkflowError("Build the English export before previewing it.")
    summary = geopackage_summary(path, "licensed_projects_st", expected_crs=4674, unique_key="record_id")
    verify_export(source, path, "ibama", baseline)
    if not preview:
        local_copy(project / "datasets/ibama", path)
    return summary


def website_id_check(project):
    """Compare IDs at the website archive's highest zoom, without changing the data."""
    archive = project / "outputs/maps/website/data/ibama.pmtiles"
    if not archive.is_file():
        return {"status": "local website archive unavailable"}
    # Tiling can split one source feature across many rows. Compare distinct IDs.
    tiles = pyogrio.read_dataframe(archive, layer="licensed_projects_st",
                                   columns=["objectid"], read_geometry=False)
    ids = pd.to_numeric(tiles.objectid, errors="raise")
    if ids.isna().any() or not (ids == ids.astype("int64")).all():
        raise WorkflowError("IBAMA website tile IDs are missing or nonintegral.")
    with sqlite3.connect(project / "data/processed/ibama/licensed_projects_st.gpkg") as connection:
        source = {int(value) for (value,) in connection.execute(
            "SELECT objectid FROM licensed_projects_st WHERE objectid IS NOT NULL")}
    visible = set(ids.astype("int64"))
    return {"status": "identifier comparison only", "source_ids": len(source),
            "website_ids": len(visible), "source_ids_absent_from_tiles": sorted(source - visible),
            "website_ids_absent_from_source": sorted(visible - source)}
