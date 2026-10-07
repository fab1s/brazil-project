"""Read-only Obrasgov attribute diagnostics; review flags never alter source rows.

All project percentages use nonmissing distinct original project identifiers.
Repeated taxonomy rows remain visible; a conflicting value is never selected by
row order. Date coverage distinguishes reported/planned dates from actual dates.
"""
from pathlib import Path
import unicodedata

import numpy as np
import pandas as pd

from brazil_project.io import WorkflowError


DATE_FIELDS = {
    "dt_cadastro": "Registration",
    "dt_inicial_prevista": "Planned start",
    "dt_final_prevista": "Planned finish",
    "dt_inicial_efetiva": "Actual start",
    "dt_final_efetiva": "Actual finish",
}
BUDGET = "vl_investimento_previsto_total"
FIELD_LABELS = {
    "id_projeto_investimento": "Project identifier", "project_id": "Project identifier",
    "desc_nome": "Project name", "desc_endereco": "Street address", "nr_cep": "Postal code",
    "desc_projeto": "Project description", "desc_funcao_social": "Social-purpose description",
    "desc_meta_global": "Project goal", "dt_cadastro": "Registration date",
    "dt_inicial_prevista": "Planned start date", "dt_final_prevista": "Planned finish date",
    "dt_inicial_efetiva": "Actual start date", "dt_final_efetiva": "Actual finish date",
    "uf_principal": "Primary state", "situacao": "Reported project status",
    "organizacao_resp": "Responsible organisation", "cnpj_organizacao_resp": "Organisation identifier",
    "populacao_beneficiada": "Reported beneficiary count", "desc_populacao_beneficiada": "Beneficiary description",
    "qtd_empregos_gerados": "Reported jobs generated", "obs_pertinentes_intervencao": "Additional project notes",
    "projeto_estruturante": "Strategic-project designation", "ind_bim": "BIM designation",
    "tipo": "Supplied category", "id_tipo": "Category code", "subtipo": "Supplied subcategory",
    "id_subtipo": "Subcategory code", "eixo": "Supplied axis", "id_eixo": "Axis code",
    "type_en": "Translated category", "subtype_en": "Translated subcategory",
    BUDGET: "Total planned investment",
}


def _missing(values):
    return values.isna() | values.astype("string").str.fullmatch(r"\s*", na=False)


def _fold(values):
    def fold(value):
        return "".join(c for c in unicodedata.normalize("NFKD", str(value))
                       if not unicodedata.combining(c)).lower()
    return values.fillna("").map(fold)


def _percent(count, denominator):
    return 100.0 * count / denominator if denominator else np.nan


def _states(frame, ids):
    values = frame.get("uf_principal", pd.Series(pd.NA, index=frame.index)).astype("string")
    values = values.mask(_missing(values))
    # CONTRACT: Conflicting states stay explicit; selecting the first would
    # conceal disagreement and assign a project to an arbitrary geography.
    groups = pd.DataFrame({"id": ids, "state": values}).dropna(subset=["id"]).groupby("id", sort=False)
    return groups.state.agg(lambda x: " | ".join(sorted(set(x.dropna()))) or "Missing state")


def _parse_date(values):
    supplied = ~_missing(values)
    # WHY: Already translated timestamps and ISO dates have explicit formats.
    # Ambiguous text such as 01/02/2020 is flagged, never guessed day/month-first.
    if pd.api.types.is_datetime64_any_dtype(values.dtype):
        parsed = pd.to_datetime(values, errors="coerce")
    else:
        parsed = pd.to_datetime(values.where(supplied), errors="coerce", format="ISO8601")
    if isinstance(parsed.dtype, pd.DatetimeTZDtype):
        parsed = parsed.dt.tz_convert("UTC").dt.tz_localize(None)
    return parsed, supplied & parsed.isna()


