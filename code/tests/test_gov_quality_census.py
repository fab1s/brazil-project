"""Synthetic correctness checks; not a declaration of national scientific validity."""
from copy import deepcopy
import json

import numpy as np
import pandas as pd
import pytest

from brazil_project.io import Context, WorkflowError
from brazil_project.infrastructure.gov_quality_census import (
    audit_frames, audit_census, _read_bundle, _sha256, _verify_saved_income, write_census_figures)
from brazil_project.acquisition.census import filename
from brazil_project.harmonisation.census import POLICY


def fixture_tables():
    ids = ["310620000000001", "310620000000002", "310620000000003", "310620000000004"]
    group_ids = ["a", "b", "c", "d"]
    race = {
        2010: pd.DataFrame({"code_tract": ids, "population": [100., 0., 10., np.nan],
                           "black": [10., 0., np.nan, 0.], "brown": [20., 0., 3., 0.]}),
        2022: pd.DataFrame({"code_tract": ids, "population": [100., 5., 10., 50.],
                           "black": [10., 4., 20., 0.], "brown": [20., 4., 0., 5.]}),
    }
    sources = {year: pd.DataFrame({"code_tract": ids, "heads": [10., 0., 5., 10.],
                                   "mean_income": [1000., 500., np.nan, 2000.]}) for year in [2010, 2022]}
    lookups = {year: pd.DataFrame({f"id_{year}": ids, "common_id": group_ids}) for year in [2010, 2022]}
    groups = pd.DataFrame({"common_id": group_ids, "n_2010": [1]*4, "n_2022": [1]*4, "relationship": ["1:1"]*4})
    indicators = {}
    for name in ["black", "brown", "black_brown"]:
        frame = pd.DataFrame({"common_id": group_ids})
        for year in [2010, 2022]:
            raw = race[year]
            count = raw[name] if name != "black_brown" else raw.black.fillna(0)+raw.brown.fillna(0)
            # Saved combined counts preserve the existing zero-coalescing rule.
            frame[f"{name}_pop_{year}"] = count.to_numpy()
            frame[f"{name}_ratio_{year}"] = (count/raw.population.where(raw.population > 0)).to_numpy()
            frame[f"pop_{year}"] = raw.population.to_numpy()
        indicators[name] = frame
    income = pd.DataFrame({"common_id": group_ids})
    for year in [2010, 2022]:
        for key, values in {"income": [1000., np.nan, np.nan, 2000.], "complete": [True, True, False, True],
                            "tract_coverage_pct": [100., 0., 0., 100.], "heads_used": [10., 0., 0., 10.],
                            "n_used": [1, 0, 0, 1], "missing_weights": [0]*4, "missing_means": [0, 0, 1, 0]}.items():
            income[f"{key}_{year}"] = values
    indicators["income"] = income
    indicators["population_density"] = pd.DataFrame({"common_id": group_ids, "area_km2": [1.]*4,
        "population_density_2010": race[2010].population, "population_density_2022": race[2022].population})
    return race, sources, indicators, lookups, groups


def _count(result, year, measure):
    data = result["tables"]["census_annual_coverage"]
    return int(data[(data.year == year) & (data.measure == measure)].n_common_areas.iloc[0])


def test_saved_ratio_does_not_hide_missing_source_components():
    result = audit_frames(*fixture_tables())
    assert _count(result, 2010, "race_ratio_available") == 2
    assert _count(result, 2010, "race_ratio_fully_observed") == 1
    assert _count(result, 2010, "race_component_gap") == 1
    assert _count(result, 2010, "race_denominator_gap") == 1
    assert _count(result, 2022, "race_ratio_available") == 2
    assert _count(result, 2022, "race_ratio_fully_observed") == 2
    flags = result["tables"]["census_race_source_quality_by_state"]
    check = flags[(flags.year == 2022) & flags.check.eq("race_total_above_population")]
    assert check.n_flagged.sum() == 2


def test_zero_weight_can_be_complete_without_an_available_income():
    result = audit_frames(*fixture_tables())
    assert _count(result, 2022, "income_available") == 2
    assert _count(result, 2022, "income_complete_available") == 2
    source = result["tables"]["census_income_source_quality_by_state"]
    assert source[source.check.eq("zero_heads")].n_flagged.sum() == 2  # one per year
    assert source[source.check.eq("missing_mean_positive_heads")].n_flagged.sum() == 2
    assert "zero-head" in result["metadata"]["income_coverage_definition"]


def test_missing_year_is_not_imputed_and_pair_counts_partition_universe():
    frames = fixture_tables()
    frames[2]["income"].loc[0, "income_2010"] = np.nan
    result = audit_frames(*frames)
    data = result["tables"]["census_paired_coverage"]
    income = data[data.measure == "income_available"].set_index("availability")
    assert income.n_common_areas.sum() == 4
    assert income.loc["both_years", "n_common_areas"] == 1
    assert income.loc["2022_only", "n_common_areas"] == 1
    assert _count(result, 2010, "income_available") == 1


