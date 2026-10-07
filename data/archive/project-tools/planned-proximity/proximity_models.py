"""Income/racial-composition associations with registered-project proximity.

The observational unit is a complete harmonised census comparison area. The
outcome is log1p(network kilometres), not service access or individual exposure.
Comparisons require empirical income/racial-composition support *within* each
municipality. Three specifications share one analysis sample. Spatial-block
cluster covariance allows dependence within blocks, but is not a correction
for omitted spatial confounders, residential segregation or causal selection.
"""
from pathlib import Path
import math

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import t as student_t

from brazil_project.io import WorkflowError


REQUIRED = ["common_id", "municipality", "income", "black_share", "brown_share",
            "race_share", "population", "density", "x_m", "y_m",
            "nearest_network_km", "origin_status"]
PREDICTION_COLUMNS = ["model", "municipality", "support_bin", "income", "scenario",
                      "race_share", "prediction_km", "lower_km", "upper_km", "n_areas"]
CONTRAST_COLUMNS = ["model", "scope", "municipality", "support_bin", "income",
                    "low_race_share", "high_race_share", "difference_km",
                    "lower_km", "upper_km", "n_areas"]
COEFFICIENT_COLUMNS = ["model", "term", "coefficient", "standard_error", "lower",
                       "upper", "p_value", "scale"]
COVERAGE_COLUMNS = ["model", "status", "reason", "n_areas", "n_parameters",
                    "n_spatial_blocks", "rank", "r_squared", "income_basis"]


def _number(cfg, key, default, minimum=None, maximum=None, integer=False):
    value = cfg.get(key, default)
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise WorkflowError(f"proximity {key} must be numeric")
    if not np.isfinite(number) or (minimum is not None and number < minimum) or (
            maximum is not None and number > maximum):
        raise WorkflowError(f"proximity {key} is outside the allowed range")
    if integer and number != int(number):
        raise WorkflowError(f"proximity {key} must be an integer")
    return int(number) if integer else number


def _settings(cfg):
    """Validate numerical choices rather than silently falling back to defaults."""
    settings = {
        "min_model_n": _number(cfg, "min_model_n", 60, 12, integer=True),
        "min_spatial_blocks": _number(cfg, "min_spatial_blocks", 8, 3, integer=True),
        "spatial_block_size_m": _number(cfg, "spatial_block_size_m", 5000, 1),
        "support_min_group": _number(cfg, "support_min_group", 10, 2, integer=True),
        "support_min_cell": _number(cfg, "support_min_cell", 3, 1, integer=True),
        "support_bins": _number(cfg, "support_bins", 5, 2, 20, integer=True),
        "support_tail_fraction": _number(cfg, "support_tail_fraction", .05, 0, .25),
        "race_low_quantile": _number(cfg, "race_low_quantile", .25, .01, .49),
        "race_high_quantile": _number(cfg, "race_high_quantile", .75, .51, .99),
    }
    return settings


def _quantile_bins(values, count=5):
    # WHY: tied observed values remain together; arbitrary ID-based splitting can
    # suggest joint support where no genuinely different values were observed.
    if len(values) == 0 or values.nunique() < 2:
        return pd.Series(1, index=values.index, dtype=int)
    bins = pd.qcut(values, count, labels=False, duplicates="drop")
    return bins.fillna(0).astype(int) + 1


def _valid_sample(frame):
    missing = [column for column in REQUIRED if column not in frame]
    if missing:
        raise WorkflowError("Proximity model inputs missing columns: " + ", ".join(missing))
    data = frame.copy().reset_index(drop=True)
    if data.common_id.isna().any() or data.common_id.astype(str).duplicated().any():
        raise WorkflowError("Proximity models require one nonmissing row per common_id")
    if data.municipality.isna().any():
        raise WorkflowError("Proximity models require explicit municipality identifiers")
    data["common_id"] = data.common_id.astype(str)
    data["municipality"] = data.municipality.astype(str)
    numeric = [column for column in REQUIRED if column not in
               ("common_id", "municipality", "origin_status")]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    audit = data[["common_id", "municipality", "origin_status"]].copy()
    audit["valid_route"] = data.origin_status.eq("routed") & np.isfinite(
        data.nearest_network_km) & data.nearest_network_km.ge(0)
    audit["valid_income"] = np.isfinite(data.income) & data.income.ge(0)
    audit["valid_race"] = np.isfinite(data[["race_share", "black_share", "brown_share"]]).all(
        axis=1) & data[["race_share", "black_share", "brown_share"]].ge(0).all(axis=1) & (
        data[["race_share", "black_share", "brown_share"]].le(1).all(axis=1))
    # CONTRACT: the combined share is the sum of the two original categories.
    audit["valid_race"] &= np.isclose(data.race_share, data.black_share + data.brown_share,
                                       atol=1e-8, rtol=1e-8)
    audit["valid_density"] = np.isfinite(data.density) & data.density.ge(0)
    audit["valid_spatial_coordinates"] = np.isfinite(data[["x_m", "y_m"]]).all(axis=1)
    audit["eligible_before_support"] = audit[["valid_route", "valid_income", "valid_race",
                                              "valid_density", "valid_spatial_coordinates"]].all(axis=1)
    return data, audit