def audit_attributes(frame, as_of_date):
    """Return ``tables`` and JSON-safe ``metadata`` without modifying ``frame``.

    The date is explicit to make future-date review reproducible. The review
    bounds 1900–2099 and R$0.01 flags are transparent screening conventions,
    not verified errors or instructions to filter observations.
    """
    if not isinstance(frame, pd.DataFrame):
        raise WorkflowError("Obrasgov attribute audit requires a pandas/GeoPandas table.")
    id_field = "id_projeto_investimento" if "id_projeto_investimento" in frame else "project_id"
    if id_field not in frame:
        raise WorkflowError("Missing original Obrasgov project identifier column.")
    try:
        as_of = pd.Timestamp(as_of_date).normalize()
        if pd.isna(as_of):
            raise ValueError("missing date")
        if as_of.tzinfo:
            as_of = as_of.tz_localize(None)
    except (ValueError, TypeError) as error:
        raise WorkflowError("Supply an explicit valid as_of_date (YYYY-MM-DD).") from error
    # A fresh positional index protects duplicate source indices without
    # rewriting identifiers or any values in the caller's immutable table.
    source = pd.DataFrame(frame.drop(columns="geometry", errors="ignore")).reset_index(drop=True)
    ids = source[id_field].astype("string").mask(_missing(source[id_field]))
    identified = ids.notna()
    project_ids = pd.Index(ids[identified].unique(), name="Project ID")
    total = len(source)
    unique = len(project_ids)
    project_states = _states(source, ids).reindex(project_ids)
    row_counts = ids[identified].value_counts(sort=False).reindex(project_ids)
    tables = {}

    def flags_by_id(flags):
        return pd.DataFrame(flags).assign(_id=ids).dropna(subset=["_id"]).groupby("_id", sort=False).any().reindex(project_ids, fill_value=False)

    def count_ids(mask):
        return int(ids[mask & identified].nunique())

    identity = [
        ("Preserved source rows", total),
        ("Distinct nonmissing project IDs", unique),
        ("Rows without a project ID", int((~identified).sum())),
        ("Repeated-ID rows beyond one per ID", int(identified.sum() - unique)),
        ("Project IDs occurring in multiple rows", int(row_counts.gt(1).sum())),
        ("Repeated identical attribute rows (geometry excluded)", int(source.duplicated().sum())),
    ]
    tables["identity_summary"] = pd.DataFrame(identity, columns=["Measure", "Count"])

    missing_rows = []
    conflicts = []
    # Attribute disagreement is recorded field by field. Multiple type/subtype
    # entries can be legitimate taxonomy expansion, not erroneous duplicates.
    for field in source:
        missing = _missing(source[field])
        by_id = pd.DataFrame({"id": ids, "missing": missing, "value": source[field].mask(missing)}).dropna(subset=["id"]).groupby("id", sort=False)
        any_missing, all_missing = by_id.missing.any(), by_id.missing.all()
        missing_rows.append({"Field": field, "Meaning": FIELD_LABELS.get(field, field.replace("_", " ")),
                             "Source rows missing": int(missing.sum()),
                             "Source rows missing (%)": _percent(int(missing.sum()), total),
                             "Project IDs with any missing row": int(any_missing.sum()),
                             "Project IDs entirely missing": int(all_missing.sum()),
                             "Project IDs entirely missing (%)": _percent(int(all_missing.sum()), unique)})
        variants = by_id.value.nunique(dropna=True)
        for pid, n in variants[variants.gt(1)].items():
            values = by_id.get_group(pid).value.dropna().astype(str).unique()
            conflicts.append({"Project ID": str(pid), "Field": field, "Distinct nonmissing values": int(n),
                              "Values": " | ".join(sorted(values)),
                              "Interpretation": "May be legitimate taxonomy expansion; review" if field in {"tipo", "id_tipo", "subtipo", "id_subtipo", "eixo", "id_eixo", "type_en", "subtype_en"} else "Attribute disagreement; no value selected"})
    tables["missingness"] = pd.DataFrame(missing_rows)
    tables["field_conflicts"] = pd.DataFrame(conflicts, columns=["Project ID", "Field", "Distinct nonmissing values", "Values", "Interpretation"])
    conflict_summary = tables["field_conflicts"].groupby("Field")["Project ID"].nunique().rename("Project IDs with conflicting values").reset_index()
    conflict_summary["Project IDs (%)"] = conflict_summary["Project IDs with conflicting values"].map(lambda n: _percent(int(n), unique))
    tables["field_conflict_summary"] = conflict_summary
    duplicate = pd.DataFrame({"Project ID": project_ids.astype(str), "Source rows": row_counts.to_numpy(),
                              "Reported state(s)": project_states.to_numpy()})
    disagreements = tables["field_conflicts"].groupby("Project ID").size() if conflicts else pd.Series(dtype="int64")
    duplicate["Fields with conflicting nonmissing values"] = duplicate["Project ID"].map(disagreements).fillna(0).astype(int)
    tables["duplicate_projects"] = duplicate[duplicate["Source rows"].gt(1)].sort_values(["Source rows", "Project ID"], ascending=[False, True]).reset_index(drop=True)

    date_flags = {}
    dates = {}
    date_summary = []
    absent = []
    for field, label in DATE_FIELDS.items():
        if field not in source:
            absent.append(field)
        raw = source.get(field, pd.Series(pd.NA, index=source.index))
        parsed, invalid = _parse_date(raw)
        dates[field] = parsed
        missing = _missing(raw)
        future = parsed.dt.normalize().gt(as_of)
        unusual = parsed.notna() & (parsed.dt.year.lt(1900) | parsed.dt.year.ge(2100))
        date_flags.update({label + ": missing": missing, label + ": invalid parse": invalid,
                           label + ": future": future, label + ": year outside 1900–2099": unusual})
        date_summary.append({"Date field": label, "Source field": field, "Field supplied": field in source,
                             "Source rows with parsed date": int(parsed.notna().sum()),
                             "Project IDs with any parsed date": count_ids(parsed.notna()),
                             "Project coverage (%)": _percent(count_ids(parsed.notna()), unique),
                             "Source rows missing": int(missing.sum()), "Source rows invalid": int(invalid.sum()),
                             "Source rows future": int(future.sum()), "Source rows year outside 1900–2099": int(unusual.sum()),
                             "Interpretation": "Registration is not commencement or commissioning" if field == "dt_cadastro" else "Future planned dates may be legitimate" if "prevista" in field else "An actual date is reported, not independently verified"})
    start, finish = dates["dt_inicial_efetiva"], dates["dt_final_efetiva"]
    planned_start, planned_finish = dates["dt_inicial_prevista"], dates["dt_final_prevista"]
    date_flags["Actual finish precedes actual start"] = start.notna() & finish.notna() & finish.lt(start)
    date_flags["Planned finish precedes planned start"] = planned_start.notna() & planned_finish.notna() & planned_finish.lt(planned_start)
    date_flags["Registration follows planned start"] = dates["dt_cadastro"].notna() & planned_start.notna() & dates["dt_cadastro"].gt(planned_start)
    completed = _fold(source.get("situacao", pd.Series("", index=source.index))).isin(["concluida", "concluido", "completed"])
    date_flags["Completed status without actual finish"] = completed & finish.isna()
    date_flags["Completed status with future actual finish"] = completed & finish.dt.normalize().gt(as_of)
    tables["dates_summary"] = pd.DataFrame(date_summary)
    date_project = flags_by_id(date_flags)
    date_project.insert(0, "Reported state(s)", project_states)
    tables["dates_anomalies"] = date_project.reset_index()
    state_dates = date_project.groupby("Reported state(s)", dropna=False)[list(date_flags)].sum().astype(int)
    state_dates.insert(0, "Distinct project IDs", date_project.groupby("Reported state(s)", dropna=False).size())
    tables["dates_anomalies_by_state"] = state_dates.reset_index()

    if BUDGET not in source:
        absent.append(BUDGET)
    raw_budget = source.get(BUDGET, pd.Series(pd.NA, index=source.index))
    budget = pd.to_numeric(raw_budget, errors="coerce")
    nonfinite = budget.notna() & ~np.isfinite(budget)
    invalid_budget = (~_missing(raw_budget) & budget.isna()) | nonfinite
    known_budget = budget.notna() & ~nonfinite
    budget_flags = {"Missing budget": _missing(raw_budget), "Invalid or nonfinite budget": invalid_budget,
                    "Zero budget": known_budget & budget.eq(0), "Negative budget": known_budget & budget.lt(0),
                    "R$0.01 review value": known_budget & budget.eq(.01),
                    "Positive budget at most R$1": known_budget & budget.gt(0) & budget.le(1)}
    budget_project = flags_by_id(budget_flags)
    valid = pd.DataFrame({"id": ids, "budget": budget.where(known_budget)}).dropna(subset=["id"]).groupby("id", sort=False).budget
    n_budget = valid.nunique(dropna=True).reindex(project_ids, fill_value=0)
    # INVARIANT: A min is used only after proving one unique numeric value;
    # projects with conflicting budgets remain unavailable in ID-level totals.
    agreed = valid.min().reindex(project_ids).where(n_budget.eq(1) & ~budget_project["Invalid or nonfinite budget"])
    budget_project["Conflicting nonmissing budgets"] = n_budget.gt(1)
    budget_project["Distinct numeric budget values"] = n_budget
    budget_project["Agreed budget (BRL)"] = agreed
    budget_project.insert(0, "Reported state(s)", project_states)
    tables["budget_anomalies"] = budget_project.reset_index()
    budget_summary = []
    for label, mask in budget_flags.items():
        n = int(budget_project[label].sum())
        budget_summary.append({"Measure": label, "Source rows": int(mask.sum()), "Distinct project IDs": n,
                               "Project IDs (%)": _percent(n, unique), "Value (BRL)": np.nan})
    budget_summary.extend([
        {"Measure": "Project IDs with conflicting nonmissing budgets", "Source rows": np.nan, "Distinct project IDs": int(n_budget.gt(1).sum()), "Project IDs (%)": _percent(int(n_budget.gt(1).sum()), unique), "Value (BRL)": np.nan},
        {"Measure": "Sum across source rows: repeats included", "Source rows": int(known_budget.sum()), "Distinct project IDs": count_ids(known_budget), "Project IDs (%)": np.nan, "Value (BRL)": float(budget.where(known_budget).sum())},
        {"Measure": "Sum of one agreed budget per ID: conflicting/invalid IDs omitted", "Source rows": np.nan, "Distinct project IDs": int(agreed.notna().sum()), "Project IDs (%)": _percent(int(agreed.notna().sum()), unique), "Value (BRL)": float(agreed.sum())},
    ])
    tables["budget_summary"] = pd.DataFrame(budget_summary)
    budget_state = budget_project.groupby("Reported state(s)", dropna=False)[[*budget_flags, "Conflicting nonmissing budgets"]].sum().astype(int)
    budget_state.insert(0, "Distinct project IDs", budget_project.groupby("Reported state(s)", dropna=False).size())
    budget_state["Agreed-ID budget sum (BRL)"] = budget_project.groupby("Reported state(s)", dropna=False)["Agreed budget (BRL)"].sum(min_count=1)
    tables["budget_by_state"] = budget_state.reset_index()

    classification = []
    for code, label in [("id_tipo", "tipo"), ("id_subtipo", "subtipo"), ("id_eixo", "eixo")]:
        if code not in source or label not in source:
            absent.extend(name for name in [code, label] if name not in source)
            continue
        pairs = source[[code, label]].copy()
        pairs = pairs[~_missing(pairs[code]) & ~_missing(pairs[label])]
        for key, labels in pairs.groupby(code, sort=False)[label]:
            variants = sorted(set(labels.astype(str)))
            if len(variants) > 1:
                mask = source[code].eq(key)
                classification.append({"Code field": code, "Code": str(key), "Label field": label,
                                       "Distinct labels": len(variants), "Labels": " | ".join(variants),
                                       "Source rows": int(mask.sum()), "Distinct project IDs": count_ids(mask),
                                       "Interpretation": "Same supplied code maps to multiple labels; review"})
    tables["classification_conflicts"] = pd.DataFrame(classification, columns=["Code field", "Code", "Label field", "Distinct labels", "Labels", "Source rows", "Distinct project IDs", "Interpretation"])
    category = source.get("tipo", pd.Series(pd.NA, index=source.index)).astype("string").mask(lambda s: _missing(s), "Missing category")
    frequency = pd.DataFrame({"Category": category, "id": ids}).groupby("Category", dropna=False).agg(**{"Source rows": ("id", "size"), "Distinct project IDs": ("id", "nunique")}).reset_index()
    tables["category_frequency"] = frequency.sort_values("Source rows", ascending=False).reset_index(drop=True)
    text = pd.Series("", index=source.index)
    for field in ["desc_nome", "desc_projeto", "organizacao_resp"]:
        text = text + " " + _fold(source.get(field, pd.Series("", index=source.index)))
    education = text.str.contains(r"\bescol|\bcreche|educa|\bfnde|\bpre.escola", regex=True)
    water = _fold(category).str.contains("hidrica|portos|hidrovia", regex=True)
    review = education & water
    consistency = []
    for cat in category[review].unique():
        mask = review & category.eq(cat)
        consistency.append({"Review signal": "Education description/provider with water/ports category",
                            "Supplied category": str(cat), "Source rows": int(mask.sum()),
                            "Distinct project IDs": count_ids(mask),
                            "Category project IDs": count_ids(category.eq(cat)),
                            "Category projects flagged (%)": _percent(count_ids(mask), count_ids(category.eq(cat))),
                            "Interpretation": "Keyword screening only; supplied categories retained, not certified misclassification"})
    tables["category_consistency"] = pd.DataFrame(consistency, columns=["Review signal", "Supplied category", "Source rows", "Distinct project IDs", "Category project IDs", "Category projects flagged (%)", "Interpretation"])

    metadata = {"source_rows": total, "distinct_projects": unique, "rows_missing_id": int((~identified).sum()),
                "project_id_field": id_field, "as_of_date": as_of.date().isoformat(),
                "project_denominator": "Distinct nonmissing original IDs; row-level counts and project flags are separate",
                "absent_fields": sorted(set(absent)), "date_review_year_bounds": [1900, 2099],
                "date_parser": "Translated datetimes or explicit ISO8601; ambiguous date strings flagged invalid",
                "budget_review_value_brl": .01,
                "budget_zero_or_low_value_not_excluded": True,
                "registration_not_commencement": True,
                "source_rows_changed": 0, "source_values_corrected": 0,
                "projects_with_any_attribute_conflict": int(tables["field_conflicts"]["Project ID"].nunique()),
                "project_attribute_conflicts_by_field": {str(row["Field"]): int(row["Project IDs with conflicting values"]) for _, row in conflict_summary.iterrows()},
                "projects_with_effective_start": count_ids(start.notna()),
                "projects_with_effective_finish": count_ids(finish.notna()),
                "projects_with_effective_start_pct": _percent(count_ids(start.notna()), unique) if unique else None,
                "projects_with_effective_finish_pct": _percent(count_ids(finish.notna()), unique) if unique else None,
                "projects_with_completed_status": count_ids(completed),
                "projects_completed_without_effective_finish": count_ids(date_flags["Completed status without actual finish"]),
                "projects_with_budget_001": int(budget_project["R$0.01 review value"].sum()),
                "projects_with_budget_001_pct": _percent(int(budget_project["R$0.01 review value"].sum()), unique) if unique else None,
                "projects_with_category_review": count_ids(review),
                "projects_with_category_review_pct": _percent(count_ids(review), unique) if unique else None,
                "limitations": ["Taxonomy expansion can repeat project rows without being erroneous.",
                                "Keyword/category disagreements require provider evidence; no category reclassification.",
                                "Actual dates are supplied observations, not independently verified openings.",
                                "Agreed-ID budgets are conditional on nonconflicting observed values; missing and conflicting values remain visible.",
                                "Geometry, geocoding and census coverage are audited separately."],
                "tables": list(tables)}
    return {"tables": tables, "metadata": metadata}