def test_duplicate_source_key_and_duplicate_common_key_fail():
    frames = fixture_tables()
    frames[0][2010] = pd.concat([frames[0][2010], frames[0][2010].iloc[:1]])
    with pytest.raises(WorkflowError, match="unique"):
        audit_frames(*frames)
    frames = fixture_tables()
    frames[2]["black"] = pd.concat([frames[2]["black"], frames[2]["black"].iloc[:1]])
    with pytest.raises(WorkflowError, match="unique"):
        audit_frames(*frames)


def test_lookup_group_and_indicator_universe_must_agree():
    frames = fixture_tables()
    frames[4].loc[0, "n_2022"] = 2
    with pytest.raises(WorkflowError, match="group-size"):
        audit_frames(*frames)
    frames = fixture_tables()
    frames[2]["income"] = frames[2]["income"].iloc[:3]
    with pytest.raises(WorkflowError, match="universe"):
        audit_frames(*frames)


def test_ratio_count_and_component_inconsistencies_reported_not_corrected():
    frames = fixture_tables()
    frames[2]["black_brown"].loc[0, "black_brown_ratio_2022"] = .7
    original = frames[2]["black_brown"].copy(deep=True)
    result = audit_frames(*frames)
    assert _count(result, 2022, "race_count_ratio_inconsistent") == 1
    assert _count(result, 2022, "race_component_ratio_inconsistent") == 1
    pd.testing.assert_frame_equal(frames[2]["black_brown"], original)


def test_negative_and_infinite_source_values_are_flagged():
    frames = fixture_tables()
    frames[0][2022].loc[0, "population"] = np.inf
    frames[0][2022].loc[3, "black"] = -1
    frames[1][2022].loc[0, "heads"] = -5
    result = audit_frames(*frames)
    race = result["tables"]["census_race_source_quality_by_state"]
    assert race[(race.year == 2022) & race.check.eq("missing_population")].n_flagged.sum() == 1
    assert race[(race.year == 2022) & race.check.eq("negative_race_component")].n_flagged.sum() == 1
    income = result["tables"]["census_income_source_quality_by_state"]
    assert income[(income.year == 2022) & income.check.eq("negative_heads")].n_flagged.sum() == 1


def test_invalid_ids_and_cross_state_groups_are_explicit():
    frames = fixture_tables()
    frames[0][2010].loc[0, "code_tract"] = "invalid"
    frames[1][2010].loc[0, "code_tract"] = "invalid"
    # Keep the invalid-ID finding visible without silently coercing it.
    result = audit_frames(*frames)
    assert len(result["tables"]["census_identifier_issues"]) == 2
    frames = fixture_tables()
    frames[3][2022] = pd.concat([frames[3][2022], pd.DataFrame({"id_2022": ["330455700000001"], "common_id": ["a"]})])
    frames[4].loc[0, "n_2022"] = 2
    result = audit_frames(*frames)
    state = result["tables"]["census_common_area_quality_by_state"]
    assert "multi_state" in state[state.year == 2022].state.tolist()


def test_scope_rejected_before_inputs_are_read(tmp_path):
    config = tmp_path/"project.toml"
    config.write_text('[project]\nroot="."\nmunicipality="3106200"\n')
    with pytest.raises(WorkflowError, match="national-only"):
        audit_census(Context(config))
    assert not (tmp_path/"data").exists()


def bundle_fixture(tmp_path):
    config = tmp_path/"project.toml"
    config.write_text('[project]\nroot="."\n[census]\nrecompute_harmonisation=false\n')
    ctx = Context(config)
    generation = "a"*32
    folder = tmp_path/"data/intermediate/harmonisation"
    directory = folder/"bundles"/generation
    directory.mkdir(parents=True)
    version = "b"*64
    manifest = {"generation": generation, "version": version, "policy": POLICY, "scope": "Brazil",
                "mode": "validated_original_correspondence", "checksums": {}}
    folder.joinpath("current.json").write_text(json.dumps({"generation": generation, "version": version}))
    _, _, _, lookups, groups = fixture_tables()
    tables = {"lookup_2010": lookups[2010], "lookup_2022": lookups[2022], "group_sizes": groups,
              "common_geometry_2022": groups[["common_id"]]}
    for name, table in tables.items():
        table = table.assign(harmonisation_version=version)
        path = directory/(name+".parquet")
        table.to_parquet(path, index=False)
        manifest["checksums"][name] = _sha256(path)
    directory.joinpath("manifest.json").write_text(json.dumps(manifest))
    return ctx, directory, manifest


def test_bundle_validation_is_read_only_and_rejects_modified_bytes(tmp_path):
    ctx, directory, _ = bundle_fixture(tmp_path)
    before = {path: _sha256(path) for path in tmp_path.rglob("*") if path.is_file()}
    frames, manifest, paths = _read_bundle(ctx)
    assert len(frames["group_sizes"]) == 4
    after = {path: _sha256(path) for path in tmp_path.rglob("*") if path.is_file()}
    assert before == after
    path = directory/"lookup_2022.parquet"
    path.write_bytes(path.read_bytes()+b"bad")
    with pytest.raises(WorkflowError, match="Changed harmonisation"):
        _read_bundle(ctx)


