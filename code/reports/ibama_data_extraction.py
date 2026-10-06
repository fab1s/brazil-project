# %% [markdown]
# ---
# title: "IBAMA - Data Extraction"
# format:
#   html: default
#   gfm: default
# editor: visual
# jupyter: python3
# ---
#
# %%
#| label: ibama_data_extraction_1
from pathlib import Path
from brazil_project.io import Context
from brazil_project.reporting import show_chunk
project = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "project.toml").exists())
ctx = Context(project / "project.toml")
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 1)

# %% [markdown]
#
# We will extract three layers separately containing point, line and polygon geometries from the [PAMGIA](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO) endpoint:
#
# - tb_empreendimento_repr_p
#
# - tb_empreendimento_repr_l
#
# - tb_empreendimento_repr_a
#
# %%
#| label: ibama_data_extraction_2
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 2)

# %% [markdown]
#
# %%
#| label: ibama_data_extraction_3
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 3)

# %% [markdown]
#
# %%
#| label: ibama_data_extraction_4
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 4)

# %% [markdown]
#
# %%
#| label: ibama_data_extraction_5
show_chunk(ctx, 'Scripts_Data/IBAMA/IBAMA - Data Extraction.qmd', 5)

# %% [markdown]
