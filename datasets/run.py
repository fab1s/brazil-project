"""Build one of the four final GeoPackages without opening Jupyter.

Restore the configured local ``data/`` inputs first; their paths are in
``datasets/project.toml``. The baseline inventory is preserved on the
``archive/full-project-2026-10-27`` branch. Neither this command nor the
notebooks download source data or publish the website.

From the repository root::

    python3 -m venv .venv
    .venv/bin/python -m pip install -r datasets/requirements.lock
    .venv/bin/python datasets/run.py census

Use ``obrasgov``, ``ibama``, or ``communities`` in place of ``census``.
The output is the local ``datasets/<name>/final.gpkg``; transfer it separately
from GitHub and compare its SHA-256 with the value in the dataset notebook.
"""

import argparse
import importlib.util
import os
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=("census", "obrasgov", "ibama", "communities"))
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    folder = root / "datasets" / args.dataset
    sys.path.insert(0, str(root / "datasets" / "shared"))
    cache = root / ".cache" / "matplotlib"
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache))
    sys.path.insert(0, str(root / "datasets"))
    spec = importlib.util.spec_from_file_location("dataset_processing", folder / "processing.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(module.build(root))


if __name__ == "__main__":
    main()
