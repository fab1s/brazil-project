"""Proximity CLI integration preserves explicit acquisition and scoped report contracts."""
import base64
import json
from pathlib import Path
import sys
from types import ModuleType

import pandas as pd
import pytest

from brazil_project import cli, report_engine as engine
from brazil_project.io import WorkflowError

NAME = "infrastructure_proximity"
STAGE = "infrastructure-proximity"
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6qxsAAAAASUVORK5CYII=")


def config(tmp_path):
    path = tmp_path / "custom.toml"
    path.write_text('[project]\nroot="."\nmunicipality=""\n'
                    '[census]\nrecompute_harmonisation=false\n'
                    '[proximity]\nnetwork="data/reference/custom-road-network.graphml"\n')
    return path


def test_proximity_dependency_order_never_acquires_or_reprocesses_national_obrasgov():
    assert cli.expand([STAGE]) == ["harmonisation", "indicators", STAGE]
    assert not set(cli.expand(cli.STAGES)).intersection(cli.ACQUISITION)
    assert "acquire-network" in cli.ACQUISITION
    assert engine.REPORTS[NAME] == (STAGE,)
    assert NAME in engine.SCOPED


def test_custom_config_and_scoped_stage_flow_are_passed_to_reports(tmp_path, monkeypatch):
    calls = []
    reports = []
    custom = config(tmp_path)

    def dispatch(ctx, stage):
        calls.append((stage, ctx.municipality, ctx.config["proximity"]["network"], str(ctx.intermediate)))
        return {}

    def render(ctx, name):
        reports.append((name, ctx.municipality, str(ctx.config_path)))
        return {"report": name, "status": "completed"}

    monkeypatch.setattr(cli, "dispatch", dispatch)
    monkeypatch.setattr(cli, "render_report", render)
    assert cli.main(["run", STAGE, "--config", str(custom), "--municipality", "3106200"]) == 0
    assert [row[0] for row in calls] == ["harmonisation", "indicators", STAGE]
    assert all(row[1:3] == ("3106200", "data/reference/custom-road-network.graphml") for row in calls)
    assert all("municipality_3106200" in row[3] for row in calls)
    assert (NAME, "3106200", str(custom)) in reports
    assert not any(name.startswith("obrasgov") for name, *_ in reports)


