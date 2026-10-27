"""Readable entry points for the existing national census/map calculations."""

import json
import os
from pathlib import Path
import runpy
import tempfile
import uuid

import shapely

from _shared import FINAL_FILENAMES, geopackage_summary, local_copy, sha256
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


def example_tracts(ctx, bundle):
    """Read a small real split for display; all analytical operations stay in cells."""
    from brazil_project.harmonisation.census import prepare, read_ids
    sizes, lookup = bundle['group_sizes'], bundle['lookup_2022']
    local = set(lookup.loc[lookup.id_2022.str.startswith('3106200'), 'common_id'])
    choices = sizes[(sizes.n_2010 == 1) & (sizes.n_2022 == 2)].copy()
    preferred = choices[choices.common_id.isin(local)]
    if len(preferred):
        choices = preferred
    cid = str(choices.sort_values('common_id').iloc[0].common_id)
    ids = {year: bundle[f'lookup_{year}'].loc[
        bundle[f'lookup_{year}'].common_id.eq(cid), f'id_{year}'] for year in (2010, 2022)}
    cfg = ctx.config['census']
    old = prepare(read_ids(ctx.path('census', 'tracts'), 2010, ids[2010], '2010'),
                  2010, cfg['crs'], cfg['precision_grid'])
    if cfg.get('recompute_harmonisation', False):
        new = prepare(read_ids(ctx.path('census', 'tracts'), 2022, ids[2022], '2022'),
                      2022, cfg['crs'], cfg['precision_grid'])
    else:
        new = read_ids(ctx.path('census', 'baseline_geometry'), 2022, ids[2022], baseline=True).to_crs(cfg['crs'])
    return cid, old, new


def plot_group(old, new, merged, common_id):
    """Keep map styling out of the visible transformation cells."""
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    old.plot(ax=axes[0], facecolor='#e7c19a', edgecolor='#71502f')
    new.plot(ax=axes[1], column='id_2022', categorical=True, cmap='Set2', edgecolor='#45606a')
    merged.plot(ax=axes[2], facecolor='#9acfc1', edgecolor='#24564b')
    for frame, year, ax in [(old, 2010, axes[0]), (new, 2022, axes[1])]:
        for _, row in frame.iterrows():
            point = row.geometry.representative_point()
            ax.text(point.x, point.y, str(row[f'id_{year}'])[-5:], ha='center', fontsize=8)
    a, b = old.total_bounds, new.total_bounds
    xmin, ymin, xmax, ymax = min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])
    margin = max(xmax - xmin, ymax - ymin) * .06
    for ax, title in zip(axes, ['2010 member tract', '2022 member pieces', 'Final merged comparison area']):
        ax.set_xlim(xmin - margin, xmax + margin)
        ax.set_ylim(ymin - margin, ymax + margin)
        ax.set_title(title, fontsize=11)
        ax.axis('off')
    fig.suptitle('Real split group ' + common_id + ' · same scale; labels show tract-code suffixes')
    fig.tight_layout()
    return fig


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
    local_copy(project / "datasets/census", destination)
    return inspect_final(project)


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
