"""Read-only path discovery must not create unused folders."""
import json
import pandas as pd
import pytest
from brazil_project.io import Context, WorkflowError


def test_paths_create_directories_only_when_writing(tmp_path):
    config = tmp_path / 'project.toml'
    config.write_text('[project]\nroot = "."\n')
    ctx = Context(config)
    missing = ctx.artifact('unused-stage', 'table.parquet')
    assert not (tmp_path / 'data').exists()
    with pytest.raises(WorkflowError, match='Missing input'):
        ctx.require(missing)
    assert not (tmp_path / 'data').exists()
    written = ctx.write_table(pd.DataFrame({'id': ['001']}), 'real-stage', 'table')
    assert pd.read_parquet(written).id.tolist() == ['001']
    ctx.report('real-stage', {'status': 'completed'})
    assert json.loads(ctx.artifact('real-stage', 'report.json').read_text())['status'] == 'completed'
    assert not missing.parent.exists()
