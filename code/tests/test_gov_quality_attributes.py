"""Attribute QA preserves raw records and makes project-level denominators explicit."""
import numpy as np
import pandas as pd
import pytest

from brazil_project.io import WorkflowError
from brazil_project.infrastructure.gov_quality_attributes import audit_attributes, write_attribute_figures


def projects():
    return pd.DataFrame({
        "id_projeto_investimento": ["001.A", "001.A", "B", "C", "D", "E", None],
        "uf_principal": ["MG", "MG", "SP", "RJ", "BA", "AM", "MG"],
        "situacao": ["Concluída", "Concluída", "Concluída", "Em execução", "Cadastrada", "Cadastrada", "Concluída"],
        "dt_cadastro": ["2025-01-01"] * 7,
        "dt_inicial_prevista": ["2011-01-01"] * 7,
        "dt_final_prevista": ["2012-01-01"] * 7,
        "dt_inicial_efetiva": [None, None, "2022-02-01", "bad", "1899-12-30", "2202-01-01", None],
        "dt_final_efetiva": [None, None, "2022-01-01", None, None, "2202-06-01", None],
        "vl_investimento_previsto_total": [.01, .01, 100, 200, 0, -1, 50],
        "tipo": ["Infraestrutura Hídrica, Portos, Hidrovia", "Educação", "Saúde", "Saúde", "Educação", "Educação", "Educação"],
        "id_tipo": [22, 20, 10, 10, 20, 20, 20],
        "desc_nome": ["Escola em outra cidade", "Creche", "Hospital", "Posto", "Escola", "Creche", "Escola"],
        "organizacao_resp": ["FUNDO NACIONAL DE DESENVOLVIMENTO DA EDUCAÇÃO"] * 7,
    })


def test_preserves_original_rows_ids_dates_and_values_and_unique_denominators():
    source = projects()
    source.index = [0, 0, 1, 2, 3, 4, 5]
    before = source.copy(deep=True)
    result = audit_attributes(source, "2026-10-07")
    pd.testing.assert_frame_equal(source, before)
    meta = result["metadata"]
    assert meta["source_rows"] == 7 and meta["distinct_projects"] == 5
    assert meta["rows_missing_id"] == 1 and meta["source_values_corrected"] == 0
    assert meta["projects_with_budget_001"] == 1 and meta["projects_with_budget_001_pct"] == 20
    assert result["tables"]["duplicate_projects"].iloc[0]["Project ID"] == "001.A"
    assert result["tables"]["duplicate_projects"].iloc[0]["Source rows"] == 2


def test_actual_planned_registration_and_sentinel_flags_are_distinct():
    tables = audit_attributes(projects(), "2026-10-07")["tables"]
    summary = tables["dates_summary"].set_index("Date field")
    assert summary.loc["Actual start", "Source rows invalid"] == 1
    assert summary.loc["Actual start", "Source rows year outside 1900–2099"] == 2
    assert summary.loc["Actual start", "Source rows future"] == 1
    ids = tables["dates_anomalies"].set_index("Project ID")
    assert bool(ids.loc["B", "Actual finish precedes actual start"])
    assert bool(ids.loc["001.A", "Completed status without actual finish"])
    assert bool(ids.loc["E", "Actual start: future"])
    assert ids["Registration follows planned start"].all()


def test_conflicting_budgets_are_not_collapsed_and_missing_is_not_zero():
    source = projects()
    source.loc[1, "vl_investimento_previsto_total"] = 25
    source.loc[3, "vl_investimento_previsto_total"] = None
    tables = audit_attributes(source, "2026-10-07")["tables"]
    budget = tables["budget_anomalies"].set_index("Project ID")
    assert bool(budget.loc["001.A", "Conflicting nonmissing budgets"])
    assert pd.isna(budget.loc["001.A", "Agreed budget (BRL)"])
    assert bool(budget.loc["C", "Missing budget"])
    assert pd.isna(budget.loc["C", "Agreed budget (BRL)"])
    assert bool(budget.loc["D", "Zero budget"])
    assert bool(budget.loc["E", "Negative budget"])
    assert tables["field_conflicts"].Field.eq("vl_investimento_previsto_total").any()