def _support(data, cfg):
    """Audit marginal overlap and local joint support before any predictions."""
    municipality_rows, cell_rows, counts = [], [], []
    selected = data.copy()
    selected["support_bin"] = 0
    selected["supported"] = False
    for municipality, group in data.groupby("municipality", sort=True):
        group = group.copy()
        group["income_quintile"] = _quantile_bins(group.income)
        group["race_quintile"] = _quantile_bins(group.race_share)
        for (income_q, race_q), joint in group.groupby(["income_quintile", "race_quintile"]):
            counts.append({"municipality": municipality, "income_quintile": int(income_q),
                           "race_quintile": int(race_q), "n_areas": len(joint),
                           "income_min_brl": float(joint.income.min()),
                           "income_max_brl": float(joint.income.max()),
                           "race_share_min": float(joint.race_share.min()),
                           "race_share_max": float(joint.race_share.max())})
        low_cut = float(group.race_share.quantile(cfg["race_low_quantile"]))
        high_cut = float(group.race_share.quantile(cfg["race_high_quantile"]))
        low, high = group[group.race_share <= low_cut], group[group.race_share >= high_cut]
        row = {"municipality": municipality, "n_eligible": len(group), "low_race_cut": low_cut,
               "high_race_cut": high_cut, "n_low": len(low), "n_high": len(high),
               "income_lower_brl": np.nan, "income_upper_brl": np.nan,
               "n_supported": 0, "supported": False, "reason": ""}
        if low_cut >= high_cut:
            row["reason"] = "No distinct low/high racial-composition groups"
        elif min(len(low), len(high)) < cfg["support_min_group"]:
            row["reason"] = "Too few areas in low/high racial-composition groups"
        else:
            tail = cfg["support_tail_fraction"]
            lower = max(float(low.income.quantile(tail)), float(high.income.quantile(tail)))
            upper = min(float(low.income.quantile(1-tail)), float(high.income.quantile(1-tail)))
            row.update(income_lower_brl=lower, income_upper_brl=upper)
            overlap = group[group.income.between(lower, upper)].copy()
            if lower >= upper:
                row["reason"] = "Low/high groups have no positive-width common income range"
            elif min(sum(overlap.race_share <= low_cut), sum(overlap.race_share >= high_cut)) < cfg["support_min_group"]:
                row["reason"] = "Insufficient low/high observations in common income range"
            else:
                overlap["support_bin"] = _quantile_bins(overlap.income, cfg["support_bins"])
                for bin_id, cell in overlap.groupby("support_bin"):
                    low_cell = cell[cell.race_share <= low_cut]
                    high_cell = cell[cell.race_share >= high_cut]
                    supported = min(len(low_cell), len(high_cell)) >= cfg["support_min_cell"]
                    cell_rows.append({"municipality": municipality, "support_bin": int(bin_id),
                                      "income_min_brl": float(cell.income.min()),
                                      "income_max_brl": float(cell.income.max()),
                                      "income_median_brl": float(cell.income.median()),
                                      "n_areas": len(cell), "n_low": len(low_cell), "n_high": len(high_cell),
                                      "low_race_share": float(low_cell.race_share.median()) if len(low_cell) else np.nan,
                                      "high_race_share": float(high_cell.race_share.median()) if len(high_cell) else np.nan,
                                      "supported": bool(supported)})
                    selected.loc[cell.index, "support_bin"] = int(bin_id)
                    selected.loc[cell.index, "supported"] = supported
                row["n_supported"] = int(selected.loc[group.index, "supported"].sum())
                row["supported"] = row["n_supported"] > 0
                row["reason"] = "Supported observed income bins" if row["supported"] else "No income bins contain sufficient low/high observations"
        municipality_rows.append(row)
    return selected[selected.supported].copy(), {
        "support_counts": pd.DataFrame(counts, columns=["municipality", "income_quintile", "race_quintile", "n_areas",
                                                        "income_min_brl", "income_max_brl", "race_share_min", "race_share_max"]),
        "support_by_municipality": pd.DataFrame(municipality_rows, columns=["municipality", "n_eligible", "low_race_cut",
                "high_race_cut", "n_low", "n_high", "income_lower_brl", "income_upper_brl", "n_supported", "supported", "reason"]),
        "support_cells": pd.DataFrame(cell_rows, columns=["municipality", "support_bin", "income_min_brl", "income_max_brl",
                "income_median_brl", "n_areas", "n_low", "n_high", "low_race_share", "high_race_share", "supported"]),
    }


