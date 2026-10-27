"""Build a final GeoPackage or copy four verified files for a collaborator.

Restore the configured local ``data/`` inputs first; their paths are in
``datasets/project.toml``. The baseline inventory is preserved on the
``archive/full-project-2026-10-27`` branch. Neither this command nor the
notebooks download source data or publish the website.

From the repository root::

    python3 -m venv .venv
    .venv/bin/python -m pip install -r datasets/requirements.lock
    .venv/bin/python datasets/run.py census

Use ``obrasgov``, ``ibama``, or ``communities`` in place of ``census``.
The command executes that dataset's build.ipynb in a fresh kernel and saves its
tables and figures after all cells and final-file checks pass. Add --from-saved
to refresh evidence from existing verified outputs without processing. The
output is a descriptively named GeoPackage in datasets/<name>/. To copy all four
verified files into one folder::

    .venv/bin/python datasets/run.py handoff --output-dir /path/to/handoff

The handoff verifies the final files, their producer receipts and the copied
bytes. It does not remove other files from the chosen directory. If interrupted,
run it again; copies already matching their sources are skipped.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile

from _shared import FINAL_FILENAMES


HANDOFF = {
    "census": (FINAL_FILENAMES["census"], "comparison_areas", 5880, "common_id",
               ("overview", "field_dictionary", "export_metadata")),
    "obrasgov": (FINAL_FILENAMES["obrasgov"], "map_components", 4674,
                 "component_id", ("excluded_primary_state", "field_dictionary", "export_metadata")),
    "ibama": (FINAL_FILENAMES["ibama"], "licensed_projects_st", 4674,
              "record_id", ("field_dictionary", "export_metadata")),
    "communities": (FINAL_FILENAMES["communities"], "favelas_2022", 4674,
                    "community_code", ("field_dictionary", "export_metadata")),
}


def checked_final(root, dataset, specification):
    """Require a current producer receipt and the expected GeoPackage schema."""
    from _shared import baseline_checksum, geopackage_summary, sha256

    folder = root / "datasets" / dataset
    final = folder / specification[0]
    receipt = json.loads((folder / ".final-gpkg.json").read_text())
    expected = receipt.get("sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"{dataset}: missing final-file checksum receipt")
    producer = (folder / receipt["source"]).resolve(strict=True)
    if not producer.is_relative_to(root.resolve()):
        raise ValueError(f"{dataset}: producer is outside the project")
    _, layer, epsg, key, other_layers = specification
    summary = geopackage_summary(final, layer, expected_crs=epsg, unique_key=key)
    if summary["sha256"] != expected or sha256(producer) != expected:
        raise ValueError(f"{dataset}: final file differs from its checked producer")
    with sqlite3.connect(f"file:{final}?mode=ro", uri=True) as connection:
        layers = {row[0] for row in connection.execute("SELECT table_name FROM gpkg_contents")}
    if not set(other_layers).issubset(layers):
        raise ValueError(f"{dataset}: a required GeoPackage layer is missing")
    if dataset == "census" and "social" in layers:
        raise ValueError("census: obsolete social layer remains in the final GeoPackage")
    if dataset != "census":
        from english_export import verify_export
        sources = {
            "obrasgov": root / "outputs/maps/obrasgov-primary-state-filter/locations.gpkg",
            "ibama": root / "data/processed/ibama/licensed_projects_st.gpkg",
            "communities": root / "data/processed/ibge/Data/favelas_2022.gpkg",
        }
        source = sources[dataset]
        if dataset in ("ibama", "communities"):
            baseline_checksum(root, source)
        else:
            report = json.loads((root / "data/intermediate/obrasgov-primary-state-filter/report.json").read_text())
            if report.get("status") != "completed" or report.get("gis_outputs", {}).get("locations.gpkg") != sha256(source):
                raise ValueError("Obrasgov handoff producer differs from its completed filter report")
        verify_export(source, final, dataset, sha256(source))
    return final, summary


def handoff(root, output_dir):
    """Stage and verify every copy before publishing any named handoff file."""
    from _shared import sha256

    output_dir = Path(output_dir).expanduser().resolve()
    if not output_dir.is_dir():
        raise NotADirectoryError(f"Handoff directory does not exist: {output_dir}")
    sources = {name: checked_final(root, name, spec)
               for name, spec in HANDOFF.items()}
    result = {}
    present_names = {entry.name for entry in output_dir.iterdir()}
    with tempfile.TemporaryDirectory(prefix=".brazil-handoff-", dir=output_dir) as temporary:
        staged = {}
        for name, (filename, *_rest) in HANDOFF.items():
            source, summary = sources[name]
            target = output_dir / filename
            # A case-insensitive filesystem can resolve an old spelling as this target.
            if target.exists() and filename not in present_names:
                raise FileExistsError(f"Case-only filename collision; move the old file first: {target}")
            if target.is_symlink():
                raise ValueError(f"Refusing to replace a symlink: {target}")
            if target.exists() and not target.is_file():
                raise ValueError(f"Handoff destination is not a file: {target}")
            if target.is_file() and sha256(target) == summary["sha256"]:
                result[name] = {"file": str(target), "sha256": summary["sha256"],
                                "features": summary["features"], "status": "already_current"}
                continue
            candidate = Path(temporary) / filename
            shutil.copyfile(source, candidate)
            if sha256(candidate) != summary["sha256"] or sha256(source) != summary["sha256"]:
                raise ValueError(f"{name}: handoff copy failed checksum verification")
            staged[name] = candidate
        for name, candidate in staged.items():
            filename = HANDOFF[name][0]
            target = output_dir / filename
            os.replace(candidate, target)
            summary = sources[name][1]
            result[name] = {"file": str(target), "sha256": summary["sha256"],
                            "features": summary["features"], "status": "copied"}
    return result


def execute_notebook(root, dataset, from_saved=False):
    """Execute the same ordered cells a reader runs, then save results atomically."""
    import nbformat
    from nbclient import NotebookClient

    folder = root / 'datasets' / dataset
    path = folder / 'build.ipynb'
    lock = folder / '.build.ipynb.lock'
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise RuntimeError('Notebook is already running, or an interrupted run left ' + str(lock) +
                           '. Remove that lock only after confirming no run is active.') from error
    os.close(descriptor)
    staged = None
    try:
        source = path.read_bytes()
        notebook = nbformat.reads(source.decode(), as_version=4)
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                cell.metadata.setdefault('jupyter', {})['source_hidden'] = True
                cell.metadata['jupyter'].pop('outputs_hidden', None)
                cell.metadata.pop('collapsed', None)
        nbformat.validate(notebook)
        environment = os.environ.copy()
        environment['BRAZIL_NOTEBOOK_FROM_SAVED'] = '1' if from_saved else '0'
        def progress(cell, cell_index):
            if cell.cell_type != 'code':
                return
            heading = 'Setup'
            for previous in reversed(notebook.cells[:cell_index]):
                lines = [line.strip('# ') for line in previous.source.splitlines() if line.startswith('## ')]
                if lines:
                    heading = lines[0]
                    break
            print('  ' + heading, flush=True)
        # CONTRACT: Each notebook gets its own kernel and its own working folder.
        NotebookClient(notebook, timeout=7200, kernel_name='python3',
                       resources={'metadata': {'path': str(folder)}}, on_cell_start=progress).execute(env=environment)
        checked_final(root, dataset, HANDOFF[dataset])
        for cell in notebook.cells:
            for output in cell.get('outputs', []):
                if output.output_type == 'stream':
                    output.text = output.text.replace(str(root) + os.sep, '')
        nbformat.validate(notebook)
        if path.read_bytes() != source:
            raise RuntimeError('Notebook source changed during execution; saved results were preserved.')
        with tempfile.NamedTemporaryFile(prefix='.build-', suffix='.ipynb', dir=folder, delete=False) as stream:
            staged = Path(stream.name)
        nbformat.write(notebook, staged)
        if path.read_bytes() != source:
            raise RuntimeError('Notebook source changed before publication; saved results were preserved.')
        os.replace(staged, path)
        return path
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset", choices=(*HANDOFF, "handoff"))
    parser.add_argument("--output-dir", type=Path, help="Existing directory for named handoff copies")
    parser.add_argument('--from-saved', action='store_true', help='Refresh notebook evidence from verified local outputs without processing')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    if args.dataset == "handoff":
        if args.from_saved:
            parser.error('--from-saved applies to dataset notebooks, not handoff')
        if args.output_dir is None:
            parser.error("handoff requires --output-dir")
        sys.path.insert(0, str(root / "datasets"))
        print(json.dumps(handoff(root, args.output_dir), indent=2))
        return
    if args.output_dir is not None:
        parser.error("--output-dir is only used with handoff")
    sys.path.insert(0, str(root / "datasets" / "shared"))
    cache = root / ".cache" / "matplotlib"
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache))
    sys.path.insert(0, str(root / "datasets"))
    print('Executing ' + args.dataset + ' notebook', flush=True)
    print('Updated ' + str(execute_notebook(root, args.dataset, args.from_saved).relative_to(root)))


if __name__ == "__main__":
    main()
