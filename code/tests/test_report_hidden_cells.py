"""Reader-facing reports execute hidden cells without showing technical controls."""
from html.parser import HTMLParser
import os
from pathlib import Path

import mistune
import pytest

from brazil_project import report_engine as engine
from brazil_project.io import WorkflowError


NAME = "brazil_poroject_charts"
ROOT = Path(__file__).resolve().parents[2]


def hidden_cell(name, code):
    return (f"<!-- brazil:cell {name}\n{code}\n-->\n\n"
            f"<!-- brazil:output {name} begin -->\nprevious result\n"
            f"<!-- brazil:output {name} end -->\n")


def visible_cell(name, code):
    return (f"<!-- brazil:cell {name} -->\n```python\n{code}\n```\n\n"
            f"<!-- brazil:output {name} begin -->\nprevious result\n"
            f"<!-- brazil:output {name} end -->\n")


class ReaderText(HTMLParser):
    """HTML comments carry executable source but are not reader-visible text."""
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def reader_text(source):
    html = mistune.create_markdown(escape=False, plugins=["table"])(source)
    reader = ReaderText()
    reader.feed(html)
    return html, " ".join(reader.parts)


@pytest.fixture
def project(tmp_path):
    config = tmp_path / "custom.toml"
    config.write_text('[project]\nroot="."\nmunicipality=""\n'
                      '[census]\nrecompute_harmonisation=false\n'
                      '[example]\nvalue=42\n')
    ctx = engine.context(config)
    source = tmp_path / "research/reports" / (NAME + ".md")
    source.parent.mkdir(parents=True)
    engine.stamp_producer(ctx, "charts")
    return ctx, source


def test_hidden_cells_keep_stable_ids_and_exact_python():
    code = 'answer = 42\ndisplay(answer)'
    cells, outputs = engine.parse_report(hidden_cell("summary", code))
    assert [cell[1] for cell in cells] == ["summary"]
    assert cells[0][2].rstrip("\n") == code
    assert [output[1] for output in outputs] == ["summary"]


def test_mixed_hidden_and_visible_cells_keep_source_execution_order():
    source = (hidden_cell("first", "value = 40")
              + visible_cell("second", "value += 1")
              + hidden_cell("third", "display(value + 1)"))
    cells, outputs = engine.parse_report(source)
    assert [cell[1] for cell in cells] == ["first", "second", "third"]
    assert [output[1] for output in outputs] == ["first", "second", "third"]
    assert [cell[2].rstrip("\n") for cell in cells] == [
        "value = 40", "value += 1", "display(value + 1)"]


@pytest.mark.parametrize("transform", [
    lambda text: text.replace("\n-->\n", "\n", 1),
    lambda text: text + hidden_cell("summary", "display(2)"),
    lambda text: text.replace("brazil:cell summary", "brazil:cell invalid-id"),
    lambda text: text.replace("brazil:output summary end", "brazil:output missing end"),
    lambda text: text.replace("brazil:output summary begin", "brazil:output other begin"),
    lambda text: text.replace("display(42)", "```python\ndisplay(42)\n```"),
    lambda text: text + "\n<!-- brazil:cell orphan\n",
])
def test_malformed_hidden_cells_fail_before_execution(transform):
    with pytest.raises((WorkflowError, SyntaxError)):
        engine.parse_report(transform(hidden_cell("summary", "display(42)")))


@pytest.mark.parametrize("unsafe_code", [
    'display("--> this prematurely ends an HTML comment")',
    'display("<!-- this nests an HTML comment")',
])
def test_hidden_comment_delimiters_are_rejected(unsafe_code):
    with pytest.raises(WorkflowError):
        engine.parse_report(hidden_cell("summary", unsafe_code))


def test_output_before_its_hidden_cell_is_rejected():
    source = hidden_cell("summary", "display(42)")
    cells, outputs = engine.parse_report(source)
    output = outputs[0].group(0)
    moved = output + "\n" + source[:outputs[0].start()]
    with pytest.raises(WorkflowError):
        engine.parse_report(moved)


def test_hidden_cells_execute_in_a_fresh_worker_preserving_narrative(project):
    ctx, source = project
    source.write_text(
        "# National assessment\n\n## Executive summary\n\n"
        "Locations need review before drawing conclusions.\n\n"
        + hidden_cell("first", 'import os\nvalue = ctx.config["example"]["value"]\ndisplay(os.getpid())')
        + "\nThe second result uses the same report state.\n\n"
        + visible_cell("second", "value += 1\ndisplay(value)")
        + hidden_cell("third", "display(value + 1)")
        + "\nAuthored caption remains unchanged.\n")
    before = source.read_text()
    result = engine.render_report(ctx, NAME)
    after = source.read_text()
    assert result["status"] == "completed"
    assert engine.authored_text(after) == engine.authored_text(before)
    outputs = engine.parse_report(after)[1]
    worker_pid = int(outputs[0][2].strip().splitlines()[1])
    assert worker_pid != os.getpid()
    assert "\n43\n" in outputs[1][2]
    assert "\n44\n" in outputs[2][2]
    engine.render_report(ctx, NAME)
    repeated = source.read_text()
    assert engine.authored_text(repeated) == engine.authored_text(before)
    # PIDs differ across fresh executions; calculated values and narrative do not.
    assert [output[2] for output in engine.parse_report(repeated)[1][1:]] == [
        output[2] for output in outputs[1:]]


def test_hidden_cells_do_not_reuse_previous_worker_state(project):
    ctx, source = project
    source.write_text(hidden_cell("summary", "private_value = 42\ndisplay(private_value)"))
    engine.render_report(ctx, NAME)
    source.write_text(hidden_cell("summary", "display(private_value)"))
    before = source.read_bytes()
    with pytest.raises(WorkflowError, match="not defined"):
        engine.render_report(ctx, NAME)
    assert source.read_bytes() == before


def test_hidden_code_is_invisible_but_results_and_narrative_are_readable():
    source = ("# Assessment\n\n## Executive summary\n\n"
              "The recorded locations need review.\n\n"
              + hidden_cell("summary", 'technical_source_secret = 42\ndisplay(technical_source_secret)'))
    source = source.replace("previous result", "**Finding:** 42 projects need review.")
    html, visible = reader_text(source)
    assert "Executive summary" in visible and "42 projects need review" in visible
    assert "technical_source_secret" not in visible
    assert "brazil:cell" not in visible and "brazil:output" not in visible
    assert "<pre>" not in html and "<details" not in html


def test_maintained_main_starts_with_summary_and_has_no_technical_controls():
    source = (ROOT / "research/reports/gov_data_quality.md").read_text()
    cells, outputs = engine.parse_report(source)
    assert [cell[1] for cell in cells] == ["gov_data_quality_summary"]
    assert len(outputs) == 1
    assert cells[0].group(0).startswith("<!-- brazil:cell gov_data_quality_summary\n")
    html, visible = reader_text(source)
    assert "Executive summary" in visible
    assert visible.index("Executive summary") < visible.index("Finding")
    assert "gov_data_quality_annex.md" in html
    for technical_control in ("How to read this analysis", "Reproduce and inspect", "Processing code and pipeline",
                              "brazil-project", "report_json(", "shared_coordinate_threshold", "gov_quality.py"):
        assert technical_control not in visible
    assert "<details" not in html and "```python" not in visible
