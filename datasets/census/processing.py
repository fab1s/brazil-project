"""Readable entry points for the existing national census/map calculations."""

import json
import os
from pathlib import Path
import runpy
import tempfile
import uuid

import shapely

from _shared import geopackage_summary, local_copy, run_stage, sha256
from brazil_project.harmonisation.census import load_bundle
from brazil_project.io import Context, WorkflowError


def calculate_indicators(project):
    """Run validated complete-group harmonisation, then the 2010/2022 indicators."""
    run_stage(project, "indicators")


def build(project):
    """Recalculate the census stages and publish one checked local GeoPackage."""
    calculate_indicators(project)
    return export_geopackage(project)


def prepare_map_geometries(ctx, source):
    """Build the same merged areas and display overview used by build_web_map.py."""
    web = runpy.run_path(str(ctx.root / "datasets/shared/scripts/build_web_map.py"))
    bundle, manifest = load_bundle(ctx, names=["comparison_geometry"])
    metrics = web["measure_fields"](ctx, bundle["common_geometry_2022"])
    members = bundle["lookup_2022"][["id_2022", "common_id"]].copy()
    members["code_muni"] = members.id_2022.str[:7]
    members = members[["common_id", "code_muni"]].drop_duplicates()
    reference = bundle["comparison_geometry"]
    reference = reference[reference.common_id.notna()][["id_2022", "geometry"]].copy()
    reference["code_muni"] = reference.id_2022.str[:7]
    # COMPATIBILITY: The public map simplifies only municipality display boundaries.
    # The analytical common-area geometry in `social` stays full resolution.
    reference.geometry = shapely.make_valid(shapely.simplify(reference.geometry.array, 500, preserve_topology=True))
    overview = reference[["code_muni", "geometry"]].dissolve(by="code_muni", as_index=False)
    overview = overview.merge(web["overview_metrics"](metrics, members), on="code_muni", validate="one_to_one")
    metrics.to_file(source, layer="social", driver="GPKG")
    overview.to_file(source, layer="overview", driver="GPKG")
    indicator_hashes = {key: sha256(ctx.artifact("indicators", key + ".parquet"))
                        for key in [*web["INDICATORS"], "income"]}
    contract = {"harmonisation_version": manifest["version"],
                "indicator_checksums": indicator_hashes,
                "export_policy": "merged-common-area-v1"}
    source.with_name("prepared.json").write_text(json.dumps({
        "contract": contract, "database_sha256": sha256(source),
        "feature_count": len(metrics), "overview_municipalities": len(overview)}, indent=2) + "\n")
    return {"common_areas": len(metrics), "municipalities": len(overview)}


def export_geopackage(project):
    """Export concise English fields after checking the original map calculations."""
    ctx = Context(project / "datasets/project.toml")
    if ctx.municipality:
        raise WorkflowError("The collaborator GeoPackage requires national scope.")
    destination = project / "outputs/maps/notebook-exports/social.gpkg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    cache = project / ".cache/dataset-notebooks"
    cache.mkdir(parents=True, exist_ok=True)
    exporter = runpy.run_path(str(project / "datasets/shared/scripts/export_social_gpkg.py"))
    with tempfile.TemporaryDirectory(prefix="census-", dir=cache) as temporary:
        source = Path(temporary) / "social.gpkg"
        prepare_map_geometries(ctx, source)
        staged = destination.with_name(".social-" + uuid.uuid4().hex + ".gpkg")
        try:
            exporter["run"](ctx, staged, source=source)
            result = geopackage_summary(staged, "social", expected_crs=5880, unique_key="common_id")
            os.replace(staged, destination)
        finally:
            staged.unlink(missing_ok=True)
    local_copy(project / "datasets/census", destination)
    result["file"] = str(destination)
    return result


def inspect_final(project, preview=False):
    path = project / "outputs/maps/notebook-exports/social.gpkg"
    if preview and not path.exists():
        path = project / "outputs/maps/social-clean/social.gpkg"
    summary = geopackage_summary(path, "social", expected_crs=5880, unique_key="common_id")
    # The other tables are part of the same deliverable, not separate datasets.
    import sqlite3
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        for layer in ("overview", "field_dictionary", "export_metadata"):
            summary[layer + "_rows"] = connection.execute(f'SELECT COUNT(*) FROM "{layer}"').fetchone()[0]
    if not preview:
        local_copy(project / "datasets/census", path)
    return summary
