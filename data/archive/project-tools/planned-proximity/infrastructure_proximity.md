# Infrastructure proximity, neighbourhood income and racial composition

Measure distances from census-area centroids to distinct registered Obrasgov projects, then examine whether neighbourhood racial composition is associated with proximity at comparable measured income. These are geographical associations, not evidence of individual discrimination, infrastructure use or causal effects.

[Variable and dataset codebook](../../docs/codebook.md) · [Methods](../../docs/methods.md) · [All reports](../README.md#read-the-reports)

Run `brazil-project run infrastructure-proximity --config project.toml` to process inputs and update this report. Use `brazil-project report infrastructure_proximity --from-saved --config project.toml` to display existing verified artifacts only. A road-network download requires the separate explicit `acquire-network` command; neither routine processing nor report refresh acquires data. Add `--municipality <IBGE code>` for a separate scoped report under `outputs/reports/`, leaving this maintained source unchanged.

## Processing code and pipeline

Execution order: `harmonisation → indicators → infrastructure-proximity → this report`. The [CLI dispatcher](../../code/brazil_project/cli.py) executes [proximity.py → run()](../../code/brazil_project/infrastructure/proximity.py). The [report engine](../../code/brazil_project/report_engine.py) executes the cells below in one fresh process and replaces their generated sections after input and producer checks.

| Responsibility | Active source | Inputs | Saved results |
| --- | --- | --- | --- |
| Distances and research table | [proximity.py → run()](../../code/brazil_project/infrastructure/proximity.py) | Versioned common-area geometry; 2022 indicators; frozen state-screened project locations with QA evidence; declared local network and provenance | `infrastructure-proximity/analysis.parquet`, route and project diagnostics, `report.json` |
| Income–racial-composition comparisons | [proximity_models.py → analyse()](../../code/brazil_project/infrastructure/proximity_models.py) | The saved analysis population with route and census coverage | Support, sample, model and contrast tables listed in the processing record |
| Current result figures | [proximity_models.py → write_figures()](../../code/brazil_project/infrastructure/proximity_models.py) and [proximity.py → run()](../../code/brazil_project/infrastructure/proximity.py) | Current processing and model tables | `outputs/figures/infrastructure-proximity/<scope>/` |
| Explicit network acquisition | [proximity.py → acquire_network()](../../code/brazil_project/infrastructure/proximity.py) | Configured study extent, network type and acquisition request | Local network and acquisition metadata; never an automatic report dependency |

Table paths without an `outputs/` prefix are under `data/intermediate/`; municipality runs use `data/intermediate/municipality_<code>/`. A national-context invocation can still use the configured study municipalities: **the study scope displayed below, not the report destination, defines the population**. See the [pipeline/source guide](../../docs/pipeline-source.md).

## How to read this analysis

The theoretical question comes from racial spatial stratification: do neighbourhoods with different racial compositions have similar proximity at comparable economic resources? First describe the unadjusted association, then standardize comparisons for measured neighbourhood income. Add density and municipality controls separately. Income and urban location can themselves be pathways of racial inequality; adjusting them changes the question rather than isolating a biological or individual “race effect.”

Each origin is the centroid of one complete, merged `common_id` area. It is not a person's home. Income is the preserved household-head-weighted area mean; racial composition is a resident population share. The analysis does not observe the joint distribution of individual race and income. It cannot compare Black and White people with identical individual incomes or show that infrastructure changed their outcomes.

Distances are metres, with kilometres used where the table or figure says so. The primary outcome is shortest configured street-network distance to a distinct project. Straight-line distance is a benchmark. Multiple retained points belonging to one project count once, using that project's shortest eligible distance. Missing and failed routes are not zero distances. A distance-weighted score describes project concentration, not service access; its configured scale, decay and destination limit belong to the result contract.

This point-distance pilot deliberately omits line and polygon destinations. Their project IDs, exclusions and source geography remain in the QA record; their absence does not mean those investments are absent. All included project categories are retained, without catchments, capacity assumptions, assumed opening dates or claims that a recorded project is operational.

## Study population and data quality

Read these counts before interpreting regression. Check study municipalities, distinct projects versus point components, routing losses and demographic missingness. A successfully routed point is still a screened source location, not independently verified geocoding. The frozen Obrasgov snapshot, census observations and network vintage may describe different dates.

Processing source: [proximity.py → run()](../../code/brazil_project/infrastructure/proximity.py). Report display: [reporting.py → table() and markdown()](../../code/brazil_project/reporting.py). This cell reads saved results; it does not recompute distances.

<details>
<summary>Read current population, route status and sample audits</summary>

<!-- brazil:cell infrastructure_proximity_coverage -->
```python
import json
import pandas as pd
from brazil_project.reporting import table, markdown
summary = report_json("infrastructure-proximity")
model = summary["model"]
available_tables = set(model["tables"])
analysis = ctx.table("infrastructure-proximity", "analysis")
measures = [("Study municipalities", ", ".join(map(str, summary["study_municipalities"]))),
            ("Census origins", summary["origins"]),
            ("Retained project points", summary["total_project_points"]),
            ("Distinct projects", summary["distinct_projects"]),
            ("Processing status", summary["status"]),
            ("Model status", model["status"])]
table(pd.DataFrame(measures, columns=["Measure", "Value"]),
      "Counts refer to the configured study population and screened source locations, not completed or operational facilities.")
table(pd.DataFrame([{"Route status": k, "Census origins": v}
                    for k, v in summary["route_status_counts"].items()]),
      "Route failures remain unavailable; they are not replaced with zero distance.")
for name in ("input_audit", "sample_audit"):
    if name in available_tables:
        table(ctx.table("infrastructure-proximity", name), "Saved " + name.replace("_", " ") + ".")
markdown("<details>\n<summary>Complete processing, timing and network provenance</summary>\n\n```json\n"
         + json.dumps(summary, indent=2, ensure_ascii=False) + "\n```\n\n</details>")
