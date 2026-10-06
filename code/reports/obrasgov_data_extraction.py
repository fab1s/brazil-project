# %% [markdown]
# ---
# title: "Obrasgov.br Data"
# format:
#   html: default
#   gfm: default
# editor: visual
# jupyter: python3
# ---
#
# ## Data Extraction
#
# %%
#| label: obrasgov_data_extraction_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
project = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "project.toml").exists())
ctx = Context(project / "project.toml")
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 1)

# %% [markdown]
#
# First we retrieve all projects.
#
# %%
#| label: obrasgov_data_extraction_2
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 2)

# %% [markdown]
#
# Then we transform the nested tables into columns.
#
# %%
#| label: obrasgov_data_extraction_3
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 3)

# %% [markdown]
#
# The Obrasgov API only allows for the extraction of point geometries. In order to enrich the dataset with multidimensional geometries we have to resort to another endpoint. Using Obrasgovr we first extract the geo-data metadata to identify which geometries are potentially multidimensional.
#
# %%
#| label: obrasgov_data_extraction_4
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 4)

# %% [markdown]
#
# With the filtered IDs, we extract the full geometries.
#
# %%
#| label: obrasgov_data_extraction_5
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 5)

# %% [markdown]
#
# %%
#| label: obrasgov_data_extraction_6
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 6)

# %% [markdown]
#
# ::: callout-note
# - Metadata can be extracted for the individual geometries. For now, geometries were merged by project ID.
# :::
#
# We then join both tables and end up with the final data set for further manipulation.
#
# %%
#| label: obrasgov_data_extraction_7
show_chunk(ctx, 'Scripts_Data/Obrasgov/Obrasgov - Data Extraction.qmd', 7)

# %% [markdown]
