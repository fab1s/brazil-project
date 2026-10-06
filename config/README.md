# Workflow Configuration

Status: current
Last updated: 2026-10-06
Version: 0.2
Scope: Workflow Configuration

## Edit History

| Date | Version | Edited by | Reason |
| ---- | ------- | --------- | ------ |
| 2026-10-06 | 0.2 | Codex | Documented location QA parameters. |
| 2026-10-05 | 0.1 | Codex | Established the independent research project. |

Paths and scientific constants in project.toml; original Obrasgov translations in obrasgov_translations.json. Paths resolve against the configured root. Update methods and tests whenever scientific configuration changes.

## Main Workflows

Use the project CLI and documented setup from the root README. Read relevant methods before editing analytical code.

## Update Rules

Update this README when local responsibilities or artifact contracts change. Preserve source provenance and report verification scope.

The `[location_qa]` section selects the frozen Obrasgov snapshot, geographic-reference directory, a 5 km offshore uncertainty tolerance, 1 km foreign-boundary tolerance, 1 km line sampling spacing and maximum 250 interpolated samples per line. All original vertices are checked even when sampling is capped. These are screening choices, separate from faithful translation and subject to the [location policy](../docs/methods/obrasgov-location-policy.md).
