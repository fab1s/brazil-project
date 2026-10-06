# Data Provenance And Migration

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Data Provenance And Migration

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.2 | Codex | Recorded geographic references and location derivatives. |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

## Original project

Source folder: `/Users/fa4850sc/Library/CloudStorage/OneDrive-LundUniversity/Brazil Project`.

Every original file has a row in migration_manifest.csv with original relative path, destination, byte count, SHA256, classification, duplicate-content reference, and copy status. Existing duplicated contents are retained with their paths; no scientific consolidation was assumed. Copy verification reads original and copied files and compares both against the recorded hash.

All 344 files were copied and checksum verified. The original bytes total 12,175,700,758. No source file was edited or removed.

## Additional local inputs

Eight existing censobr v0.5.0 Parquet inputs were imported from the user's local R cache. Their full source paths and checksums are recorded in `data/raw/ibge/census/provenance.json`. They were not downloaded during migration. The optional R adapter retains censobr acquisition for future input recovery.

## Data classifications

Raw contains original source tables and boundaries. Reference contains codebooks, inflation workbooks, valuation references, and supplied PDFs. Processed contains copied original outputs used as baselines. Intermediate contains new reproducible stage artifacts. Archive contains original code, outputs, backups, and session files.

Original notes remain verbatim under `docs/reference/original_notes/`. Files that describe legacy working directories should be interpreted with the migration manifest rather than edited retroactively.

## Source limitations

The 2022 display base has duplicate tract IDs. The cadastral CSV referenced by the property notebook is absent. A parsed valuation workbook is an exploratory input rather than an authenticated legal interpretation. Source package caching and live provider access may have restrictions recorded in the original notes.

## Location-quality references and derivatives

[Geographic-reference provenance](location-qa-references.json) records pinned IBGE municipality mesh 2022 and Natural Earth archive URLs, checksums, acquisition dates and internal version labels. The full zips stay under `data/reference/location-qa/` outside Git. The diagnostic source is the preserved original frozen map GeoPackage, not a newly harvested or translated snapshot. [Verification evidence](../verification/obrasgov-location-qa-evidence.json) records its checksum and all derivative contracts. Corrected coordinates have not been inferred or substituted.
