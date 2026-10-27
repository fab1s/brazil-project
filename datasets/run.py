"""Build one of the four final GeoPackages without opening Jupyter."""

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
    sys.path.insert(0, str(root / "code"))
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
