"""Validate the syntax and cell/output structure of all executable Markdown reports."""
from pathlib import Path
from brazil_project.report_engine import REPORTS, parse_report
root=Path(__file__).resolve().parents[2]
for name in REPORTS:
    cells,_=parse_report((root/'research/reports'/(name+'.md')).read_text())
    print(name, len(cells), 'valid executable cells')