```

</details>

<!-- brazil:output infrastructure_proximity_coverage begin -->
_Results appear after the first successful processing run; no analysis findings are asserted before execution._
<!-- brazil:output infrastructure_proximity_coverage end -->

## Income–racial-composition overlap

Income-adjusted comparisons require actual observations at the racial-composition and income combinations being compared. The support diagnostic shows where those observations exist and where they are scarce. Unsupported combinations are excluded from adjusted contrasts rather than manufactured by extrapolation. Support restrictions change the analysis population; compare the audit counts with the full routed sample.

Processing source: [proximity_models.py → analyse()](../../code/brazil_project/infrastructure/proximity_models.py) and [write_figures()](../../code/brazil_project/infrastructure/proximity_models.py). Report display reads the saved support tables and exact current PNG bytes.

<details>
<summary>Display overlap and the geographical distance checks</summary>

<!-- brazil:cell infrastructure_proximity_support -->
```python
for name in ("support_counts", "support_by_municipality"):
    if name in available_tables:
        table(ctx.table("infrastructure-proximity", name),
              "Income–racial-composition support: counts are census areas, not residents.")
report_image(summary["figures"]["income-race-support.png"])
markdown("**Income–racial-composition overlap.** The plotted population follows the saved coverage and support rules. Empty combinations do not supply evidence for regression contrasts.")
for name, caption in (("distance-map.png", "Study centroids and eligible project points; not household locations or project catchments."),
                      ("distance-benchmark.png", "Configured network-distance versus straight-line benchmark; route and snapping limitations remain in the audit.")):
    if name in summary["figures"]:
        report_image(summary["figures"][name])
        markdown(caption)