def _basis_info(data):
    income = np.log1p(data.income.to_numpy(float))
    # WHY: an explicit centred cubic basis is reproducible at prediction time,
    # avoids implicit knots, and exposes rather than masks singular designs.
    return {"income_centre": float(income.mean()), "income_scale": float(income.std()) or 1.,
            "race_centre": float(data.race_share.mean()),
            "black_centre": float(data.black_share.mean()), "brown_centre": float(data.brown_share.mean()),
            "municipalities": sorted(data.municipality.unique().tolist())}


def _design(data, basis, specification, separate=False):
    columns = {"intercept": np.ones(len(data))}
    race_names = ["black", "brown"] if separate else ["race"]
    for race in race_names:
        columns[f"{race}_share"] = data[f"{race}_share"].to_numpy(float) - basis[f"{race}_centre"]
    if specification >= 2:
        z = (np.log1p(data.income.to_numpy(float))-basis["income_centre"])/basis["income_scale"]
        for degree in (1, 2, 3):
            columns[f"log_income_degree_{degree}"] = z**degree
        if specification == 3:
            for race in race_names:
                for degree in (1, 2, 3):
                    columns[f"{race}_income_degree_{degree}"] = columns[f"{race}_share"] * z**degree
            columns["log_density"] = np.log1p(data.density.to_numpy(float))
    for municipality in basis["municipalities"][1:]:
        columns[f"municipality_{municipality}"] = data.municipality.eq(municipality).to_numpy(float)
    return pd.DataFrame(columns, index=data.index)


def _blocks(data, cfg):
    # INVARIANT: blocks share the projected CRS and cross municipal boundaries;
    # municipality labels must not split physically adjacent block members.
    size = cfg["spatial_block_size_m"]
    return (np.floor(data.x_m/size).astype("int64").astype(str) + ":" +
            np.floor(data.y_m/size).astype("int64").astype(str))


def _residual_diagnostic(data, residuals, model):
    if len(data) < 3:
        return {"model": model, "n_areas": len(data), "n_neighbor_edges": 0,
                "moran_style_i": np.nan, "interpretation": "Insufficient observations"}
    n_neighbors = min(5, len(data)-1)
    indices = cKDTree(data[["x_m", "y_m"]].to_numpy(float)).query(
        data[["x_m", "y_m"]].to_numpy(float), k=n_neighbors+1)[1]
    edges = set()
    for origin, neighbors in enumerate(indices):
        for target in neighbors:
            if origin != target:
                edges.add(tuple(sorted((origin, int(target)))))
    centered = np.asarray(residuals)-np.mean(residuals)
    denominator = float(centered @ centered)
    statistic = (len(data)/len(edges) * sum(centered[a]*centered[b] for a, b in edges)/denominator
                 if denominator > 0 and edges else np.nan)
    return {"model": model, "n_areas": len(data), "n_neighbor_edges": len(edges),
            "moran_style_i": float(statistic),
            "interpretation": "Exploratory symmetric five-nearest-neighbor residual association; no significance test"}


