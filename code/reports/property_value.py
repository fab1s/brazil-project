# %% [markdown]
# ---
# title: "Property value"
# format:
#   html: default
#   gfm: default
# editor: visual
# jupyter: python3
# ---
#
# %%
#| label: property_value_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
project = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "project.toml").exists())
ctx = Context(project / "project.toml")
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 1)

# %% [markdown]
#
# %%
#| label: property_value_2
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 2)

# %% [markdown]
#
# %%
#| label: property_value_3
show_chunk(ctx, 'Scripts_Data/Land value/Belo Horizonte/Property value.qmd', 3)

# %% [markdown]