def test_explicit_network_acquisition_dispatches_only_requested_action(tmp_path, monkeypatch):
    module = ModuleType("brazil_project.infrastructure.proximity")
    calls = []
    module.acquire_network = lambda ctx: calls.append("acquire-network") or {}
    module.run = lambda ctx: (_ for _ in ()).throw(AssertionError("analysis started during acquisition"))
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(cli, "render_report", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected report")))
    assert cli.main(["run", "acquire-network", "--config", str(config(tmp_path))]) == 0
    assert calls == ["acquire-network"]


def test_saved_report_does_not_process_or_acquire(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(cli, "dispatch", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected processing")))
    monkeypatch.setattr(cli, "render_report", lambda ctx, name: seen.append(name) or {"report": name, "status": "completed"})
    assert cli.main(["report", NAME, "--from-saved", "--config", str(config(tmp_path))]) == 0
    assert seen == [NAME]


def test_processing_failure_keeps_proximity_report_and_other_reports_continue(tmp_path, monkeypatch):
    custom = config(tmp_path)
    previous = tmp_path / "research/reports" / (NAME + ".md")
    previous.parent.mkdir(parents=True)
    previous.write_text("Prior reviewed report.")
    calls = []
    reports = []

    def dispatch(ctx, stage):
        calls.append(stage)
        if stage == STAGE:
            raise WorkflowError("Missing declared network. Run acquire-network explicitly or import a documented network.")
        return {}

    monkeypatch.setattr(cli, "dispatch", dispatch)
    monkeypatch.setattr(cli, "render_report", lambda ctx, name: reports.append(name) or {"report": name, "status": "completed"})
    assert cli.main(["run", "all", "--config", str(custom)]) == 1
    assert previous.read_text() == "Prior reviewed report."
    assert STAGE in calls and "ibama" in calls and "charts" in calls
    assert NAME not in reports and "obrasgov_preprocessing" in reports
    evidence = json.loads((tmp_path / "data/intermediate/runs/report.json").read_text())
    stage_row = next(row for row in evidence["stages"] if row["stage"] == STAGE)
    report_row = next(row for row in evidence["reports"] if row["report"] == NAME)
    assert stage_row["status"] == "blocked" and report_row["status"] == "blocked"
    assert "acquire-network" in stage_row["error"]


def test_report_failure_does_not_relabel_completed_proximity_processing(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "dispatch", lambda ctx, stage: {})

    def render(ctx, name):
        if name == NAME:
            raise RuntimeError("Malformed result figure")
        return {"report": name, "status": "completed"}

    monkeypatch.setattr(cli, "render_report", render)
    assert cli.main(["run", STAGE, "--config", str(config(tmp_path))]) == 1
    record = json.loads((tmp_path / "data/intermediate/runs/report.json").read_text())
    assert next(row for row in record["stages"] if row["stage"] == STAGE)["status"] == "completed"
    assert next(row for row in record["reports"] if row["report"] == NAME)["status"] == "failed"


@pytest.fixture
def report_project(tmp_path):
    custom = config(tmp_path)
    ctx = engine.context(custom)
    original = Path(__file__).resolve().parents[2] / "research/reports" / (NAME + ".md")
    source = tmp_path / "research/reports" / original.name
    source.parent.mkdir(parents=True)
    source.write_bytes(original.read_bytes())
    ctx.write_table(pd.DataFrame({"common_id": ["area-001"], "distance_m": [1250.0]}), STAGE, "analysis")
    tables = ["sample_audit", "support_counts", "model_coverage", "contrasts", "correlations", "residual_spatial"]
    for name in tables:
        ctx.write_table(pd.DataFrame({"Measure": ["Current saved value"], "Value": [1250.0]}), STAGE, name)
    figures = {}
    for name in ("income-race-support.png", "distance-predictions.png", "adjusted-contrasts.png"):
        image = tmp_path / "outputs/figures/infrastructure-proximity/configured" / name
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(PNG)
        figures[name] = str(image.relative_to(tmp_path))
    ctx.report(STAGE, {"model": {"status": "estimated", "tables": tables}, "study_municipalities": ["3106200"],
                       "origins": 1, "total_project_points": 2, "distinct_projects": 1,
                       "status": "completed", "route_status_counts": {"routed": 1}, "figures": figures})
    engine.stamp_producer(ctx, STAGE)
    return ctx, source


def test_new_report_is_executable_and_preserves_narrative_exact_figures_and_tables(report_project):
    ctx, source = report_project
    before = source.read_text()
    cells, _ = engine.parse_report(before)
    assert [cell[1] for cell in cells] == ["infrastructure_proximity_coverage", "infrastructure_proximity_support",
                                         "infrastructure_proximity_models", "infrastructure_proximity_diagnostics"]
    result = engine.render_report(ctx, NAME)
    assert result["status"] == "completed"
    after = source.read_text()
    assert engine.authored_text(after) == engine.authored_text(before)
    assert "1,250.0000" in after and "3106200" in after
    images = list((source.parent / "assets").glob("*.png"))
    assert images and all(image.read_bytes() == PNG for image in images)
    engine.render_report(ctx, NAME)
    assert source.read_text() == after


def test_missing_current_figure_preserves_previous_report(report_project):
    ctx, source = report_project
    before = source.read_bytes()
    record = json.loads(ctx.artifact(STAGE, "report.json").read_text())
    (ctx.root / record["figures"]["distance-predictions.png"]).unlink()
    with pytest.raises(WorkflowError, match="Missing input"):
        engine.render_report(ctx, NAME)
    assert source.read_bytes() == before


def test_scoped_proximity_report_does_not_replace_maintained_source(report_project):
    ctx, source = report_project
    before = source.read_bytes()
    scoped = engine.context(ctx.config_path, "3106200")
    for name in ("analysis", "sample_audit", "support_counts", "model_coverage", "contrasts", "correlations", "residual_spatial"):
        scoped.write_table(ctx.table(STAGE, name), STAGE, name)
    scoped.report(STAGE, json.loads(ctx.artifact(STAGE, "report.json").read_text()))
    engine.stamp_producer(scoped, STAGE)
    result = engine.render_report(scoped, NAME)
    assert source.read_bytes() == before
    copied = ctx.root / result["output"]
    assert "municipality_3106200" in str(copied)
    assert "../../../code/brazil_project/infrastructure/proximity.py" in copied.read_text()
    assert "../../../docs/codebook.md" in copied.read_text()
