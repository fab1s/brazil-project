"""Dispatch individual analytical stages; dataset notebooks own their order."""

import argparse
import os
import sys

from brazil_project.io import Context, WorkflowError


STAGES = (
    'harmonisation', 'indicators', 'ibama',
    "obrasgov-snapshot",
    "obrasgov-location-qa",
    "obrasgov-location-plot",
    "obrasgov-primary-state-check",
    "obrasgov-primary-state-filter",
)


def dispatch(ctx, stage):
    if stage == "harmonisation":
        from brazil_project.harmonisation.census import run
    elif stage == "indicators":
        from brazil_project.indicators.temporal import run
    elif stage in ("ibama", "obrasgov-snapshot"):
        from brazil_project.infrastructure.projects import run
        return run(ctx, "ibama" if stage == "ibama" else "obrasgov")
    elif stage == "obrasgov-location-qa":
        from brazil_project.infrastructure.location_qa import run
    elif stage == "obrasgov-location-plot":
        from scripts.plot_location_qa import run
    elif stage == "obrasgov-primary-state-check":
        from scripts.check_obras_primary_state import run
    elif stage == "obrasgov-primary-state-filter":
        from scripts.filter_obras_primary_state import run
    else:
        raise WorkflowError("Unknown dataset stage: " + stage)
    return run(ctx)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run",))
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--config", default="datasets/project.toml")
    args = parser.parse_args(argv)
    try:
        ctx = Context(args.config)
        if ctx.municipality:
            raise WorkflowError("The four final GeoPackages require national scope; clear project.municipality.")
        os.environ.setdefault("MPLCONFIGDIR", str(ctx.root / ".cache/matplotlib"))
        print("Running " + args.stage, flush=True)
        dispatch(ctx, args.stage)
        return 0
    except (WorkflowError, FileNotFoundError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
