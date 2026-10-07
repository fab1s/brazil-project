"""National QA is read-only, independently runnable and protected by report publication."""
import base64
import json
from pathlib import Path

import pandas as pd
import pytest

from brazil_project import cli, report_engine as engine
from brazil_project.io import WorkflowError

NAME = "gov_data_quality"
ANNEX = "gov_data_quality_annex"
STAGE = "gov-data-quality"
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6qxsAAAAASUVORK5CYII=")


def config(tmp_path):
    path = tmp_path / "custom.toml"
    path.write_text('[project]\nroot="."\nmunicipality=""\n'
                    '[census]\nrecompute_harmonisation=false\n'
                    '[gov_quality]\nsource="data/reference/custom-frozen-projects.parquet"\n')
    return path


def test_national_audit_is_registered_without_processing_or_acquisition_dependencies():
    assert cli.expand([STAGE]) == [STAGE]
    assert STAGE in cli.STAGES
    assert not set(cli.expand(cli.STAGES)).intersection(cli.ACQUISITION)
    assert engine.REPORTS[NAME] == (STAGE,)
    assert engine.REPORTS[ANNEX] == (STAGE,)
    assert engine.REPORT_ANNEXES[NAME] == (ANNEX,)
    assert not {NAME, ANNEX}.intersection(engine.SCOPED)
    assert "infrastructure-proximity" not in cli.STAGES
    assert "acquire-network" not in cli.ACQUISITION


def test_custom_configuration_reaches_processing_and_report_without_other_stages(tmp_path, monkeypatch):
    calls = []
    reports = []
    custom = config(tmp_path)
    def dispatch(ctx, stage):
        calls.append((stage, str(ctx.config_path), ctx.config["gov_quality"]["source"]))
        return {}
    monkeypatch.setattr(cli, "dispatch", dispatch)
    monkeypatch.setattr(cli, "render_report", lambda ctx, name: reports.append(name) or {"report": name, "status": "completed"})
    assert cli.main(["run", STAGE, "--config", str(custom)]) == 0
    assert calls == [(STAGE, str(custom), "data/reference/custom-frozen-projects.parquet")]
    assert reports == [ANNEX, NAME]


