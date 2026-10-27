# Interactive map source

The live [Brazil project map](https://sandy-ivory-k65c.here.now/) is separate from the four dataset notebooks. This folder contains its HTML, JavaScript, CSS, pinned browser libraries, licenses, and a preview image.

The full tile archives and generated indexes are local outputs, not GitHub files. Running a notebook produces a GeoPackage; it does not rebuild or publish this website. The map simplifies or tiles geography for display, so use the GeoPackages in `datasets/` for analysis. The current frozen IBAMA tiles contain 8,492 of 8,494 source IDs; all 12,348 community IDs appear in the frozen community tiles. Exact tile attributes and geometry have not been fully compared.

Website build and publication history is preserved on the [archive branch](https://github.com/fab1s/brazil-project/tree/archive/full-project-2026-10-27).
