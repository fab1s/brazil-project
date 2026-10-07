# Interactive Brazil Map

Status: maintained
Last updated: 2026-10-07
Version: 0.3
Scope: Browser source for the existing here.now research map

This folder contains the browser source for [the project map](https://sandy-ivory-k65c.here.now/). It was imported from the user's existing site, version `01M31KE04H54YANWH772AWSSJW`; the earlier local source lived under the September 14 Codex task's `work/brazil-map/site`. This is independent of RISSI.

`app.js` manages the map, project layers, search, camera, and loading. `social-indicators.js` manages the 13 census indicators, formulas, selectors, and common-area popups. `data-summaries.js` renders nationwide estimates and unmatched coverage. `id-search.js` reads generated tract/common-area bounds. `startup.js` reports module failures. CSS and `mobile.js` preserve the existing desktop/mobile controls. `vendor/` retains the existing MapLibre 5.16.0, PMTiles 4.3.0, and Lucide 0.468.0 browser dependencies, with their upstream license texts alongside the files.

The exporter `code/scripts/build_web_map.py` reads the validated national harmonisation bundle and indicator tables. Its active detailed geography has one feature per common ID, including all source pieces; original tract search uses reference bounds. The municipality overview sums complete groups once per municipality touched by their 2022 tracts. Such summaries include whole groups crossing administrative boundaries. Nationwide summaries count each group once.

Generated tiles, manifests, search indexes, and frozen project/community assets live in `outputs/maps/website/`, outside Git. The existing project/community data are preserved by `code/scripts/snapshot_web_map.py`, an explicit network operation. Build and publishing commands, dependencies, and verification limits are in [the web-map workflow](../docs/web-map.md).

Keep source data immutable, retain visible attribution, and version all browser/tile references when changing the export contract. Verify numeric attributes and source loading separately from geometry simplification. Preserve annual missingness; absent indicator rows remain unavailable. Density change retains the website's percentage presentation while the research package also saves absolute change.

Obrasgov displays the reviewed location derivative as points and lines only. `code/scripts/build_obras_web_map.py` requires the completed national QA/state-filter pipeline, preserves original public fields, validates its GeoPackage exchange, and writes a source-hash-derived archive and `data/obras-location.json`. The archive contains 224,495 components; 392 retained locations still require review. [Publication evidence](../docs/website-location-update.md) documents verification. Polygon components and excluded locations remain in research archives but have no rendering or picking layer. Counts and investment summaries describe source records, including excluded polygon records. IBAMA polygons and census/community areas retain their display behavior. See [the spatial review](../docs/obrasgov-spatial-review.md).
