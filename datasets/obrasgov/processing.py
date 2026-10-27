"""Run and verify the approved Obrasgov location derivative."""

import json
import os
from pathlib import Path
import sqlite3
import tempfile

from _shared import FINAL_FILENAMES, geopackage_summary, local_copy, sha256
from english_export import export, verify_export
from brazil_project.io import Context, WorkflowError
from scripts.filter_obras_primary_state import verified_inputs


def verify_producer(project):
    ctx = Context(project / "datasets/project.toml")
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
    return path, summary


def export_saved(project):
    """Apply English handoff labels to the verified saved map derivative."""
    source, source_summary = verify_producer(project)
    destination = project / "outputs/maps/notebook-exports" / FINAL_FILENAMES["obrasgov"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".obrasgov-", suffix=".gpkg", dir=destination.parent, delete=False) as temp:
        staged = Path(temp.name)
    staged.unlink()
    try:
        export(source, staged, "obrasgov", source_summary["sha256"])
        verify_export(source, staged, "obrasgov", source_summary["sha256"])
        os.replace(staged, destination)
    finally:
        staged.unlink(missing_ok=True)
    return inspect_final(project)


def inspect_final(project):
    source, source_summary = verify_producer(project)
    path = project / "outputs/maps/notebook-exports" / FINAL_FILENAMES["obrasgov"]
    summary = geopackage_summary(path, "map_components", expected_crs=4674,
                                 unique_key="component_id")
    verify_export(source, path, "obrasgov", source_summary["sha256"])
    if summary["features"] != source_summary["features"]:
        raise WorkflowError("Obrasgov English export changed the retained component count.")
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
        excluded = connection.execute('SELECT COUNT(*) FROM "excluded_primary_state"').fetchone()[0]
    if excluded != source_summary["excluded_primary_state"]:
        raise WorkflowError("Obrasgov English export changed the excluded component count.")
    summary["excluded_primary_state"] = excluded
    summary["file"] = str(local_copy(project / "datasets/obrasgov", path))
    return summary