def _predictions(data, cells, basis, specification, result, critical, model):
    predictions, contrasts, gradients, deltas = [], [], [], []
    params, covariance = np.asarray(result.params), np.asarray(result.cov_params())
    for cell in cells[cells.supported].itertuples(index=False):
        observations = data[(data.municipality == cell.municipality) & (data.support_bin == cell.support_bin)]
        if observations.empty:
            continue
        center = observations.copy()
        center["income"] = cell.income_median_brl
        # CONTRACT: covariates are standardized over actual observations within
        # each supported bin; levels use observed low/high-group share medians.
        row_designs, row_means = {}, {}
        for scenario, race_share in [("low", cell.low_race_share), ("high", cell.high_race_share)]:
            scenario_data = center.copy()
            scenario_data["race_share"] = race_share
            x = _design(scenario_data, basis, specification).to_numpy(float).mean(axis=0)
            mu = float(x @ params)
            variance = float(x @ covariance @ x)
            standard_error = math.sqrt(max(variance, 0))
            predictions.append({"model": model, "municipality": cell.municipality, "support_bin": cell.support_bin,
                                "income": cell.income_median_brl, "scenario": scenario, "race_share": race_share,
                                "prediction_km": float(np.expm1(mu)), "lower_km": float(np.expm1(mu-critical*standard_error)),
                                "upper_km": float(np.expm1(mu+critical*standard_error)), "n_areas": len(observations)})
            row_designs[scenario], row_means[scenario] = x, mu
        gradient = np.exp(row_means["high"])*row_designs["high"] - np.exp(row_means["low"])*row_designs["low"]
        difference = float(np.expm1(row_means["high"])-np.expm1(row_means["low"]))
        se = math.sqrt(max(float(gradient @ covariance @ gradient), 0))
        contrasts.append({"model": model, "scope": "supported_income_bin", "municipality": cell.municipality,
                          "support_bin": cell.support_bin, "income": cell.income_median_brl,
                          "low_race_share": cell.low_race_share, "high_race_share": cell.high_race_share,
                          "difference_km": difference, "lower_km": difference-critical*se,
                          "upper_km": difference+critical*se, "n_areas": len(observations)})
        # WHY: the overall contrast standardizes at *each area's* actual income,
        # not only the cell median. Derivatives propagate the fitted covariance.
        designs = {}
        for scenario, race_share in [("low", cell.low_race_share), ("high", cell.high_race_share)]:
            scenario_data = observations.copy()
            scenario_data["race_share"] = race_share
            designs[scenario] = _design(scenario_data, basis, specification).to_numpy(float)
        lo_mu, hi_mu = designs["low"] @ params, designs["high"] @ params
        gradients.extend(np.exp(hi_mu)[:, None]*designs["high"] - np.exp(lo_mu)[:, None]*designs["low"])
        deltas.extend(np.expm1(hi_mu)-np.expm1(lo_mu))
    if deltas:
        gradient = np.asarray(gradients).mean(axis=0)
        difference = float(np.mean(deltas))
        se = math.sqrt(max(float(gradient @ covariance @ gradient), 0))
        contrasts.append({"model": model, "scope": "area_weighted_standardized", "municipality": "all_supported",
                          "support_bin": np.nan, "income": np.nan, "low_race_share": np.nan,
                          "high_race_share": np.nan, "difference_km": difference,
                          "lower_km": difference-critical*se, "upper_km": difference+critical*se, "n_areas": len(deltas)})
    return predictions, contrasts


