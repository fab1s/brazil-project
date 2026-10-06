# Brazil Project Migration Plan

Status: current
Last updated: 2026-10-06
Version: 0.4
Scope: Brazil Project Migration Plan

## Implemented project organization

The complete original folder is copied locally, classified, and checksum verified. Research documents are separated from executable code; original scripts, Quarto notebooks, backups, outputs, and session files remain recoverable. Duplicate contents are recorded and conflicting files are never overwritten silently.

The migration manifest accounts for all 344 original files totaling 12,175,700,758 bytes. It records 78 additional files sharing already-seen content checksums. Existing GeoPackages remain original baselines; new results use independent intermediates.

## Workflow migration

The Python runner exposes explicit acquisition, overview, harmonisation, indicators, infrastructure, land-value, and chart stages. Acquisition does not run as a dependency of routine analysis. Failed stages are recorded and return a nonzero result.

Census and boundary acquisition remain isolated R adapters. The exploratory geographic overview retains sf/S2 to preserve spherical intersection behavior. Python performs projected correspondence, annual indicators, income, population density, infrastructure processing, and conference chart calculations.

The original workflow ordering and narrative are retained through Markdown reports and separate Python report scripts. Each original executable chunk is mapped to its implementation and artifact contract. Original R code remains available for independent reference validation.

## Validation strategy

Compare copies against original SHA256 checksums. Validate synthetic edge cases, complete common-area membership, original stored outputs, fresh R reference calculations, chart populations, cutoffs, and rendered figures. Store reference mismatches as evidence instead of changing the original files.

Python correspondence recomputation is explicit; routine runs validate the original crosswalk for positive polygon-area overlap while national recomputation parity remains unverified.

## Completion boundaries

All existing research areas are represented. The property notebook's workbook and available geometry imports are implemented, but its exact cadastral CSV is missing from the original folder. Fresh infrastructure downloads are implemented with resumable caches and tested response handling; live external endpoint equivalence is not claimed without a recorded acquisition run.

The later researcher-approved harmonisation policy is recorded separately in `docs/harmonisation-policy.md`; it excludes contact-only matches and adds merged outputs. Data defects and differences between current source code and stored results are documented for scientific review.
