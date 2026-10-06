# Research Reference Inputs

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Research Reference Inputs

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.2 | Codex | Recorded location screening references. |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

Codebooks, workbooks and source reference documents remain supplied originals. Changes to parsed valuation material require independent review.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

`location-qa/` preserves the explicitly downloaded IBGE municipal mesh 2022 and Natural Earth land/coastline release archives and their checksum/URL/date manifest. They are independent QA references, not replacements for census tract geometry. Routine processing rejects missing or changed references and never downloads them automatically. Full archives remain outside Git; a small provenance record accompanies verification documentation.