@pytest.mark.parametrize("arguments", [["run", STAGE], ["report", NAME, "--from-saved"], ["report", ANNEX, "--from-saved"]])
def test_national_scope_rejection_precedes_writes_or_report_updates(tmp_path, monkeypatch, arguments):
    custom = config(tmp_path)
    monkeypatch.setattr(cli, "dispatch", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected processing")))
    monkeypatch.setattr(cli, "render_report", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected report")))
    assert cli.main(arguments + ["--config", str(custom), "--municipality", "3106200"]) == 1
    assert not (tmp_path / "data/intermediate").exists()


def test_saved_report_does_not_process_or_acquire(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(cli, "dispatch", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected processing")))
    monkeypatch.setattr(cli, "render_report", lambda ctx, name: seen.append(name) or {"report": name, "status": "completed"})
    assert cli.main(["report", NAME, "--from-saved", "--config", str(config(tmp_path))]) == 0
    assert seen == [ANNEX, NAME]


def test_report_with_processing_runs_one_stage_then_annex_and_summary(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(cli, "dispatch", lambda ctx, stage: seen.append(stage) or {})
    monkeypatch.setattr(cli, "render_report", lambda ctx, name: seen.append(name) or {"report": name, "status": "completed"})
    assert cli.main(["report", NAME, "--config", str(config(tmp_path))]) == 0
    assert seen == [STAGE, ANNEX, NAME]


def test_all_saved_reports_publish_each_annex_once_before_summary_without_processing(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(cli, "dispatch", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected processing")))
    monkeypatch.setattr(cli, "render_report", lambda ctx, name: seen.append(name) or {"report": name, "status": "completed"})
    assert cli.main(["report", "all", "--from-saved", "--config", str(config(tmp_path))]) == 0
    assert set(seen) == set(engine.REPORTS)
    assert len(seen) == len(set(seen))
    assert seen.index(ANNEX) < seen.index(NAME)


def test_annex_expansion_deduplicates_and_rejects_invalid_relationships(monkeypatch):
    assert engine.expand_reports([NAME, ANNEX, NAME]) == [ANNEX, NAME]
    monkeypatch.setitem(engine.REPORT_ANNEXES, ANNEX, (NAME,))
    with pytest.raises(WorkflowError, match="Circular report annex"):
        engine.expand_reports([NAME])
    with pytest.raises(WorkflowError, match="Unknown report"):
        engine.expand_reports(["nonexistent"])


@pytest.mark.parametrize("arguments", [["run", STAGE], ["report", NAME, "--from-saved"]])
def test_annex_failure_blocks_summary_and_preserves_previous_content(tmp_path, monkeypatch, arguments):
    previous = tmp_path / "research/reports" / (NAME + ".md")
    previous.parent.mkdir(parents=True)
    previous.write_text("Prior reviewed concise report.")
    seen = []
    monkeypatch.setattr(cli, "dispatch", lambda ctx, stage: {})
    def render(ctx, name):
        seen.append(name)
        if name == ANNEX:
            raise WorkflowError("Required annex figure is absent")
        raise AssertionError("Summary published after its annex failed")
    monkeypatch.setattr(cli, "render_report", render)
    assert cli.main(arguments + ["--config", str(config(tmp_path))]) == 1
    assert seen == [ANNEX]
    assert previous.read_text() == "Prior reviewed concise report."
    evidence = json.loads((tmp_path / "data/intermediate/runs/report.json").read_text())
    assert evidence["reports"] == [
        {"report": ANNEX, "status": "failed", "error": "Required annex figure is absent"},
        {"report": NAME, "status": "blocked", "error": "Required annex did not complete: " + ANNEX},
    ]
    if evidence["stages"]:
        assert evidence["stages"][0]["status"] == "completed"


def test_failed_audit_preserves_prior_report_while_all_independent_work_continues(tmp_path, monkeypatch):
    custom = config(tmp_path)
    previous = tmp_path / "research/reports" / (NAME + ".md")
    previous.parent.mkdir(parents=True)
    previous.write_text("Prior reviewed report.")
    calls = []
    reports = []
    def dispatch(ctx, stage):
        calls.append(stage)
        if stage == STAGE:
            raise WorkflowError("Frozen location provenance differs; explicitly regenerate the source stage.")
        return {}
    monkeypatch.setattr(cli, "dispatch", dispatch)
    monkeypatch.setattr(cli, "render_report", lambda ctx, name: reports.append(name) or {"report": name, "status": "completed"})
    assert cli.main(["run", "all", "--config", str(custom)]) == 1
    assert previous.read_text() == "Prior reviewed report."
    assert STAGE in calls and "ibama" in calls and "charts" in calls
    assert NAME not in reports and ANNEX not in reports and "obrasgov_preprocessing" in reports
    evidence = json.loads((tmp_path / "data/intermediate/runs/report.json").read_text())
    assert next(row for row in evidence["stages"] if row["stage"] == STAGE)["status"] == "blocked"
    assert next(row for row in evidence["reports"] if row["report"] == NAME)["status"] == "blocked"


def test_audit_remains_independent_after_harmonisation_failure(tmp_path, monkeypatch):
    calls = []
    reports = []
    def dispatch(ctx, stage):
        calls.append(stage)
        if stage == "harmonisation":
            raise RuntimeError("Broken census processing input")
        return {}
    monkeypatch.setattr(cli, "dispatch", dispatch)
    monkeypatch.setattr(cli, "render_report", lambda ctx, name: reports.append(name) or {"report": name, "status": "completed"})
    assert cli.main(["run", "all", "--config", str(config(tmp_path))]) == 1
    assert STAGE in calls and NAME in reports
    assert reports.count(ANNEX) == reports.count(NAME) == 1
    assert reports.index(ANNEX) < reports.index(NAME)
    assert "indicators" not in calls


def test_report_failure_does_not_relabel_completed_audit(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "dispatch", lambda ctx, stage: {})
    monkeypatch.setattr(cli, "render_report", lambda *args: (_ for _ in ()).throw(RuntimeError("Missing current figure")))
    assert cli.main(["run", STAGE, "--config", str(config(tmp_path))]) == 1
    record = json.loads((tmp_path / "data/intermediate/runs/report.json").read_text())
    assert record["stages"][0]["status"] == "completed"
    assert record["reports"][0]["report"] == ANNEX
    assert record["reports"][0]["status"] == "failed"
    assert record["reports"][1]["report"] == NAME
    assert record["reports"][1]["status"] == "blocked"


@pytest.fixture
def report_project(tmp_path):
    ctx = engine.context(config(tmp_path))
    reports = Path(__file__).resolve().parents[2] / "research/reports"
    for name in (ANNEX, NAME):
        original = reports / (name + ".md")
        source = tmp_path / "research/reports" / original.name
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(original.read_bytes())
    source = tmp_path / "research/reports" / (ANNEX + ".md")
    tables = ["identity_summary", "missingness", "location_summary", "shared_coordinate_thresholds", "coordinate_sites",
              "dates_summary", "budget_summary", "census_annual_coverage", "linkage_constraints"]
    for name in tables:
        ctx.write_table(pd.DataFrame({"Measure": ["Current saved value"], "Value": [1250.0]}), STAGE, name)
    ctx.write_table(pd.DataFrame({'year': [2010, 2022, 2022, 2022],
                                 'measure': ['race_ratio_available', 'race_ratio_available',
                                             'race_ratio_fully_observed', 'joint_fully_observed'],
                                 'n_common_areas': [100, 101, 99, 98],
                                 'share_pct': [90., 91., 90., 89.]}), STAGE, 'census_annual_coverage')
    figures = {}
    for name in ("location-overview.png", "point-project-coverage.png", "shared-coordinates-by-state.png",
                 "shared-coordinate-distribution.png", "attribute-missingness.png", "category-consistency.png",
                 "date-coverage.png", "budget-distribution.png", "census-coverage-by-state.png",
                 "income-coverage.png", "income-race-observed.png"):
        image = tmp_path / "outputs/figures/gov-data-quality" / name
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(PNG)
        figures[name] = str(image.relative_to(tmp_path))
    ctx.report(STAGE, {"source_rows": 134929, "distinct_projects": 129961, "geometry_components": 230356,
                       "status": "completed", "as_of_date": "2026-10-07", "tables": tables, "figures": figures,
                       'attributes': {'projects_with_effective_start': 1750, 'projects_with_effective_start_pct': 1.35,
                                      'projects_with_effective_finish': 1241, 'projects_with_effective_finish_pct': .95,
                                      'projects_with_budget_001': 20, 'projects_with_budget_001_pct': 16.,
                                      'projects_with_category_review': 45},
                       'locations': {'shared_point_projects': 30, 'valid_point_projects': 100, 'shared_coordinate_threshold': 25},
                       'census': {'n_common_areas': 110},
                       "warnings": ["Coordinates are recorded locations, not certified project sites."]})
    engine.stamp_producer(ctx, STAGE)
    return ctx, source


def test_report_preserves_narrative_exact_figure_bytes_and_saved_table_values(report_project):
    ctx, source = report_project
    before = source.read_text()
    cells, _ = engine.parse_report(before)
    assert [cell[1] for cell in cells] == ["gov_data_quality_lineage", "gov_data_quality_locations", "gov_data_quality_shared_coordinates",
                                         "gov_data_quality_categories", "gov_data_quality_dates_budgets", "gov_data_quality_census", "gov_data_quality_readiness"]
    result = engine.render_report(ctx, ANNEX)
    assert result["status"] == "completed"
    after = source.read_text()
    assert engine.authored_text(after) == engine.authored_text(before)
    assert "1,250.0000" in after and "134929" in after
    assert "not certified project sites" in after
    images = list((source.parent / "assets").glob("*.png"))
    assert images and all(image.read_bytes() == PNG for image in images)
    engine.render_report(ctx, ANNEX)
    assert source.read_text() == after


def test_concise_summary_refreshes_saved_counts_preserves_narrative_and_limits_figures(report_project):
    ctx, _ = report_project
    source = ctx.root / "research/reports" / (NAME + ".md")
    before = source.read_text()
    assert [cell[1] for cell in engine.parse_report(before)[0]] == ["gov_data_quality_summary"]
    engine.render_report(ctx, NAME)
    after = source.read_text()
    assert engine.authored_text(after) == engine.authored_text(before)
    assert ANNEX + ".md" in after
    assert after.count("![Generated figure](assets/") == 3
    assert "4,968" in after and "129,961" in after
    record = json.loads(ctx.artifact(STAGE, "report.json").read_text())
    record["locations"]["shared_point_projects"] = 40
    ctx.report(STAGE, record)
    engine.render_report(ctx, NAME)
    refreshed = source.read_text()
    assert "40.00%" in refreshed
    assert engine.authored_text(refreshed) == engine.authored_text(before)


def test_missing_current_figure_preserves_previous_report(report_project):
    ctx, source = report_project
    before = source.read_bytes()
    record = json.loads(ctx.artifact(STAGE, "report.json").read_text())
    (ctx.root / record["figures"]["date-coverage.png"]).unlink()
    with pytest.raises(WorkflowError, match="Missing input"):
        engine.render_report(ctx, ANNEX)
    assert source.read_bytes() == before


def test_omitted_required_figure_manifest_cannot_produce_partial_success(report_project):
    ctx, source = report_project
    before = source.read_bytes()
    record = json.loads(ctx.artifact(STAGE, "report.json").read_text())
    record['figures'].pop('budget-distribution.png')
    ctx.report(STAGE, record)
    with pytest.raises(WorkflowError, match='Missing required national quality figures'):
        engine.render_report(ctx, ANNEX)
    assert source.read_bytes() == before


def test_long_record_audit_is_explicitly_previewed_not_dumped(report_project):
    ctx, source = report_project
    ctx.write_table(pd.DataFrame({"Audit row": ["review-row-" + str(i) for i in range(35)]}), STAGE, "coordinate_sites")
    engine.render_report(ctx, ANNEX)
    rendered = source.read_text()
    assert "Showing the first 20 of 35 rows" in rendered
    assert "review-row-19" in rendered and "review-row-20" not in rendered


def test_uninterpreted_current_figure_blocks_publication(report_project):
    ctx, source = report_project
    before = source.read_bytes()
    record = json.loads(ctx.artifact(STAGE, "report.json").read_text())
    record["figures"]["unexplained-new-figure.png"] = next(iter(record["figures"].values()))
    ctx.report(STAGE, record)
    with pytest.raises(WorkflowError, match="lack a report interpretation"):
        engine.render_report(ctx, ANNEX)
    assert source.read_bytes() == before