```

</details>

<!-- brazil:output infrastructure_proximity_support begin -->
_Support and distance diagnostics are generated from the current processing tables._
<!-- brazil:output infrastructure_proximity_support end -->

## Model comparisons and predicted distances

Compare the overall racial-composition association with the income-standardized association and the specification adding density and municipality. Flexible income terms and an income-by-composition interaction ask whether the composition association changes across income levels. A change between specifications is not a causal mediation percentage.

Prediction curves are restricted to the saved support population. Intervals quantify the uncertainty method recorded in the model contract; they cannot address all spatial, geocoding or temporal errors. A positive contrast means greater distance for the stated higher-composition comparison, conditional on that specification. A missing contrast or informative “not estimable” figure is a limitation, not an estimated zero effect.

Processing source: [proximity_models.py → analyse()](../../code/brazil_project/infrastructure/proximity_models.py) and [write_figures()](../../code/brazil_project/infrastructure/proximity_models.py). Report display reads `model_coverage`, `contrasts` and current figures; methodological calculations remain in the package.

<details>
<summary>Display saved comparisons and predictions</summary>

<!-- brazil:cell infrastructure_proximity_models -->
```python
for name in ("model_coverage", "contrasts"):
    if name in available_tables:
        table(ctx.table("infrastructure-proximity", name),
              "Saved model " + name.replace("_", " ") + "; use the recorded population, units and uncertainty method.")
report_image(summary["figures"]["distance-predictions.png"])
markdown("**Predicted proximity by income and racial composition.** Predictions are neighbourhood associations for supported comparisons; they are not individual outcomes or infrastructure effects.")
report_image(summary["figures"]["adjusted-contrasts.png"])
markdown("**Racial-composition distance contrasts.** Compare specifications and interval widths; income standardization changes the comparison and does not identify discrimination.")
```

</details>

<!-- brazil:output infrastructure_proximity_models begin -->
_Model estimates and notices are saved only after processing succeeds._
<!-- brazil:output infrastructure_proximity_models end -->

## Sensitivity and interpretation checks

Assess correlation between explanatory variables and spatial structure in residuals before treating interval precision as sufficient. The main dataset preserves alternative distances and route-quality fields for further centroid, snapping, destination-category and geocoding checks. An available inverse-distance score is a separate outcome with its own parameter contract, not an interchangeable definition of accessibility.

Processing source: [proximity_models.py → analyse()](../../code/brazil_project/infrastructure/proximity_models.py). Report display reads saved diagnostic tables without refitting or changing the analysis population.

<details>
<summary>Display diagnostic tables and technical coefficients</summary>

<!-- brazil:cell infrastructure_proximity_diagnostics -->
```python
for name in ("correlations", "residual_spatial"):
    if name in available_tables:
        table(ctx.table("infrastructure-proximity", name),
              "Saved " + name.replace("_", " ") + "; a software diagnostic does not establish causal validity.")
if "coefficients" in available_tables:
    markdown("<details>\n<summary>Technical model coefficients; predicted contrasts are the main interpretation</summary>\n")
    table(ctx.table("infrastructure-proximity", "coefficients"), "Coefficients retain their saved model units and reference terms.")
    markdown("</details>")
```

</details>

<!-- brazil:output infrastructure_proximity_diagnostics begin -->
_Diagnostics and limitations accompany the current model generation._
<!-- brazil:output infrastructure_proximity_diagnostics end -->

## Interpretation and limits

This is an exploratory, cross-sectional neighbourhood comparison grounded in racial spatial stratification. It reports proximity to registered project points and conditional associations with area composition and measured income. It does not estimate catchments, functioning services, individual race–income inequalities, discrimination or causal infrastructure effects.

Centroids can poorly represent large or disconnected inhabited areas. A frozen street graph can omit routes or use a vintage unlike the census and project records. The sampled projects are not a complete infrastructure inventory; their statuses, location errors, point-only inclusion and study-boundary coverage can affect distance. Density and geographic controls may absorb pathways of segregation. Common-area merging preserves the comparison contract but reduces spatial resolution. Model support, missingness, temporal mismatch and spatial diagnostic notices must accompany every substantive interpretation.

Figures above are regenerated from processing outputs and copied by exact bytes into report assets. Acquisition and website publication remain separate explicit actions. Source and script-audit evidence are documented in [methods](../../docs/methods.md), [progress](../../docs/progress.md) and the [pipeline source guide](../../docs/pipeline-source.md).