def _fit_family(data, support, cfg, prefix=""):
    coverage, coefficients, predictions, contrasts, residuals = [], [], [], [], []
    names = ["racial_composition", "income_adjusted", "income_density_interaction", "black_brown_sensitivity"]
    for number, name in enumerate(names):
        model = prefix + name
        row = {"model": model, "status": "unestimable", "reason": "", "n_areas": len(data),
               "n_parameters": 0, "n_spatial_blocks": 0, "rank": 0, "r_squared": np.nan,
               "income_basis": "centred cubic polynomial of log1p(income)" if number else "none"}
        if len(data) < cfg["min_model_n"]:
            row["reason"] = f"Supported sample below min_model_n={cfg['min_model_n']}"
            coverage.append(row)
            continue
        basis = _basis_info(data)
        specification = min(number+1, 3)
        design = _design(data, basis, specification, separate=number == 3)
        rank = int(np.linalg.matrix_rank(design.to_numpy(float)))
        blocks = _blocks(data, cfg)
        n_blocks = int(blocks.nunique())
        row.update(n_parameters=design.shape[1], rank=rank, n_spatial_blocks=n_blocks)
        if rank < design.shape[1]:
            row["reason"] = "Rank-deficient design; no terms silently dropped"
        elif len(data) <= design.shape[1] + 5:
            row["reason"] = "Insufficient residual degrees of freedom"
        elif n_blocks < cfg["min_spatial_blocks"]:
            row["reason"] = f"Too few spatial blocks for robust uncertainty: need {cfg['min_spatial_blocks']}"
        else:
            try:
                import statsmodels.api as sm
            except ImportError as error:
                raise WorkflowError("Install locked Python dependencies: statsmodels is required for proximity models") from error
            result = sm.OLS(np.log1p(data.nearest_network_km.to_numpy(float)), design).fit(
                cov_type="cluster", cov_kwds={"groups": blocks.to_numpy(), "use_correction": True,
                                               "df_correction": True}, use_t=True)
            covariance = np.asarray(result.cov_params())
            if not np.isfinite(result.params).all() or not np.isfinite(covariance).all():
                row["reason"] = "Nonfinite coefficients or cluster covariance"
            else:
                critical = float(student_t.ppf(.975, n_blocks-1))
                row.update(status="estimated", reason="", r_squared=float(result.rsquared))
                for term, coefficient, standard_error, p_value in zip(design.columns, result.params,
                                                                     result.bse, result.pvalues):
                    coefficients.append({"model": model, "term": term, "coefficient": float(coefficient),
                                         "standard_error": float(standard_error), "lower": float(coefficient-critical*standard_error),
                                         "upper": float(coefficient+critical*standard_error), "p_value": float(p_value),
                                         "scale": "log1p(network distance in km)"})
                residuals.append(_residual_diagnostic(data, result.resid, model))
                if number != 3:
                    pred, con = _predictions(data, support["support_cells"], basis, specification, result, critical, model)
                    predictions.extend(pred)
                    contrasts.extend(con)
        coverage.append(row)
    return {"model_coverage": pd.DataFrame(coverage, columns=COVERAGE_COLUMNS),
            "coefficients": pd.DataFrame(coefficients, columns=COEFFICIENT_COLUMNS),
            "predictions": pd.DataFrame(predictions, columns=PREDICTION_COLUMNS),
            "contrasts": pd.DataFrame(contrasts, columns=CONTRAST_COLUMNS),
            "residual_spatial": pd.DataFrame(residuals, columns=["model", "n_areas", "n_neighbor_edges", "moran_style_i", "interpretation"])}


def _correlations(data):
    rows = []
    variables = ["income", "race_share", "black_share", "brown_share", "density", "nearest_network_km"]
    for left_index, left in enumerate(variables):
        for right in variables[left_index+1:]:
            pair = data[[left, right]].replace([np.inf, -np.inf], np.nan).dropna()
            estimable = len(pair) >= 3 and pair[left].nunique() > 1 and pair[right].nunique() > 1
            rows.append({"left": left, "right": right, "n_areas": len(pair),
                         "pearson": float(pair[left].corr(pair[right])) if estimable else np.nan,
                         "spearman": float(pair[left].corr(pair[right], method="spearman")) if estimable else np.nan})
    return pd.DataFrame(rows)


