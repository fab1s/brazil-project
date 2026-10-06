# %% [markdown]
# ---
# title: "IBGE Census - Data Extraction"
# format:
#   html: default
#   gfm: default
# editor: visual
# jupyter: python3
# ---
#
# %%
#| label: ibge_census_data_extraction_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
project = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "project.toml").exists())
ctx = Context(project / "project.toml")
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 1)

# %% [markdown]
#
# %%
#| label: ibge_census_data_extraction_2
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 2)

# %% [markdown]
#
# %%
#| label: ibge_census_data_extraction_3
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 3)

# %% [markdown]
#
# ### Black population ratio
#
# %%
#| label: ibge_census_data_extraction_4
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 4)

# %% [markdown]
#
# %%
#| label: ibge_census_data_extraction_5
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 5)

# %% [markdown]
#
# %%
#| label: ibge_census_data_extraction_6
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE Census - Data Extraction.qmd', 6)

# %% [markdown]
