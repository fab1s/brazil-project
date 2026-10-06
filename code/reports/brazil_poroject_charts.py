# %% [markdown]
# ---
# title: "Brazil Poroject - Charts"
# format:
#   html: default
#   gfm: default
# editor: visual
# jupyter: python3
# ---
#
# %%
#| label: brazil_poroject_charts_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
project = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "project.toml").exists())
ctx = Context(project / "project.toml")
show_chunk(ctx, 'CS2Nordic/Brazil Poroject - Charts.qmd', 1)

# %% [markdown]
