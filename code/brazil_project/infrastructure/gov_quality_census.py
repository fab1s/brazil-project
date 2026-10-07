"""Read-only national census quality checks before infrastructure associations.

No distances, models, imputation or census processing are performed here. Raw
tract measurements are checked separately from saved common-area estimates:
an aggregate ratio can look available after missing components were coalesced
to zero. Area income is a head-weighted mean, not a person-level race/income
joint distribution. This module deliberately preserves those distinctions.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from brazil_project.io import WorkflowError, identifiers, keys, lookup_keys
from brazil_project.acquisition.census import filename
from brazil_project.indicators.temporal import prepare_income, income_aggregate
from brazil_project.harmonisation.census import POLICY


STATE_NAMES = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP",
               "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB",
               "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
               "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS",
               "51": "MT", "52": "GO", "53": "DF"}


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _state(ids):
    codes = ids.astype("string").str[:2]
    return codes.map(STATE_NAMES).fillna("invalid_or_unknown")


def _valid_ids(ids):
    return ids.astype("string").str.fullmatch(r"[0-9]{15}", na=False) & ids.astype("string").str[:2].isin(STATE_NAMES)


def _numeric(series):
    return pd.to_numeric(series, errors="coerce")


def _ratio_quality(frame):
    result = frame[["code_tract"]].copy()
    result["state"] = _state(result.code_tract)
    for column in ["population", "black", "brown"]:
        result[column] = _numeric(frame[column])
    finite_population = np.isfinite(result.population)
    finite_components = np.isfinite(result.black) & np.isfinite(result.brown)
    result["missing_population"] = ~finite_population
    result["zero_population"] = finite_population & result.population.eq(0)
    result["negative_population"] = finite_population & result.population.lt(0)
    result["missing_race_component"] = ~finite_components
    result["negative_race_component"] = ((np.isfinite(result.black) & result.black.lt(0)) |
                                         (np.isfinite(result.brown) & result.brown.lt(0)))
    result["race_total_above_population"] = finite_population & finite_components & (
        result.black + result.brown > result.population)
    result["valid_observed_race_ratio"] = (finite_population & result.population.gt(0) & finite_components &
                                           ~result.negative_race_component & ~result.race_total_above_population)
    result["race_share"] = ((result.black + result.brown)/result.population).where(result.valid_observed_race_ratio)
    result["valid_identifier"] = _valid_ids(result.code_tract)
    return result


def _income_quality(frame):
    result = frame[["code_tract"]].copy()
    result["state"] = _state(result.code_tract)
    result["heads"] = _numeric(frame.heads)
    result["mean_income"] = _numeric(frame.mean_income)
    result["missing_heads"] = ~np.isfinite(result.heads)
    result["negative_heads"] = np.isfinite(result.heads) & result.heads.lt(0)
    result["zero_heads"] = np.isfinite(result.heads) & result.heads.eq(0)
    result["missing_mean_positive_heads"] = np.isfinite(result.heads) & result.heads.gt(0) & ~np.isfinite(result.mean_income)
    result["negative_mean_positive_heads"] = np.isfinite(result.heads) & result.heads.gt(0) & np.isfinite(result.mean_income) & result.mean_income.lt(0)
    result["valid_weighted_income_pair"] = (np.isfinite(result.heads) & result.heads.gt(0) &
                                            np.isfinite(result.mean_income) & result.mean_income.ge(0))
    result["valid_identifier"] = _valid_ids(result.code_tract)
    return result


def _flags_by_state(frame, year, flags):
    rows = []
    for state, part in frame.groupby("state", sort=True):
        for flag in flags:
            count = int(part[flag].sum())
            rows.append({"year": year, "state": state, "check": flag, "n_tracts": len(part),
                         "n_flagged": count, "share_pct": 100*count/len(part)})
    return rows


def _structure(frame, year, dataset):
    ids = frame.code_tract
    return {"year": year, "dataset": dataset, "source_rows": len(frame),
            "distinct_nonmissing_tract_ids": int(ids.nunique()), "missing_ids": int(ids.isna().sum()),
            "repeated_nonmissing_id_rows": int(ids.notna().sum()-ids.nunique()),
            "invalid_identifier_rows": int((~_valid_ids(ids)).sum())}


def _distribution(values, year, variable, unit, source):
    numeric = _numeric(values)
    valid = numeric[np.isfinite(numeric)]
    record = {"year": year, "variable": variable, "unit": unit, "source": source,
              "n_rows": len(values), "n_finite": len(valid), "n_nonfinite": len(values)-len(valid),
              "n_negative": int((valid < 0).sum()), "n_zero": int((valid == 0).sum())}
    for name, quantile in [("minimum", 0), ("p01", .01), ("p25", .25), ("median", .5),
                            ("p75", .75), ("p95", .95), ("p99", .99), ("maximum", 1)]:
        record[name] = float(valid.quantile(quantile)) if len(valid) else np.nan
    return record


def audit_frames(race_sources, income_sources, indicators, lookups, group_sizes):
    """Pure audit used by the national adapter and synthetic verification.

    Source tables use ``code_tract,population,black,brown`` and
    ``code_tract,heads,mean_income``. Saved indicators retain their existing
    provider-derived column names. No source or derived result is modified.
    """
    keys(group_sizes, "common_id")
    structure, variable_rows, race_state, income_state, population_coverage, issues = [], [], [], [], [], []
    race_audits, income_audits, clean_lookups = {}, {}, {}
    for year in (2010, 2022):
        for dataset, frame in [("racial_composition", race_sources[year]), ("head_weighted_income", income_sources[year])]:
            keys(frame, "code_tract")
            structure.append(_structure(frame, year, dataset))
            invalid = frame[~_valid_ids(frame.code_tract)][["code_tract"]].copy()
            if len(invalid):
                invalid["year"], invalid["dataset"] = year, dataset
                issues.extend(invalid.to_dict("records"))
            for column in frame.columns:
                if column != "code_tract":
                    unit = "BRL, source-year basis" if column == "mean_income" else "count"
                    variable_rows.append(_distribution(frame[column], year, column, unit, dataset))
        race = _ratio_quality(race_sources[year])
        income = _income_quality(income_sources[year])
        race_audits[year], income_audits[year] = race, income
        race_state.extend(_flags_by_state(race, year, ["missing_population", "zero_population", "negative_population",
            "missing_race_component", "negative_race_component", "race_total_above_population", "valid_observed_race_ratio", "valid_identifier"]))
        valid_population = np.isfinite(race.population) & race.population.ge(0)
        known_total = float(race.population.where(valid_population).sum())
        for flag in ["missing_race_component", "negative_race_component", "race_total_above_population", "valid_observed_race_ratio"]:
            mask = race[flag]
            known_flagged = float(race.population.where(mask & valid_population).sum())
            population_coverage.append({"year": year, "check": flag, "n_source_tracts": int(mask.sum()),
                "known_population_flagged": known_flagged, "source_known_population_total": known_total,
                "share_of_known_population_pct": 100*known_flagged/known_total if known_total > 0 else np.nan,
                "flagged_tracts_missing_population": int((mask & ~valid_population).sum()),
                "unit": "people in source tracts with known finite nonnegative population; incomplete totals explicitly retained"})
        income_state.extend(_flags_by_state(income, year, ["missing_heads", "negative_heads", "zero_heads",
            "missing_mean_positive_heads", "negative_mean_positive_heads", "valid_weighted_income_pair", "valid_identifier"]))
        lookup = lookup_keys(lookups[year], year)
        if lookup.common_id.isna().any() or not set(lookup.common_id).issubset(set(group_sizes.common_id.astype("string"))):
            raise WorkflowError("Census quality audit lookup has invalid common-area memberships")
        counts = lookup.groupby("common_id")[f"id_{year}"].nunique().reindex(group_sizes.common_id.astype("string"))
        if counts.isna().any() or not np.array_equal(counts.to_numpy(), group_sizes[f"n_{year}"].to_numpy()):
            raise WorkflowError("Census quality audit lookup/group-size contract mismatch")
        clean_lookups[year] = lookup
    for name, frame in indicators.items():
        keys(frame, "common_id")
        if set(frame.common_id.astype("string")) != set(group_sizes.common_id.astype("string")):
            raise WorkflowError(f"Census quality indicator {name} does not cover the active common-area universe")
    common = group_sizes[["common_id", "n_2010", "n_2022", "relationship"]].copy()
    common["common_id"] = common.common_id.astype("string")
    for year in (2010, 2022):
        state = clean_lookups[year].copy()
        state["state"] = _state(state[f"id_{year}"])
        state_groups = state.groupby("common_id").state.agg(["first", "nunique"])
        group_state = state_groups["first"].where(state_groups["nunique"].eq(1), "multi_state")
        common[f"state_{year}"] = common.common_id.map(group_state)
        lookup = clean_lookups[year][[f"id_{year}", "common_id"]].rename(columns={f"id_{year}": "code_tract"})
        joined = lookup.merge(race_audits[year], on="code_tract", how="left", validate="one_to_one")
        joined["race_component_gap"] = joined.missing_race_component.astype("boolean").fillna(True)
        joined["race_denominator_gap"] = joined.missing_population.astype("boolean").fillna(True)
        joined["race_any_invalid"] = ~joined.valid_observed_race_ratio.astype("boolean").fillna(False)
        flags = joined.groupby("common_id")[["race_component_gap", "race_denominator_gap", "race_any_invalid"]].any()
        for flag in flags:
            common[f"{flag}_{year}"] = common.common_id.map(flags[flag]).fillna(True)
    selected = {
        "black_brown": [f"{name}_{year}" for year in (2010, 2022) for name in ["black_brown_ratio", "black_brown_pop", "pop"]],
        "black": [f"black_ratio_{year}" for year in (2010, 2022)],
        "brown": [f"brown_ratio_{year}" for year in (2010, 2022)],
        "income": [f"{name}_{year}" for year in (2010, 2022) for name in ["income", "complete", "tract_coverage_pct", "heads_used", "n_used", "missing_weights", "missing_means"]],
        "population_density": ["area_km2", "population_density_2010", "population_density_2022"],
    }
    for name, columns in selected.items():
        absent = [column for column in columns if column not in indicators[name]]
        if absent:
            raise WorkflowError(f"Census quality saved {name} is missing columns: {absent}")
        frame = indicators[name][["common_id"]+columns].copy()
        frame["common_id"] = frame.common_id.astype("string")
        common = common.merge(frame, on="common_id", how="left", validate="one_to_one")
    annual_rows, common_state, income_distribution = [], [], []
    for year in (2010, 2022):
        race_ratio = _numeric(common[f"black_brown_ratio_{year}"])
        population = _numeric(common[f"pop_{year}"])
        race_numerator = _numeric(common[f"black_brown_pop_{year}"])
        common[f"race_ratio_available_{year}"] = np.isfinite(race_ratio) & race_ratio.between(0, 1) & np.isfinite(population) & population.gt(0)
        common[f"race_ratio_fully_observed_{year}"] = common[f"race_ratio_available_{year}"] & ~common[f"race_any_invalid_{year}"]
        common[f"race_count_ratio_inconsistent_{year}"] = (np.isfinite(race_ratio) & np.isfinite(population) & population.gt(0) &
            ~np.isclose(race_ratio, race_numerator/population, rtol=1e-10, atol=1e-12))
        common[f"race_component_ratio_inconsistent_{year}"] = (np.isfinite(race_ratio) &
            np.isfinite(common[f"black_ratio_{year}"]) & np.isfinite(common[f"brown_ratio_{year}"]) &
            ~np.isclose(race_ratio, common[f"black_ratio_{year}"]+common[f"brown_ratio_{year}"], rtol=1e-10, atol=1e-12))
        mean_income = _numeric(common[f"income_{year}"])
        common[f"income_available_{year}"] = np.isfinite(mean_income) & mean_income.ge(0) & common[f"heads_used_{year}"].gt(0)
        complete = common[f"complete_{year}"]
        if not complete.dropna().isin([True, False, 0, 1]).all():
            raise WorkflowError("Saved income completeness flags must be boolean")
        common[f"income_complete_available_{year}"] = common[f"income_available_{year}"] & complete.eq(True)
        common[f"joint_available_{year}"] = common[f"income_available_{year}"] & common[f"race_ratio_available_{year}"]
        common[f"joint_fully_observed_{year}"] = common[f"income_complete_available_{year}"] & common[f"race_ratio_fully_observed_{year}"]
        flags = [f"{name}_{year}" for name in ["race_ratio_available", "race_ratio_fully_observed", "race_component_gap",
            "race_denominator_gap", "race_any_invalid", "race_count_ratio_inconsistent", "race_component_ratio_inconsistent",
            "income_available", "income_complete_available", "joint_available", "joint_fully_observed"]]
        for flag in flags:
            count = int(common[flag].sum())
            annual_rows.append({"year": year, "measure": flag[:-5], "n_common_areas": count,
                                "denominator_common_areas": len(common), "share_pct": 100*count/len(common) if len(common) else np.nan})
        for state, part in common.groupby(f"state_{year}", sort=True):
            for flag in flags:
                count = int(part[flag].sum())
                common_state.append({"year": year, "state": state, "measure": flag[:-5], "n_common_areas": len(part),
                                     "n_available_or_flagged": count, "share_pct": 100*count/len(part)})
        income_distribution.append(_distribution(common[f"income_{year}"].where(common[f"income_available_{year}"]),
            year, "head_weighted_mean_income", "July 2022 BRL", "all available common areas"))
        income_distribution.append(_distribution(common[f"income_{year}"].where(common[f"income_complete_available_{year}"]),
            year, "head_weighted_mean_income", "July 2022 BRL", "complete income coverage only"))
    paired_rows = []
    for flag in ["race_ratio_available", "race_ratio_fully_observed", "income_available", "income_complete_available",
                 "joint_available", "joint_fully_observed"]:
        old, new = common[f"{flag}_2010"], common[f"{flag}_2022"]
        for status, mask in [("both_years", old & new), ("2010_only", old & ~new), ("2022_only", ~old & new), ("neither_year", ~old & ~new)]:
            paired_rows.append({"measure": flag, "availability": status, "n_common_areas": int(mask.sum()),
                                "denominator_common_areas": len(common), "share_pct": 100*float(mask.mean()) if len(common) else np.nan})
    plots = common[["common_id", "state_2022", "income_2022", "black_brown_ratio_2022", "tract_coverage_pct_2022",
                    "income_available_2022", "income_complete_available_2022", "race_ratio_available_2022", "joint_fully_observed_2022"]].copy()
    metadata = {"scope": "Brazil", "status": "descriptive_quality_audit", "n_common_areas": len(common),
        "unit": "source tract and complete harmonised common area, reported separately",
        "no_analysis_started": "No network acquisition, distances, regressions, imputation, corrections or filters",
        "income_definition": "Existing head-weighted tract mean; 2010 converted to July 2022 BRL using configured historical inflation factor",
        "income_coverage_definition": "complete flag excludes missing valid weights/means; zero-head tracts do not contribute and can remain complete",
        "race_availability_definition": "saved finite ratio in [0,1] with positive population denominator",
        "fully_observed_race_definition": "all contributing tract denominators positive and both components finite, nonnegative and summing no higher than population",
        "interpretation": "Availability is not measurement validity. Aggregate income and racial share do not provide individual race-income joint distributions.",
        "limits": ["Missing race components can become zero under preserved combined-race aggregation rules.",
                   "Common-area income completeness is distinct from whether a finite mean is saved.",
                   "Source-year income populations/definitions differ; inflation conversion does not establish comparability.",
                   "A common-area racial-composition/income association cannot identify individual income-adjusted racial differences.",
                   "Areas spanning states are reported as multi_state, never silently assigned.",
                   "This audit does not establish causal timing between the census and infrastructure projects."]}
    return {"tables": {"census_source_structure": pd.DataFrame(structure), "census_source_variables": pd.DataFrame(variable_rows),
        "census_race_source_quality_by_state": pd.DataFrame(race_state), "census_income_source_quality_by_state": pd.DataFrame(income_state),
        "census_common_area_quality_by_state": pd.DataFrame(common_state), "census_annual_coverage": pd.DataFrame(annual_rows),
        "census_paired_coverage": pd.DataFrame(paired_rows), "census_income_distribution": pd.DataFrame(income_distribution),
        "census_race_population_coverage": pd.DataFrame(population_coverage),
        "census_identifier_issues": pd.DataFrame(issues, columns=["code_tract", "year", "dataset"]),
        "census_plot_data": plots}, "metadata": metadata}


def _read_bundle(ctx):
    """Verify consumed bundle contracts without updating any checksum cache."""
    folder = ctx.intermediate/"harmonisation"
    pointer_path = ctx.require(folder/"current.json")
    pointer = json.loads(pointer_path.read_text())
    generation = pointer.get("generation", "")
    if len(generation) != 32 or any(character not in "0123456789abcdef" for character in generation):
        raise WorkflowError("Invalid harmonisation generation in national census quality audit")
    directory = folder/"bundles"/generation
    manifest_path = ctx.require(directory/"manifest.json")
    manifest = json.loads(manifest_path.read_text())
    expected_mode = "recomputed_python" if ctx.config["census"].get("recompute_harmonisation", False) else "validated_original_correspondence"
    if manifest.get("version") != pointer.get("version") or manifest.get("policy") != POLICY or manifest.get("scope") != "Brazil" or manifest.get("mode") != expected_mode:
        raise WorkflowError("National census quality audit requires a consistent current national harmonisation bundle")
    frames, paths = {}, [pointer_path, manifest_path]
    for name in ["lookup_2010", "lookup_2022", "group_sizes", "common_geometry_2022"]:
        path = ctx.require(directory/(name+".parquet"))
        if _sha256(path) != manifest["checksums"].get(name):
            raise WorkflowError("Changed harmonisation artifact in census quality audit: " + name)
        columns = ["common_id", "harmonisation_version"] if name == "common_geometry_2022" else None
        frame = pd.read_parquet(path, columns=columns)
        if "harmonisation_version" not in frame or not frame.harmonisation_version.eq(manifest["version"]).all():
            raise WorkflowError("Mixed harmonisation versions in census quality audit")
        frames[name] = frame.drop(columns="harmonisation_version")
        paths.append(path)
    keys(frames["common_geometry_2022"], "common_id")
    if set(frames["common_geometry_2022"].common_id) != set(frames["group_sizes"].common_id):
        raise WorkflowError("Geometry/group universe mismatch in census quality audit")
    return frames, manifest, paths


def _verify_saved_income(income_sources, lookups, saved, inflation_factor):
    """Validate saved income against raw eligible pairs and actual configuration.

    Reconstructing the existing weighted calculation is an audit check only;
    it does not publish a newly processed estimate. Without this check a custom
    inflation setting could incorrectly label a previously saved income table.
    """
    if not np.isfinite(inflation_factor) or inflation_factor <= 0:
        raise WorkflowError("Census quality inflation factor must be finite and positive")
    keys(saved, "common_id")
    checks = []
    for year in (2010, 2022):
        source = income_sources[year].rename(columns={"code_tract": f"id_{year}"})
        reconstructed = income_aggregate(source, lookups[year], year)
        expected = reconstructed[["common_id", f"income_{year}"]].rename(columns={f"income_{year}": "expected"})
        actual = saved[["common_id", f"income_{year}"]].rename(columns={f"income_{year}": "actual"})
        joined = expected.merge(actual, on="common_id", how="outer", validate="one_to_one", indicator=True)
        factor = inflation_factor if year == 2010 else 1.
        equal = np.isclose(joined.actual, joined.expected*factor, rtol=1e-9, atol=1e-6, equal_nan=True)
        mismatches = joined[~equal | ~joined["_merge"].eq("both")]
        if len(mismatches):
            raise WorkflowError(f"Saved {year} income differs from raw eligible pairs/configured inflation in {len(mismatches)} common areas; rerun indicators explicitly")
        if year == 2010 and "income_2010_nominal" in saved:
            nominal = expected.merge(saved[["common_id", "income_2010_nominal"]], on="common_id", validate="one_to_one")
            if not np.isclose(nominal.income_2010_nominal, nominal.expected, rtol=1e-9, atol=1e-6, equal_nan=True).all():
                raise WorkflowError("Saved nominal 2010 income differs from raw eligible pairs; rerun indicators explicitly")
        checks.append({"year": year, "n_common_areas": len(joined), "inflation_factor": factor,
                       "relative_tolerance": 1e-9, "absolute_tolerance_brl": 1e-6,
                       "missingness_matched": True, "check": "raw eligible head-weighted income versus saved estimate"})
    return checks


def audit_census(ctx):
    """Audit actual local national sources and saved indicators, with fingerprints."""
    if ctx.municipality:
        raise WorkflowError("gov-quality census audit is national-only; remove municipality scope")
    paths, snapshots = [], {}
    def capture(path):
        path = ctx.require(path)
        if path not in snapshots:
            snapshots[path] = {"size_bytes": path.stat().st_size, "sha256": _sha256(path)}
            paths.append(path)
        return path
    # CONTRACT: capture fingerprints before reading, including the bundle
    # pointer. A direct helper call is protected without relying on CLI tracking.
    pointer_path = capture(ctx.intermediate/"harmonisation"/"current.json")
    pointer = json.loads(pointer_path.read_text())
    generation = pointer.get("generation", "")
    if len(generation) != 32 or any(character not in "0123456789abcdef" for character in generation):
        raise WorkflowError("Invalid harmonisation generation in national census quality audit")
    directory = pointer_path.parent/"bundles"/generation
    capture(directory/"manifest.json")
    for name in ["lookup_2010", "lookup_2022", "group_sizes", "common_geometry_2022"]:
        capture(directory/(name+".parquet"))
    bundle, manifest, _ = _read_bundle(ctx)
    indicator_report_path = capture(ctx.artifact("indicators", "report.json"))
    indicator_report = json.loads(indicator_report_path.read_text())
    if indicator_report.get("harmonisation_version") != manifest["version"]:
        raise WorkflowError("Saved indicators use a different harmonisation version; rerun indicators explicitly")
    release = ctx.config["census"]["release"]
    def raw(year, dataset, columns):
        path = capture(ctx.path("census", "tables")/filename(year, dataset, release))
        frame = pd.read_parquet(path, columns=columns)
        frame["code_tract"] = identifiers(frame.code_tract)
        keys(frame, "code_tract")
        return frame
    old = raw(2010, "Pessoa", ["code_tract", "pessoa03_V001", "pessoa03_V003", "pessoa03_V005"])
    old = old.rename(columns={"pessoa03_V001": "population", "pessoa03_V003": "black", "pessoa03_V005": "brown"})
    basic = raw(2022, "Basico", ["code_tract", "V0001"])
    persons = raw(2022, "Pessoas", ["code_tract", "raca_V01318", "raca_V01320"])
    new = basic.merge(persons, on="code_tract", how="outer", validate="one_to_one", indicator=True)
    join_counts = new["_merge"].value_counts().to_dict()
    new = new.drop(columns="_merge").rename(columns={"V0001": "population", "raca_V01318": "black", "raca_V01320": "brown"})
    incomes, original_income_variables = {}, []
    for year, codes in [(2010, ["V020", "V021", "V022"]), (2022, ["V06001", "V06004"])]:
        path = capture(ctx.path("census", "tables")/filename(year, "ResponsavelRenda", release))
        schema = pq.read_schema(path).names
        selected = ["code_tract"]
        for code in codes:
            matched = [column for column in schema if column == code or column.endswith("_"+code)]
            if len(matched) != 1:
                raise WorkflowError(f"Census quality expected one income field {code}; got {matched}")
            selected += matched
        source = raw(year, "ResponsavelRenda", selected)
        original_income_variables.extend(_distribution(source[column], year, column,
            "provider count or source-year BRL; see original codebook", "ResponsavelRenda original field")
            for column in selected if column != "code_tract")
        prepared = prepare_income(source, year).rename(columns={f"id_{year}": "code_tract"})
        incomes[year] = prepared
    indicators = {}
    for name in ["black", "brown", "black_brown", "income", "population_density"]:
        path = capture(ctx.artifact("indicators", name+".parquet"))
        indicators[name] = pd.read_parquet(path)
    inflation_2010, inflation_2022 = ctx.config["census"]["inflation_2010"], ctx.config["census"]["inflation_2022"]
    if not np.isfinite(inflation_2010) or inflation_2010 <= 0 or not np.isfinite(inflation_2022) or inflation_2022 <= 0:
        raise WorkflowError("Census quality inflation indexes must be finite and positive")
    inflation_factor = float(inflation_2022/inflation_2010)
    income_checks = _verify_saved_income(incomes, {year: bundle[f"lookup_{year}"] for year in (2010, 2022)},
                                         indicators["income"], inflation_factor)
    result = audit_frames({2010: old, 2022: new}, incomes, indicators,
                          {year: bundle[f"lookup_{year}"] for year in (2010, 2022)}, bundle["group_sizes"])
    result["tables"]["census_source_variables"] = pd.concat([
        result["tables"]["census_source_variables"], pd.DataFrame(original_income_variables)], ignore_index=True)
    result["metadata"].update({"harmonisation_version": manifest["version"], "harmonisation_generation": manifest["generation"],
                              "2022_source_join": {key: int(value) for key, value in join_counts.items()},
                              "inflation_factor": inflation_factor, "income_validation": income_checks,
                              "input_fingerprints": [{"path": str(path.relative_to(ctx.root)), **snapshots[path]} for path in paths]})
    for path in paths:
        if path.stat().st_size != snapshots[path]["size_bytes"] or _sha256(path) != snapshots[path]["sha256"]:
            raise WorkflowError("Census quality input changed during audit; previous results must remain intact: " + str(path))
    result["metadata"]["input_snapshot_verified_after_read"] = True
    return result


def write_census_figures(tables, metadata, outdir):
    """Generate descriptive national coverage, missingness and observed data plots."""
    import matplotlib.pyplot as plt
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    files = {name: outdir/name for name in ["census-coverage-by-state.png", "income-coverage.png", "income-race-observed.png"]}
    state = tables["census_common_area_quality_by_state"]
    state = state[state.measure.eq("joint_fully_observed")]
    pivot = state.pivot(index="state", columns="year", values="share_pct").reindex(sorted(state.state.unique()))
    figure, axes = plt.subplots(figsize=(11, 5))
    position = np.arange(len(pivot))
    for year, offset, color in [(2010, -.18, "#c87d51"), (2022, .18, "#147e92")]:
        axes.bar(position+offset, pivot[year], .36, color=color, label=str(year))
    axes.set_xticks(position)
    axes.set_xticklabels(pivot.index, rotation=45)
    axes.set_ylim(0, 105)
    axes.set_ylabel("Fully observed race and complete income\n(% of common areas)")
    axes.set_title("National census coverage by state and year")
    axes.legend()
    figure.text(.01, .01, "Denominator: all complete harmonised common areas in each state's year-specific tract membership.\nPositive tract populations and observed race components required; complete income is not individual income coverage.", fontsize=8)
    figure.tight_layout(rect=(0, .08, 1, 1))
    figure.savefig(files["census-coverage-by-state.png"], dpi=150)
    plt.close(figure)
    annual = tables["census_annual_coverage"]
    figure, axes = plt.subplots(figsize=(9, 4.8))
    measures = ["race_ratio_available", "race_ratio_fully_observed", "income_available", "income_complete_available", "joint_fully_observed"]
    labels = ["Saved racial share", "Fully observed racial share", "Finite weighted income", "Complete weighted income", "Both fully observed"]
    for year, offset, color in [(2010, -.18, "#c87d51"), (2022, .18, "#147e92")]:
        rows = annual[annual.year == year].set_index("measure")
        axes.barh(np.arange(len(measures))+offset, rows.loc[measures, "share_pct"], .36, color=color, label=str(year))
    axes.set_yticks(np.arange(len(measures)))
    axes.set_yticklabels(labels)
    axes.invert_yaxis()
    axes.set_xlim(0, 105)
    axes.set_xlabel("All national common areas (%)")
    axes.set_title("Saved availability versus observed component coverage")
    axes.legend()
    figure.text(.01, .01, "A saved ratio can remain available when missing components were coalesced to zero.\nThe complete-income flag and tract contribution percentage describe different aspects of weighting.", fontsize=8)
    figure.tight_layout(rect=(0, .09, 1, 1))
    figure.savefig(files["income-coverage.png"], dpi=150)
    plt.close(figure)
    data = tables["census_plot_data"]
    data = data[data.income_available_2022 & data.race_ratio_available_2022]
    figure, axes = plt.subplots(figsize=(8.5, 5.6))
    if len(data):
        usable = data.income_2022.gt(0)
        artist = axes.hexbin(data.loc[usable, "income_2022"], data.loc[usable, "black_brown_ratio_2022"]*100,
                             xscale="log", gridsize=55, mincnt=1, bins="log", cmap="viridis")
        figure.colorbar(artist, ax=axes, label="Number of common areas (log colour scale)")
        axes.set_xlabel("2022 head-weighted mean neighbourhood income (BRL; log scale)")
        axes.set_ylabel("Black + Brown population (%)")
        axes.set_title("Saved national income and racial composition")
        zero_count = int((~usable).sum())
        figure.text(.01, .01, f"{len(data):,} areas with saved valid income/racial shares; {zero_count:,} zero-income areas omitted from log axis.\nSaved shares can include missing race components coalesced to zero; availability is not full observation.\nArea counts, not population weights. National municipality mix; no model, individual comparison or causal inference.", fontsize=8)
    else:
        axes.axis("off")
        axes.text(.05, .7, "No common areas have saved valid income and racial shares.\nSee audit tables; no synthetic observations substituted.", transform=axes.transAxes)
    figure.tight_layout(rect=(0, .105, 1, 1))
    figure.savefig(files["income-race-observed.png"], dpi=150)
    plt.close(figure)
    return files