def test_taxonomy_expansion_is_not_certified_error_but_code_label_conflicts_are_visible():
    source = projects()
    source.loc[3, "tipo"] = "Other supplied label"
    result = audit_attributes(source, "2026-10-07")
    conflicts = result["tables"]["classification_conflicts"]
    assert len(conflicts) == 1 and conflicts.iloc[0]["Code"] == "10"
    category = result["tables"]["category_consistency"]
    assert category.iloc[0]["Distinct project IDs"] == 1
    assert "not certified" in category.iloc[0]["Interpretation"]
    row = result["tables"]["field_conflicts"].query("Field == 'tipo' and `Project ID` == '001.A'").iloc[0]
    assert "legitimate taxonomy" in row.Interpretation


def test_ambiguous_dates_nonfinite_budgets_and_conflicting_states_remain_reviewable():
    source = projects()
    source.loc[1, "uf_principal"] = "SP"
    source.loc[2, "dt_inicial_efetiva"] = "01/02/2022"
    source.loc[3, "vl_investimento_previsto_total"] = np.inf
    tables = audit_attributes(source, "2026-10-07")["tables"]
    assert tables["dates_summary"].set_index("Date field").loc["Actual start", "Source rows invalid"] == 2
    budget = tables["budget_anomalies"].set_index("Project ID")
    assert bool(budget.loc["C", "Invalid or nonfinite budget"])
    assert pd.isna(budget.loc["C", "Agreed budget (BRL)"])
    assert budget.loc["001.A", "Reported state(s)"] == "MG | SP"


def test_translated_millisecond_dates_2202_remain_parsed_not_missing():
    source = projects()
    for field in ["dt_cadastro", "dt_inicial_prevista", "dt_final_prevista", "dt_inicial_efetiva", "dt_final_efetiva"]:
        source[field] = pd.to_datetime(source[field], errors="coerce", format="ISO8601").astype("datetime64[ms]")
    result = audit_attributes(source, "2026-10-07")
    row = result["tables"]["dates_summary"].set_index("Date field").loc["Actual start"]
    assert row["Source rows future"] == 1 and row["Source rows invalid"] == 0
    assert result["metadata"]["projects_with_effective_start"] == 3


def test_as_of_date_includes_times_within_that_whole_calendar_day():
    source = projects()
    source.loc[2, "dt_final_efetiva"] = "2026-10-07T20:10:00"
    source.loc[5, "dt_final_efetiva"] = "2026-10-08T00:00:00"
    dates = audit_attributes(source, "2026-10-07")["tables"]["dates_anomalies"].set_index("Project ID")
    assert not bool(dates.loc["B", "Actual finish: future"])
    assert bool(dates.loc["E", "Actual finish: future"])


def test_missing_columns_empty_denominators_and_figures_are_explicit(tmp_path):
    source = pd.DataFrame({"project_id": pd.Series(dtype="string")})
    result = audit_attributes(source, "2026-10-07")
    assert result["metadata"]["distinct_projects"] == 0
    assert "dt_inicial_efetiva" in result["metadata"]["absent_fields"]
    assert result["tables"]["dates_summary"]["Project coverage (%)"].isna().all()
    paths = write_attribute_figures(result["tables"], result["metadata"], tmp_path)
    assert len(paths) == 4
    for file in tmp_path.glob("*.png"):
        assert file.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_requires_identity_and_explicit_valid_date():
    with pytest.raises(WorkflowError, match="identifier"):
        audit_attributes(pd.DataFrame({"budget": [1]}), "2026-10-07")
    with pytest.raises(WorkflowError, match="as_of_date"):
        audit_attributes(projects(), "not a date")