def test_mixed_bundle_version_rejected_even_with_updated_checksum(tmp_path):
    ctx, directory, manifest = bundle_fixture(tmp_path)
    path = directory/"lookup_2022.parquet"
    data = pd.read_parquet(path).assign(harmonisation_version="c"*64)
    data.to_parquet(path, index=False)
    manifest["checksums"]["lookup_2022"] = _sha256(path)
    directory.joinpath("manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(WorkflowError, match="Mixed harmonisation"):
        _read_bundle(ctx)


def test_saved_income_must_match_raw_weights_and_configured_inflation():
    _, sources, indicators, lookups, _ = fixture_tables()
    saved = indicators["income"].copy()
    saved["income_2010_nominal"] = saved.income_2010
    saved["income_2010"] *= 2
    checks = _verify_saved_income(sources, lookups, saved, 2)
    assert checks[0]["inflation_factor"] == 2
    with pytest.raises(WorkflowError, match="configured inflation"):
        _verify_saved_income(sources, lookups, saved, 3)
    sources[2022].loc[0, "mean_income"] += 100
    with pytest.raises(WorkflowError, match="Saved 2022 income"):
        _verify_saved_income(sources, lookups, saved, 2)


def adapter_fixture(tmp_path):
    ctx, _, manifest = bundle_fixture(tmp_path)
    ctx.config_path.write_text('[project]\nroot="."\n[census]\nrecompute_harmonisation=false\n'
        'tables="data/raw/census"\nrelease="test"\ninflation_2010=1\ninflation_2022=1\n')
    ctx = Context(ctx.config_path)
    raw = tmp_path/"data/raw/census"
    raw.mkdir(parents=True)
    race, income, indicators, _, _ = fixture_tables()
    race[2010].rename(columns={"population": "pessoa03_V001", "black": "pessoa03_V003",
        "brown": "pessoa03_V005"}).to_parquet(raw/filename(2010, "Pessoa", "test"), index=False)
    race[2022][["code_tract", "population"]].rename(columns={"population": "V0001"}).to_parquet(
        raw/filename(2022, "Basico", "test"), index=False)
    race[2022][["code_tract", "black", "brown"]].rename(columns={"black": "raca_V01318", "brown": "raca_V01320"}).to_parquet(
        raw/filename(2022, "Pessoas", "test"), index=False)
    for year in (2010, 2022):
        if year == 2010:
            frame = income[year].rename(columns={"heads": "V020", "mean_income": "V022"}).assign(V021=1.)
        else:
            frame = income[year].rename(columns={"heads": "V06001", "mean_income": "V06004"})
        frame.to_parquet(raw/filename(year, "ResponsavelRenda", "test"), index=False)
    output = tmp_path/"data/intermediate/indicators"
    output.mkdir()
    output.joinpath("report.json").write_text(json.dumps({"harmonisation_version": manifest["version"]}))
    for name, frame in indicators.items():
        frame.to_parquet(output/(name+".parquet"), index=False)
    return ctx


def test_adapter_fingerprints_reads_without_mutating_input_files(tmp_path):
    ctx = adapter_fixture(tmp_path)
    before = {path: _sha256(path) for path in tmp_path.rglob("*") if path.is_file()}
    result = audit_census(ctx)
    assert result["metadata"]["input_snapshot_verified_after_read"] is True
    assert len(result["metadata"]["income_validation"]) == 2
    after = {path: _sha256(path) for path in tmp_path.rglob("*") if path.is_file()}
    assert before == after


def test_adapter_rejects_source_change_during_read(tmp_path, monkeypatch):
    ctx = adapter_fixture(tmp_path)
    target = ctx.path("census", "tables")/filename(2010, "Pessoa", "test")
    original_read = pd.read_parquet
    changed = []
    def mutate_after_read(path, *args, **kwargs):
        result = original_read(path, *args, **kwargs)
        if str(path) == str(target) and not changed:
            modified = result.copy()
            modified.loc[0, "pessoa03_V001"] += 1
            modified.to_parquet(target, index=False)
            changed.append(True)
        return result
    monkeypatch.setattr(pd, "read_parquet", mutate_after_read)
    with pytest.raises(WorkflowError, match="input changed during audit"):
        audit_census(ctx)


def test_figures_are_real_finite_outputs_and_do_not_modify_inputs(tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    result = audit_frames(*fixture_tables())
    before = deepcopy(result)
    paths = write_census_figures(result["tables"], result["metadata"], tmp_path)
    assert set(paths) == {"census-coverage-by-state.png", "income-coverage.png", "income-race-observed.png"}
    for path in paths.values():
        assert path.read_bytes().startswith(b"\x89PNG")
        assert path.stat().st_size > 5000
    for name, frame in result["tables"].items():
        pd.testing.assert_frame_equal(frame, before["tables"][name])