def write_attribute_figures(tables, metadata, outdir):
    """Write four reviewed-style descriptive PNGs; no inference or data filtering."""
    import matplotlib
    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    figures = {}

    def save(fig, name, caption):
        fig.text(.02, .01, caption, fontsize=9, va="bottom", wrap=True)
        fig.tight_layout(rect=(0, .065, 1, 1))
        target = outdir / name
        fig.savefig(target, dpi=150, facecolor="white")
        plt.close(fig)
        figures[name] = str(target)

    missing = tables["missingness"]
    missing = missing[missing["Project IDs entirely missing (%)"].gt(0)].sort_values("Project IDs entirely missing (%)", ascending=True).tail(18)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(missing["Meaning"], missing["Project IDs entirely missing (%)"], color="#647f8c")
    if not len(missing):
        ax.text(.5, .5, "No entirely-missing fields among observed project IDs\n(or no project IDs; see population counts)", ha="center", transform=ax.transAxes)
    ax.set(xlim=(0, 100), xlabel="Distinct project IDs entirely missing this field (%)", title="Obrasgov attribute coverage: most incomplete fields")
    save(fig, "attribute-missingness.png", "Denominator: nonmissing distinct project IDs. Up to 18 fields shown; partial missingness and absent fields remain in audit tables.")

    dates = tables["dates_summary"]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(dates["Date field"], dates["Project coverage (%)"], color=["#8b969b", "#8b969b", "#8b969b", "#278b80", "#278b80"])
    ax.set(xlim=(0, 100), xlabel="Distinct project IDs with any parsed date (%)", title="Registration and planned dates do not establish operation")
    for j, value in enumerate(dates["Project coverage (%)"]):
        if np.isfinite(value):
            ax.text(min(value + 1, 93), j, f"{value:.2f}%", va="center", fontsize=10)
    save(fig, "date-coverage.png", f"Reported date coverage; future/sentinel-like values are not removed. Actual dates are not independently verified. Review as of {metadata['as_of_date']}.")

    budgets = tables["budget_anomalies"]
    agreed = budgets["Agreed budget (BRL)"]
    usable = agreed[agreed.gt(.01) & np.isfinite(agreed)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1.5, 1]})
    if len(usable):
        axes[0].hist(np.log10(usable), bins=35, color="#278b80")
    else:
        axes[0].text(.5, .5, "No agreed budgets greater than R$0.01", ha="center", transform=axes[0].transAxes)
    axes[0].set(xlabel="log₁₀ agreed planned budget (BRL)", ylabel="Distinct project IDs", title="Agreed positive budgets greater than R$0.01")
    names = ["Missing budget", "Invalid or nonfinite budget", "Zero budget", "Negative budget", "R$0.01 review value", "Conflicting nonmissing budgets"]
    axes[1].barh([n.replace(" or nonfinite", "") for n in names], [int(budgets[n].sum()) for n in names], color="#b26850")
    axes[1].set(xlabel="Distinct project IDs", title="Review flags (can overlap)")
    save(fig, "budget-distribution.png", "One value per ID only when nonconflicting; R$0.01 is a review flag, not a verified placeholder. Flags and all raw values remain preserved.")

    categories = tables["category_frequency"].head(12)
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw={"width_ratios": [1.5, 1]})
    axes[0].barh(categories["Category"].astype(str).map(lambda x: x[:48]), categories["Distinct project IDs"], color="#647f8c")
    axes[0].invert_yaxis()
    axes[0].set(xlabel="Distinct project IDs within supplied category", title="Supplied project categories (up to 12)")
    n_review = metadata["projects_with_category_review"]
    axes[1].bar(["Education signal +\nwater/ports category", "All distinct\nproject IDs"], [n_review, metadata["distinct_projects"]], color=["#b26850", "#647f8c"])
    axes[1].set(ylabel="Distinct project IDs", title="Category wording requires review")
    save(fig, "category-consistency.png", "Categories can overlap through taxonomy expansion. Education signal uses names/descriptions/provider; screening does not certify or correct classification.")
    return figures
