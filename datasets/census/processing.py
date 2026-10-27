"""Readable entry points for the existing national census/map calculations."""

import json
import os
from pathlib import Path
import runpy
import tempfile
import uuid

import shapely

from _shared import FINAL_FILENAMES, geopackage_summary, local_copy, run_stage, sha256
from brazil_project.harmonisation.census import load_bundle
from brazil_project.io import Context, WorkflowError


def plot_harmonisation_flow():
    """Show the current crosswalk and common-area construction as a schematic."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")

    def box(x, y, width, height, label, colour):
        ax.add_patch(FancyBboxPatch((x - width / 2, y - height / 2), width, height,
                                    boxstyle="round,pad=0.012", facecolor=colour,
                                    edgecolor="#45606a", linewidth=1.2))
        ax.text(x, y, label, ha="center", va="center", fontsize=10.5, color="#172b36")

    def arrow(start, end):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15,
                                     linewidth=1.2, color="#45606a"))

    box(.5, .91, .40, .09, "2010 and 2022 tract polygons", "#e8f1f3")
    box(.25, .70, .39, .13, "Usual run: check saved overlap links\nfor positive polygon area", "#edf2f8")
    box(.75, .70, .39, .13, "Optional: recompute largest overlap\nin both directions nationally", "#edf2f8")
    box(.5, .48, .53, .14, "Connect all eligible links into groups\n1:1 · split · merge · many-to-many", "#dceeed")
    box(.25, .26, .39, .11, "Dissolve all 2022 pieces\nwithin each common_id", "#e8f1f3")
    box(.75, .26, .39, .11, "Aggregate each year's counts\nwithin the same common_id", "#e8f1f3")
    box(.5, .07, .46, .09, "One comparison-area record per common_id", "#c8e4df")
    for start, end in [((.5, .86), (.25, .78)), ((.5, .86), (.75, .78)),
                       ((.25, .62), (.5, .56)), ((.75, .62), (.5, .56)),
                       ((.5, .40), (.25, .33)), ((.5, .40), (.75, .33)),
                       ((.25, .19), (.5, .13)), ((.75, .19), (.5, .13))]:
        arrow(start, end)
    fig.tight_layout()
    return fig


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
    # The analytical comparison-area geometry stays full resolution.
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
    destination = project / "outputs/maps/notebook-exports" / FINAL_FILENAMES["census"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    cache = project / ".cache/dataset-notebooks"
    cache.mkdir(parents=True, exist_ok=True)
    exporter = runpy.run_path(str(project / "datasets/shared/scripts/export_census_gpkg.py"))
    with tempfile.TemporaryDirectory(prefix="census-", dir=cache) as temporary:
        source = Path(temporary) / "census_source.gpkg"
        prepare_map_geometries(ctx, source)
        staged = destination.with_name(".census-export-" + uuid.uuid4().hex + ".gpkg")
        try:
            exporter["run"](ctx, staged, source=source)
            result = geopackage_summary(staged, "comparison_areas", expected_crs=5880, unique_key="common_id")
            os.replace(staged, destination)
        finally:
            staged.unlink(missing_ok=True)
    result["file"] = str(local_copy(project / "datasets/census", destination))
    return result


def inspect_final(project, preview=False):
    path = project / "outputs/maps/notebook-exports" / FINAL_FILENAMES["census"]
    if preview and not path.exists():
        raise WorkflowError("Build the named census export before previewing it.")
    summary = geopackage_summary(path, "comparison_areas", expected_crs=5880, unique_key="common_id")
    # The other tables are part of the same deliverable, not separate datasets.
    import sqlite3
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        if connection.execute("SELECT 1 FROM gpkg_contents WHERE table_name='social'").fetchone():
            raise WorkflowError("Obsolete social layer remains in the final census GeoPackage.")
        for layer in ("overview", "field_dictionary", "export_metadata"):
            summary[layer + "_rows"] = connection.execute(f'SELECT COUNT(*) FROM "{layer}"').fetchone()[0]
    if not preview:
        summary["file"] = str(local_copy(project / "datasets/census", path))
    else:
        local = project / "datasets/census" / FINAL_FILENAMES["census"]
        if local.is_file() and sha256(local) == summary["sha256"]:
            summary["file"] = str(local)
    return summary
