"""Run and verify the approved Obrasgov location derivative."""

import json
import sqlite3

from _shared import geopackage_summary, local_copy, run_stage, sha256
from brazil_project.io import Context, WorkflowError
from scripts.filter_obras_primary_state import verified_inputs


def build(project):
    """Snapshot translation → component QA → state check → approved exclusion."""
    run_stage(project, "obrasgov")
    return inspect_final(project)


def inspect_final(project):
    ctx = Context(project / "project.toml")
    if ctx.municipality:
        raise WorkflowError("This derivative requires national scope.")
    path = project / "outputs/maps/obrasgov-primary-state-filter/locations.gpkg"
    report = json.loads(ctx.require(ctx.artifact("obrasgov-primary-state-filter", "report.json")).read_text())
    if report.get("status") != "completed" or report.get("policy") != "exclude_entirely_outside_primary_state_v1":
        raise WorkflowError("The approved completed exclusion report is required.")
    # CONTRACT: An existing GeoPackage is current only with its verified QA/state lineage.
    verified_inputs(ctx)
    for relative, expected in report["inputs"].items():
        if sha256(ctx.require(ctx.root / relative)) != expected:
            raise WorkflowError("A producer input changed; rerun the Obrasgov stages: " + relative)
    if report["gis_outputs"]["locations.gpkg"] != sha256(path):
        raise WorkflowError("GeoPackage differs from its completed producer report.")
    summary = geopackage_summary(path, "map_components", expected_crs=4674, unique_key="component_id")
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        excluded = connection.execute('SELECT COUNT(*) FROM "excluded_primary_state"').fetchone()[0]
        other = connection.execute("SELECT COUNT(*) FROM map_components WHERE geometry_type NOT IN ('Point','LineString')").fetchone()[0]
        if other:
            raise WorkflowError("Non-point/line geometry appears in the map derivative.")
    if summary["features"] != report["map_components_after"] or excluded != report["excluded_components"]:
        raise WorkflowError("Export counts differ from the completed producer report.")
    summary["excluded_primary_state"] = excluded
    local_copy(project / "datasets/obrasgov", path)
    return summary
