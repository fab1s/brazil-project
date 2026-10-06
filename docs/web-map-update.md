# Here.now Merged-Area Map Verification

Status: published; local and live verification passed
Last updated: 2026-10-06
Version: 0.2
Scope: Existing here.now map updated from the approved national harmonisation bundle

The updated map uses 287,178 complete merged common areas rather than repeated values on individual tract pieces. Original reference geometry remains available in the research bundle; the active census tiles, popup identifiers, and summaries use common IDs. The existing Rio opening view, basemaps, desktop/mobile controls, project and community layers, timeline, and all 13 indicators are retained.

## Checks

| Check | Result |
| ---- | ------ |
| Common-area export | 287,178 rows and 287,178 unique common IDs |
| Research attribute parity | All 13 indicators match source tables exactly after existing presentation exclusions |
| Income | 279,962 groups have available real percentage change; source means, weights, coverage, and changes retained |
| Unavailable groups | Missing indicator rows retain geometry and unavailable estimates; no invented zeros |
| Municipal overview | 5,570 features; complete groups counted once per municipality touched by 2022 tracts |
| PMTiles | 17 archives have valid MVT headers and the `social` source layer |
| Browser rendering | Overview, mid, and detail tiers render; density percentage change and income work |
| Popups and search | Popups identify common areas and contributing tract counts; numeric common-ID search works |
| Coverage summary | Shows unmatched 2010/2022 counts, known excluded population/household totals, and missing values |
| Desktop and mobile | Rendered screenshots inspected; existing controls remain usable |
| Preserved assets | Obrasgov, IBAMA, favelas, project statistics, and timeline hashes match the previous publication |
| Repeat build | Prepared database fingerprints verified; existing regional archives reused and overview rebuilt |
| Python tests | All 36 tests pass, including five focused web-map tests |

The browser reads the current census manifest without cache and uses its input-derived archive suffix and measured regional bounds. Updated modules and JSON requests avoid stale versions. A zoom-transition loading guard was corrected: basemap tile loading no longer prevents adding the next census tier. Common-area search also supports member-derived `g_` identifiers, covered by a focused test; the current national baseline retains numeric IDs.

## Research interpretation and limits

Municipality overview estimates include complete groups crossing their boundaries. They are summaries of contributing comparison areas, not clipped within-boundary counts. Nationwide summaries count each group once. Regional archives can contain the same complete group near state borders; popup selection deduplicates by common ID.

Tile clipping, simplification, and quantisation are display operations. The density denominator is the research bundle's saved equal-area value, and the map retains its prior percentage-change presentation. Original raw geometry and absolute density changes remain in the research outputs. The accepted boundary-change assumption is disclosed in the map; habitation data have not independently verified it.

Infrastructure/community assets were preserved from the existing site rather than replaced with a different research snapshot. No new live data acquisition or scientific publication review is implied. Full national geometric recomputation remains unbenchmarked.

Machine-readable checks, archive hashes, source fingerprints, browser results, and publication details are in [web-map-update-evidence.json](evidence/web-map-update-evidence.json). See [the maintained workflow](web-map.md) for rebuild and update commands.

## Publication

The existing [here.now map](https://sandy-ivory-k65c.here.now/) was updated permanently in the saved account. Published version: `01M465TDBFC8ZXMSKM92V7HRJT`. All 121 published file hashes match the local build. Live browser checks render overview, mid, and detailed census layers, common-ID search, summaries, income, density change, and mobile controls with zero page errors or failed HTTP responses.
