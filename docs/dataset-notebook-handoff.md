# Final dataset notebook process and audit

Status: implemented; local software verification complete
Last updated: 2026-10-26
Version: 0.1
Scope: Four readable national GeoPackage workflows for collaborator handoff

## What was built

The [dataset entry point](../datasets/README.md) has one folder per requested dataset. Each folder contains a short README, a runnable `build.ipynb`, adjacent `processing.py`, and an ignored, verified local `final.gpkg` copy after a successful build. The notebooks show code, small tables and figures on GitHub. Their default is a full local build; saved outputs were generated in the explicitly labeled `BRAZIL_NOTEBOOK_REBUILD=0` preview mode. The preview does **not** establish a new processing run.

| Dataset | Inputs and provenance | Build decision | Final local output |
| --- | --- | --- | --- |
| Census | National versioned harmonisation bundle; configured 2010/2022 census inputs; saved indicator contracts; original map-field functions | Run `indicators`; prepare the same full-resolution merged areas and display overview; export English fields with the original-code dictionary. No tile publishing. | `datasets/census/final.gpkg`, copied from `outputs/maps/notebook-exports/social.gpkg` (`social`, `overview`, `field_dictionary`, `export_metadata`) |
| Obrasgov | Preserved local project snapshot; pinned municipality/land/coast references; approved location and state rules | Run the existing combined command. Keep original rows; export only eligible point/line components and a separate state-exclusion layer. | `datasets/obrasgov/final.gpkg`, copied from `outputs/maps/obrasgov-primary-state-filter/locations.gpkg` |
| IBAMA | Inventoried preserved local licensing GeoPackage | Rerun active sector translation; require exact baseline attributes, CRS, order and WKB; copy baseline bytes after parity. | `datasets/ibama/final.gpkg`, copied from `outputs/maps/notebook-exports/ibama.gpkg` |
| Communities | Inventoried IBGE 2022 community GeoPackage | Require matching size and SHA-256, valid GeoPackage, EPSG:4674 and unique `cd_fcu`; copy bytes unchanged. | `datasets/communities/final.gpkg`, copied from `outputs/maps/notebook-exports/communities.gpkg` |

All source files remain in their original project locations. Full datasets, generated exports, notebook checkpoints and local `final.gpkg` copies are excluded from Git. The external census comparison copy is unchanged. No automatic acquisition or here.now publication occurs.

## Execution and verification

Run a notebook's cells from its folder in the locked project environment. For a read-only saved-output preview, set `BRAZIL_NOTEBOOK_REBUILD=0`; this mode is used only to save small GitHub-visible tables and figures. The `.ipynb` files have been executed in fresh Jupyter kernels and contain no cell errors. One first attempt in the restricted environment could not open Jupyter's local kernel socket; the authorized local-kernel run succeeded. The notebook results show area/component/source-feature counts, sector/state distributions and the reviewed Obrasgov before/after figure.

The complete census default build ran harmonisation and indicators, rebuilt the source map GeoPackage, then exported **287,178** `social` areas, **5,570** overview rows and **187** dictionary mappings. Streaming comparison against an earlier reviewed external comparison copy found **exact row equality** in all three data layers, including attributes and GeoPackage geometry blobs. The whole-file SHA differs because each `export_metadata` table includes run-specific provenance; this is not a numerical or geometry difference. IBAMA translation and copy reproduced all **8,494** preserved records and the baseline SHA-256. Communities copied all **12,348** polygons with the baseline SHA-256. The new focused notebook tests cover notebook structure/output, duplicate-key/CRS rejection and protection of unrelated local files.

The full `brazil-project run obrasgov --config project.toml` path also completed from the preserved local snapshot. It regenerated **224,495** eligible point/line components and **2,346** primary-state exclusions, with a completed producer report and matching GeoPackage hash. The default-build path of the community notebook was executed in a fresh Jupyter kernel; all four GitHub preview notebooks were executed in separate fresh kernels. The documented `jupyter nbconvert` preview command succeeded. The full Python suite passed **205 tests**. [Machine-readable output and notebook fingerprints](evidence/dataset-notebook-handoff.json) record the local result files, layer counts and saved previews.

All four `datasets/*/final.gpkg` files are regular local files, not links. Their sizes and SHA-256 values exactly match their producer GeoPackages. They are excluded from Git while remaining usable if an individual dataset folder is transferred with its binary included.

The saved census, Obrasgov, IBAMA and community charts were visually inspected. The census plot now uses plain-language relationship labels; the Obrasgov map still distinguishes the 1,485 newly excluded **points** from the 2,346 exclusions across all geometry components.

An optional read-only ID comparison used the locally saved **highest-zoom** website archives. All **12,348** community source IDs occur in the community tiles. The IBAMA archive contains **8,492 of 8,494** source `objectid` values; `136441` and `3347413` are absent, with no tile-only IDs. Source geometry and records remain untouched. Repeated tile fragments are deduplicated by ID; this comparison does not certify tile geometry or attributes or establish why those two records were omitted.

![Obrasgov retained point locations before and after the approved primary-state rule](assets/obrasgov-primary-state-filter.png)

Generated by `brazil-project run obrasgov --config project.toml` through the existing filter script. The figure illustrates original eligible **points** before and after the state rule; lines, polygons and previously quarantined points are omitted. It is not a count of projects or investment. The reviewed documentation image and its checksum remain recorded in the [original exclusion audit](obrasgov-primary-state-filter.md).

## Script audit and remaining limits

- **Correctness and provenance:** Census invokes the active harmonisation/indicator logic and existing map-field functions; the English exporter verifies current bundle and indicator fingerprints before publication. Obrasgov consumes the unchanged approved stage chain and checks its completed GIS hash, policy, ID uniqueness and counts. IBAMA and communities require the baseline inventory before copying.
- **Output contracts and recovery:** Census and copied baselines stage complete files before atomic replacement. Each folder's `final.gpkg` is a checked byte copy, with an ignored local checksum receipt. An interrupted copy leaves the previous final file intact; if publication completes before its receipt, the next run repairs the receipt only after matching the source checksum. An unrelated edited final file is never overwritten. Obrasgov follows its existing producer recovery contract: require a completed report with matching artifact hashes after any interruption. Concurrent runs against the same stage outputs remain unsupported.
- **Research interpretation:** Notebook preview plots count areas, location components or source features; they are not population or investment totals. Map eligibility does not verify coordinates. The census boundary-change assumption remains explicit. Frozen website ID coverage is documented above, while tile-to-GeoPackage attribute/geometry parity is unverified; the map also quantises or simplifies some display geometry.
- **Software versus science:** Exact output/parity checks verify the implemented handoff and saved baselines; they do not independently validate source geocoding, census coverage assumptions or licensing interpretations.