def analyse(frame, cfg):
    """Return audit tables and model estimates, or an explicit unestimable status.

    ``income_complete_2022`` controls an independent complete-coverage sensitivity
    family whose empirical support is rechecked. It never changes the retained
    census income mean or imputes missing incomes/routes. Every result is an
    ecological conditional association; an adjusted coefficient is not a direct
    race effect or a mediated proportion of disparity.
    """
    settings = _settings(cfg)
    data, audit = _valid_sample(frame)
    eligible = data[audit.eligible_before_support].copy()
    supported, support = _support(eligible, settings)
    audit["included_in_model"] = audit.common_id.isin(supported.common_id)
    tables = dict(support)
    tables["sample_audit"] = audit
    tables["input_audit"] = pd.DataFrame([
        {"check": "Input common areas", "n_areas": len(data)},
        *[{"check": "Failed " + flag, "n_areas": int((~audit[flag]).sum())} for flag in
          ["valid_route", "valid_income", "valid_race", "valid_density", "valid_spatial_coordinates"]],
        {"check": "Eligible before joint-support restriction", "n_areas": len(eligible)},
        {"check": "Included in common supported model sample", "n_areas": len(supported)}])
    tables.update(_fit_family(supported, support, settings))
    tables["correlations"] = _correlations(eligible)
    notices = []
    complete_column = next((column for column in ["income_complete_2022", "complete_2022", "income_complete"]
                            if column in data), None)
    if complete_column is None:
        notices.append("Complete-income-coverage sensitivity unavailable: coverage flag absent")
    else:
        complete_values = eligible[complete_column]
        if not complete_values.dropna().isin([True, False, 0, 1]).all():
            raise WorkflowError("Income coverage flags must be boolean; strings cannot be coerced")
        complete = eligible[complete_values.eq(True)].copy()
        complete_supported, complete_support = _support(complete, settings)
        complete_tables = _fit_family(complete_supported, complete_support, settings, prefix="complete_income_")
        for key, table in complete_tables.items():
            tables[key] = pd.concat([tables[key], table], ignore_index=True)
        for key, table in complete_support.items():
            tables["complete_income_" + key] = table
        notices.append(f"Complete-income sensitivity: {len(complete)} eligible areas; {len(complete_supported)} jointly supported")
    fitted = tables["model_coverage"].set_index("model").status
    main_models = ["racial_composition", "income_adjusted", "income_density_interaction"]
    status = "estimated" if all(fitted.get(name) == "estimated" for name in main_models) else (
        "partially_estimable" if any(fitted.get(name) == "estimated" for name in main_models) else "unestimable")
    if eligible.empty:
        notices.append("No origins have complete valid routing and model covariates")
    if supported.empty:
        notices.append("No empirical within-municipality income/racial-composition overlap meets minimum counts")
    metadata = {"status": status, "n_input_areas": len(data), "n_eligible_areas": len(eligible),
                "n_supported_areas": len(supported), "settings": settings,
                "analysis_unit": "complete harmonised common_id census area",
                "outcome": "log1p(shortest street-network distance to a registered Obrasgov project, km)",
                "prediction_scale": "expm1 of conditional mean log1p distance; not arithmetic mean distance",
                "contrast_scale": "high minus low observed racial-composition transformed-scale predictions, km",
                "standardization": "equal area weights; local empirical racial-share medians; observed municipality/income/density",
                "uncertainty": "95% spatial-block cluster-robust intervals; Student t with block_count-1 degrees of freedom",
                "support": "within-municipality low/high share groups; trimmed common income range; sufficient groups in each income bin",
                "residual_diagnostic": "symmetric five-nearest-neighbor Moran-style association, descriptive; no p-value",
                "interpretation": "Ecological conditional associations; no individual racial effect, discrimination or causal mediation estimate",
                "notices": notices}
    return {"tables": tables, "metadata": metadata}


def _notice_figure(path, title, text):
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(figsize=(8, 4))
    axes.axis("off")
    axes.set_title(title, loc="left", fontweight="bold")
    axes.text(.02, .72, text, transform=axes.transAxes, va="top", wrap=True, fontsize=11)
    figure.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(figure)


