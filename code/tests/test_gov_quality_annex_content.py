"""The concise assessment retains an executable, complete and readable annex."""
import hashlib
import re
import zipfile
from pathlib import Path
import mistune

from brazil_project import report_engine as engine


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "research/reports"
ORIGINAL_ARCHIVE = ROOT / "data/archive/project-tools/gov-data-quality-before-annex-20261007.zip"
ORIGINAL_MEMBER = "research/reports/gov_data_quality.md"
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def original_report():
    with zipfile.ZipFile(ORIGINAL_ARCHIVE) as archive:
        return archive.read(ORIGINAL_MEMBER).decode()


def test_annex_preserves_all_original_cell_code_and_explanations():
    original = original_report()
    annex = (REPORTS / "gov_data_quality_annex.md").read_text()
    original_cells, _ = engine.parse_report(original)
    annex_cells, _ = engine.parse_report(annex)
    assert [cell[1] for cell in annex_cells] == [cell[1] for cell in original_cells]
    assert [cell[2] for cell in annex_cells] == [cell[2] for cell in original_cells]
    # The title and navigation can change; original methods, captions, code
    # links and caveats remain authored text, independent of refreshed results.
    preserved_body = engine.authored_text(original).split("\n", 1)[1]
    assert preserved_body in engine.authored_text(annex)
    assert "gov_data_quality.md" in annex


def test_original_eleven_figure_assets_remain_exact_and_annex_is_complete():
    original_paths = IMAGE.findall(original_report())
    assert len(original_paths) == 11
    for relative in original_paths:
        asset = REPORTS / relative
        assert asset.is_file()
        assert hashlib.sha256(asset.read_bytes()).hexdigest() == asset.stem
    annex = (REPORTS / "gov_data_quality_annex.md").read_text()
    current_paths = IMAGE.findall(annex)
    assert len(current_paths) == 11
    for relative in current_paths:
        asset = REPORTS / relative
        assert hashlib.sha256(asset.read_bytes()).hexdigest() == asset.stem


def test_main_is_a_short_executable_summary_with_three_figures_and_annex_link():
    main = (REPORTS / "gov_data_quality.md").read_text()
    cells, outputs = engine.parse_report(main)
    assert [cell[1] for cell in cells] == ["gov_data_quality_summary"]
    assert len(outputs) == 1
    assert len(IMAGE.findall(main)) == 3
    assert "gov_data_quality_annex.md" in main
    # Reader length excludes the supporting execution code in an HTML comment.
    html = mistune.create_markdown(escape=False, plugins=["table"])(main)
    visible = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    assert len(re.sub(r'<[^>]+>', ' ', visible).split()) < 1100
    assert "census_annual_coverage" in cells[0][2]
    assert "joint_fully_observed" in cells[0][2]
    for name in ("location-overview.png", "date-coverage.png", "income-coverage.png"):
        assert name in cells[0][2]


def test_main_retains_quality_flag_timing_completeness_and_aggregate_limits():
    main = (REPORTS / "gov_data_quality.md").read_text().lower()
    for concept in ("national", "projects", "2022", "complete usable", "income",
                    "registration", "construction", "planned", "review", "individual"):
        assert concept in main
    assert "shared_coordinate_threshold" in main
    assert "valid_point_projects" in main
    assert "not" in main and "correct" in main
    assert "removed" in main
