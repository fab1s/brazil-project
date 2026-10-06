# Remaining Research Tasks

Status: current
Last updated: 2026-10-06
Version: 0.8
Scope: Remaining Research Tasks

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.8 | Codex | Updated report-review tasks for the Markdown workflow. |
| 2026-10-05 | 0.4 | Codex | Added Obrasgov coordinate-quality review. |

- Review the [harmonisation update](harmonisation-update.md) and its footprint/coverage diagnostics under the approved boundary-change assumption. The requested implementation corrections are complete.
- Supply the exact `20220601_regional_barreiro_cadastro_imobiliario.csv` referenced by the property report, or approve a separate dated-input methodological change.
- Inspect the seven small overlapping-piece cases identified by the audit. Original pieces are preserved and unique part IDs are implemented.
- Review the original stored density absolute-change discrepancy and the income prose/code discrepancy separately from translation.
- Verify full national correspondence recomputation before replacing the original default crosswalk.
- Record live IBAMA and Obrasgov acquisition comparisons against provider snapshots when acquisition is requested.
- Review generated research reports and figures before publication. Fresh Python outputs are review copies; update the maintained Markdown only after reviewing values and figures.
- Supply the original Linha Verde shapefile to restore the optional overlay; no substitute was inferred.
- Do not mark scientific or publication review complete merely because software tests pass.

- Review the completed [national Obrasgov location QA](obrasgov-location-qa.md): offshore, coastal, foreign-border, administrative and possible marine flags require provider evidence before correction.

The national diagnostic and clean/quarantine exports are complete; see [verification](obrasgov-location-qa.md). Remaining location work is review of flagged source IDs, provider-supported corrections and marine exceptions, coastal/island edge cases, and deliberate map publication if this derivative is adopted. Never infer corrected coordinates or present eligible locations as validated geocoding.

The [approved primary-state exclusion](obrasgov-primary-state-filter.md) is implemented: all 2,346 entirely-outside components are excluded from the separate derivative; 224,495 map components remain after baseline QA. Review partially intersecting projects separately and adopt/publish the final map derivative when requested. No source correction or whole-project deletion was inferred.
