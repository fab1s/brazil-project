"""Verify and deliver the unchanged IBGE 2022 community geometry baseline."""

import os
from pathlib import Path
import shutil
import sqlite3
import tempfile

import pyogrio

from _shared import baseline_checksum, geopackage_summary, local_copy, sha256
from brazil_project.io import WorkflowError


def source_file(project):
    return project / "data/processed/ibge/Data/favelas_2022.gpkg"


def build(project):
    """Preserve the supplied geography byte for byte; no inferred changes."""
    source = source_file(project)
    expected = baseline_checksum(project, source)
    destination = project / "outputs/maps/notebook-exports/communities.gpkg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".communities-", suffix=".gpkg", dir=destination.parent, delete=False) as temp:
        staged = Path(temp.name)
    try:
        shutil.copyfile(source, staged)
        if sha256(staged) != expected:
            raise WorkflowError("Community GeoPackage copy failed checksum verification.")
        geopackage_summary(staged, "favelas_2022", expected_crs=4674, unique_key="cd_fcu")
        os.replace(staged, destination)
    finally:
        staged.unlink(missing_ok=True)
    local_copy(project / "datasets/communities", destination)
    return inspect_final(project)


def inspect_final(project, preview=False):
    source = source_file(project)
    expected = baseline_checksum(project, source)
    path = project / "outputs/maps/notebook-exports/communities.gpkg"
    if preview and not path.exists():
        path = source
    result = geopackage_summary(path, "favelas_2022", expected_crs=4674, unique_key="cd_fcu")
    if result["sha256"] != expected:
        raise WorkflowError("Community file differs from the preserved, verified baseline.")
    if not preview:
        local_copy(project / "datasets/communities", path)
    return result


def website_id_check(project):
    """Compare unique community codes at the website archive's highest zoom."""
    archive = project / "outputs/maps/website/data/favelas.pmtiles"
    if not archive.is_file():
        return {"status": "local website archive unavailable"}
    tiles = pyogrio.read_dataframe(archive, layer="favelas_2022",
                                   columns=["cd_fcu"], read_geometry=False)
    with sqlite3.connect(source_file(project)) as connection:
        source = {str(value) for (value,) in connection.execute(
            "SELECT cd_fcu FROM favelas_2022 WHERE cd_fcu IS NOT NULL")}
    visible = set(tiles.cd_fcu.dropna().astype(str))
    return {"status": "identifier comparison only", "source_ids": len(source),
            "website_ids": len(visible), "source_ids_absent_from_tiles": sorted(source - visible),
            "website_ids_absent_from_source": sorted(visible - source)}
