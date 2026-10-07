# Research Data

Status: current
Last updated: 2026-10-07
Version: 0.3
Scope: Research Data

- `raw/`: immutable source datasets, grouped by provider.
- `processed/`: preserved source result baselines.
- `reference/`: codebooks, workbooks and geographic references.
- `intermediate/`: generated stage bundles used by processing.
- `archive/`: original code, source notes, outputs and session material; recovery copies of the previous layout.

Full datasets stay local by researcher choice; GitHub tracks their checksum inventory and recovery instructions. The exact input paths are in [project.toml](../project.toml); stages create outputs only when executed. See [provenance](../docs/provenance.md) and [workflow](../docs/workflow.md). Do not overwrite original inputs or replace missing inputs with guesses.

## Research material included in GitHub

- [Original R and Quarto sources](archive/original_code/): immutable historical implementations used by parity checks.
- [Original figures](archive/original_outputs/): historical visual results, separate from current processing outputs.
- [IBGE references](reference/ibge/): original codebooks, questionnaires, manuals and inflation workbook.
- [Land-value references](reference/land_value/): supplied PDFs and the parsed workbook used by processing.
- [Location-reference manifest](reference/location-qa/manifest.json): acquisition URLs and checksums; geographic ZIP archives remain local.

The [baseline inventory](../docs/evidence/baseline-files.csv) identifies every preserved GeoPackage by path, size and SHA-256. Their combined size exceeds ordinary Git storage limits. Reference documents and original figures are preserved exactly; inclusion does not change their licenses or establish scientific validation.

## Recovering local baselines on another machine

Keep the complete local project backed up separately from Git. To restore the baseline files, copy `data/processed/` from that backup into the same path in a fresh clone. Alternatively, use `docs/evidence/migration_manifest.csv` to find each baseline's original relative path in the preserved OneDrive Brazil Project and copy it to its recorded destination, without modifying OneDrive.

Verify each restored file against `docs/evidence/baseline-files.csv` using its byte count and SHA-256 (`shasum -a 256 <file>` on macOS). Do not substitute newly acquired releases for these historical baselines. Raw census tables and tract geometries are also required by the pipeline; restore them using the migration manifest and the local census `provenance.json` described in [provenance](../docs/provenance.md). The baseline inventory alone is not a complete input backup. Location reference archives can be recovered from the URLs and hashes in their [manifest](reference/location-qa/manifest.json).
