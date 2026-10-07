# Here.now Map Workflow

Status: maintained
Last updated: 2026-10-07
Version: 0.4
Scope: Build and update the existing research map from local validated common areas

Browser source is under `website/`. The public site remains `https://sandy-ivory-k65c.here.now/`. Public data derivatives are generated in `outputs/maps/website/`; never publish the project root, raw datasets, work GeoPackage, credentials, or local here.now state.

## Inputs and preparation

The build requires the national versioned harmonisation bundle and the matching indicator report/tables. It rejects stale indicator versions, duplicate common IDs, and indicator IDs outside the bundle. Some indicator tables omit groups entirely; these retain their geometry and unavailable estimates. Out-of-range proportions remain unavailable in map presentation, matching the earlier website rule.

IBAMA, favelas, timeline, and other existing assets are frozen from the current website. Obrasgov is rebuilt from the approved national location derivative, using the same frozen source records. The snapshot utility verifies published hashes and preserves these without rebuilding them from a different research snapshot. Snapshotting is an explicit network step, only needed to initialize or deliberately refresh the existing assets:

```bash
.venv/bin/python code/scripts/snapshot_web_map.py --output outputs/maps/website
```

This reads a saved here.now credential or `HERENOW_API_KEY` without printing it. An optional `--local-site /path/to/old/site` avoids downloads only for checksum-identical files. It does not overwrite maintained source under `website/`.

## Build

```bash
.venv/bin/python code/scripts/build_web_map.py --config project.toml --output outputs/maps/website --work .cache/map-update/build
```

Use a fresh work folder for changed inputs. `--reuse-prepared` supports interrupted tile generation only when source fingerprints and the prepared GeoPackage checksum match. Use the project Python environment and `ogr2ogr` with the PMTiles driver; this publication used GDAL 3.13.3. Generated archives have an input-derived suffix in `data/social.json`; the browser reads the manifest before creating sources and uses its actual regional bounds. Browser module query versions must also be updated for source changes.

The work GeoPackage has one `social` row per common ID, all 13 indicators, and complete group sizes. Its overview contains 5,570 municipality features. The export creates 16 regional archives (zoom 7–9, simplified at 100 m; zoom 10–12, with overzoom) plus a municipality overview at zoom 2–6. Geographic tile clipping and coordinate quantisation are display operations; exported attributes use the research tables and density's saved equal-area denominator. Detailed geometry is the merged 2022 footprint, including disconnected MultiPolygons.

Search indexes support both preserved numeric common IDs and member-derived `g_` IDs from explicit recomputation.

Common groups may touch multiple municipalities or regions. Municipal summaries use each whole group once per touched municipality and therefore are not strict within-boundary estimates; nationwide summaries deduplicate globally. Regional archives can share those same common IDs. Popup selection deduplicates by common ID.

The website preserves income's real percentage-change presentation and density's percentage change. Counts, weights, inflation, missing years, and denominators follow the research outputs. The approved boundary-change assumption is visible in the explanatory controls; habitation has not independently verified it. Coverage summaries report unmatched tract counts, known population/household totals, and missing values.

## Verify and publish

Run the Python suite, compare all exported attributes with the source tables, and inspect rendered maps and controls. Check range responses and real tile loading at overview, mid, and detail zooms, then common-ID search, popups, summary coverage, density change, income, and mobile layout. Preserve unchanged infrastructure/community hashes; record the deliberate Obrasgov archive replacement separately.

Publish only the completed site directory, using the here.now skill's helper:

```bash
bash /Users/fa4850sc/.agents/skills/here-now/scripts/publish.sh outputs/maps/website --slug sandy-ivory-k65c --client codex
```

The helper stages files, skips unchanged hashes, uploads changed assets, and finalizes the existing slug. Save the publication version and verification evidence in `docs/evidence/`. A failed build must not be published. No scientific publication review is implied by software/render checks.

## Obrasgov display policy

At researcher request, Obrasgov polygon components have no fill layer and are excluded from map interaction. Only point and line layers are registered, including after background changes. Mixed collections can still display their point/line components. Raw records and archived previous PMTiles remain unchanged; IBAMA polygons, favelas and census areas are unaffected. Source-record totals and investment summaries still include polygon records, with explicit wording in the interface.

The approved location QA and primary-state exclusions are published through the derivative described in [the publication record](website-location-update.md). Build it after the existing national Obrasgov command:

```bash
.venv/bin/brazil-project run obrasgov --config project.toml
.venv/bin/python code/scripts/build_obras_web_map.py --config project.toml
```

The exporter verifies producer records and source hashes, preserves source attributes and component geometry in the prepared exchange, and updates map counts separately from source-record summaries. The exporter copies maintained browser source into the publication folder; inspect it and publish with the command above. Preserve the previous archive under `data/archive/` before removing it from the active site directory. No automatic coordinate correction is performed.
