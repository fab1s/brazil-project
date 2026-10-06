# %% [markdown]
# ---
# title: "IBGE Dataset Overview"
# format:
#   html: default
#   gfm: default
# editor: visual
# jupyter: python3
# ---
#
# This code compares census tract boundaries from 2000, 2010, and 2022 in Belo Horizonte. It measures how much the areas overlap and classifies older tracts as stable, reshaped, split, or unmatched. It then visualizes examples of these changes and compares the share of the Black population in 2010 and 2022.
#
# %%
#| label: ibge_dataset_overview_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
project = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "project.toml").exists())
ctx = Context(project / "project.toml")
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 1)

# %% [markdown]
#
# %%
#| label: ibge_dataset_overview_2
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 2)

# %% [markdown]
#
# %%
#| label: ibge_dataset_overview_3
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 3)

# %% [markdown]
#
# # Census Tract
#
# ## Overlap Analysis
#
# %%
#| label: ibge_dataset_overview_4
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 4)

# %% [markdown]
#
# %%
#| label: ibge_dataset_overview_5
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 5)

# %% [markdown]
#
# ### 2000 -\> 2010
#
# %%
#| label: ibge_dataset_overview_6
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 6)

# %% [markdown]
#
# ### 2000 -\> 2022
#
# %%
#| label: ibge_dataset_overview_7
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 7)

# %% [markdown]
#
# ### Visualization - Change Types
#
# **Split**
#
# %%
#| label: ibge_dataset_overview_8
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 8)

# %% [markdown]
#
# %%
#| label: ibge_dataset_overview_9
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 9)

# %% [markdown]
#
# **Reshaped**
#
# %%
#| label: ibge_dataset_overview_10
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 10)

# %% [markdown]
#
# **Stable**
#
# %%
#| label: ibge_dataset_overview_11
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 11)

# %% [markdown]
#
# # Census Data
#
# ## Visualization - BH
#
# ### Black population ratio
#
# %%
#| label: ibge_dataset_overview_12
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 12)

# %% [markdown]
#
# %%
#| label: ibge_dataset_overview_13
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 13)

# %% [markdown]
#
# %%
#| label: ibge_dataset_overview_14
show_chunk(ctx, 'Scripts_Data/IBGE/IBGE - Dataset Overview.qmd', 14)

# %% [markdown]