def write_figures(frame, tables, metadata, outdir):
    """Render real observed support and supported predictions, including notices.

    Matplotlib's backend is the caller's choice (pipeline/report runners use
    Agg). No illustrative curves are substituted for failed estimations.
    """
    import matplotlib.pyplot as plt
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    files = {name: outdir/name for name in ["income-race-support.png", "distance-predictions.png", "adjusted-contrasts.png"]}
    data, audit = _valid_sample(frame)
    valid = data[audit.eligible_before_support].copy()
    sample = tables["sample_audit"].set_index("common_id")
    selected = valid.common_id.map(sample.included_in_model).fillna(False)
    if len(valid):
        figure, axes = plt.subplots(figsize=(8, 5))
        for mask, color, label in [(~selected, "#bfc5c7", "Outside supported comparison sample"),
                                   (selected, "#008b92", "Supported comparison sample")]:
            axes.scatter(valid.loc[mask, "income"], valid.loc[mask, "race_share"]*100,
                         s=9, alpha=.35, color=color, label=label, rasterized=True)
        axes.set_xscale("symlog", linthresh=100)
        axes.set_xlabel("2022 head-weighted mean neighbourhood income (BRL; symlog scale)")
        axes.set_ylabel("Black + Brown population (%)")
        axes.set_title("Observed income–racial composition support")
        axes.legend(fontsize=8, loc="best")
        figure.text(.02, .01, f"{len(valid):,} complete valid origins; {int(selected.sum()):,} supported. Support assessed within each municipality.", fontsize=8)
        figure.tight_layout(rect=(0, .035, 1, 1))
        figure.savefig(files["income-race-support.png"], dpi=150)
        plt.close(figure)
    else:
        _notice_figure(files["income-race-support.png"], "Income–racial composition support unavailable",
                       "No origins have complete valid route, income, racial-composition, density and projected-coordinate inputs.\nSee input_audit and sample_audit for exclusions.")
    predictions = tables["predictions"]
    predictions = predictions[predictions.model.eq("income_density_interaction")]
    if len(predictions):
        municipalities = predictions.groupby("municipality").n_areas.sum().sort_values(ascending=False).head(4).index
        figure, axes = plt.subplots(len(municipalities), 1, figsize=(8, 3.4*len(municipalities)), squeeze=False)
        for ax, municipality in zip(axes[:, 0], municipalities):
            rows = predictions[predictions.municipality == municipality]
            for scenario, color, label in [("low", "#147e92", "Lower observed Black/Brown share"),
                                           ("high", "#d16543", "Higher observed Black/Brown share")]:
                group = rows[rows.scenario == scenario].sort_values("support_bin")
                # WHY: never draw a continuous line through an unsupported bin.
                segments = (group.support_bin.diff().fillna(1) > 1).cumsum()
                for segment_number, (_, segment) in enumerate(group.groupby(segments)):
                    ax.plot(segment.income, segment.prediction_km, "o-", color=color,
                            label=label if segment_number == 0 else None)
                    ax.fill_between(segment.income.to_numpy(float), segment.lower_km.to_numpy(float),
                                    segment.upper_km.to_numpy(float), color=color, alpha=.17)
                ax.set_title(f"Municipality {municipality} — supported observed income bins", fontsize=11)
                ax.set_ylabel("Transformed-scale predicted distance (km)")
                ax.set_xlabel("2022 mean neighbourhood income (BRL)")
                ax.legend(fontsize=8)
        figure.text(.02, .008, "95% spatial-block robust intervals. Observed share levels vary by bin; expm1 predictions are not arithmetic means.\nConditional neighbourhood associations, not individual discrimination or service access.", fontsize=8)
        figure.tight_layout(rect=(0, .065/len(municipalities), 1, 1))
        figure.savefig(files["distance-predictions.png"], dpi=150)
        plt.close(figure)
    else:
        _notice_figure(files["distance-predictions.png"], "Adjusted distance predictions not estimable",
                       "The joint-support, sample-size, model-rank or spatial-block requirements were not met.\nNo curves are extrapolated or substituted. See model_coverage for exact reasons.")
    contrasts = tables["contrasts"]
    contrasts = contrasts[contrasts.scope.eq("area_weighted_standardized")]
    if len(contrasts):
        figure, axes = plt.subplots(figsize=(8, max(3.8, .65*len(contrasts))))
        positions = np.arange(len(contrasts))
        errors = np.stack([contrasts.difference_km-contrasts.lower_km,
                           contrasts.upper_km-contrasts.difference_km])
        axes.errorbar(contrasts.difference_km, positions, xerr=errors, fmt="o", color="#147e92", capsize=3)
        axes.axvline(0, color="#999999", linewidth=1)
        axes.set_yticks(positions)
        axes.set_yticklabels([name.replace("_", " ") for name in contrasts.model], fontsize=9)
        axes.invert_yaxis()
        axes.set_xlabel("Higher minus lower observed Black/Brown share: predicted distance difference (km)")
        axes.set_title("Area-weighted standardized contrasts")
        figure.text(.02, .01, "95% spatial-block robust delta-method intervals. Same supported sample for the three main specifications.\nComplete-income sensitivities recheck support; these are conditional neighbourhood associations.", fontsize=8)
        figure.tight_layout(rect=(0, .07, 1, 1))
        figure.savefig(files["adjusted-contrasts.png"], dpi=150)
        plt.close(figure)
    else:
        _notice_figure(files["adjusted-contrasts.png"], "Distance contrasts not estimable",
                       "No specification satisfied empirical support and inference requirements.\nInput exclusions and model limitations remain recorded; no zero contrast is invented.")
    return files
