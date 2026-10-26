"""Dataset notebooks must remain executable entry points with checked local outputs."""

from pathlib import Path
import sys

import geopandas as gpd
import nbformat
import pytest
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "datasets"))
from _shared import geopackage_summary, local_copy


@pytest.mark.parametrize("name", ["census", "obrasgov", "ibama", "communities"])
def test_notebook_has_real_build_and_saved_readable_results(name):
    notebook = nbformat.read(ROOT / "datasets" / name / "build.ipynb", as_version=4)
    nbformat.validate(notebook)
    code = "\n".join(cell.source for cell in notebook.cells if cell.cell_type == "code")
    assert 'BRAZIL_NOTEBOOK_REBUILD", "1"' in code
    assert "build(PROJECT)" in code or "calculate_indicators(PROJECT)" in code
    assert any(cell.cell_type == "markdown" and "**Why:**" in cell.source for cell in notebook.cells)
    assert any(output.output_type == "display_data" and "image/png" in output.data
               for cell in notebook.cells if cell.cell_type == "code"
               for output in cell.get("outputs", []))
    assert not [output for cell in notebook.cells if cell.cell_type == "code"
                for output in cell.get("outputs", []) if output.output_type == "error"]


def test_geopackage_summary_rejects_duplicate_final_identifiers(tmp_path):
    path = tmp_path / "duplicate.gpkg"
    frame = gpd.GeoDataFrame({"common_id": ["a", "a"]},
                             geometry=[Point(0, 0), Point(1, 1)], crs=4674)
    frame.to_file(path, layer="social", driver="GPKG")
    with pytest.raises(ValueError, match="unique"):
        geopackage_summary(path, "social", expected_crs=4674, unique_key="common_id")
    with pytest.raises(ValueError, match="Expected EPSG"):
        geopackage_summary(path, "social", expected_crs=5880)


def test_local_final_copy_is_self_contained_and_protects_unrelated_work(tmp_path):
    source = tmp_path / "source.gpkg"
    source.write_bytes(b"source")
    folder = tmp_path / "dataset"
    folder.mkdir()
    final = local_copy(folder, source)
    assert final.is_file() and not final.is_symlink() and final.read_bytes() == b"source"
    assert local_copy(folder, source) == final
    source.write_bytes(b"updated source")
    assert local_copy(folder, source).read_bytes() == b"updated source"
    (folder / ".final-gpkg.json").write_text('{"sha256":"stale","source":"../source.gpkg"}')
    assert local_copy(folder, source).read_bytes() == b"updated source"
    final.write_bytes(b"user file")
    with pytest.raises(FileExistsError, match="changed outside this pipeline"):
        local_copy(folder, source)
    assert final.read_bytes() == b"user file"
