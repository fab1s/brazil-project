# Research Data

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Research Data

- `raw/`: immutable source datasets, grouped by provider.
- `processed/`: preserved source result baselines.
- `reference/`: codebooks, workbooks and geographic references.
- `intermediate/`: generated stage bundles used by processing.
- `archive/`: original code, source notes, outputs and session material; recovery copies of the previous layout.

Full datasets stay outside Git. The exact input paths are in [project.toml](../project.toml); stages create outputs only when executed. See [provenance](../docs/provenance.md) and [workflow](../docs/workflow.md). Do not overwrite original inputs or replace missing inputs with guesses.
