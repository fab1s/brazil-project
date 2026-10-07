library(sf)
library(tidyverse)
library(arcgislayers)

library(mapview)

## data extraction

sector_translation <- tibble(
  tp_setor = c("Transporte", "Energia", "Mineração", "Petróleo e Gás",
               "Outros", "Recursos Hídricos", "Nuclear/Radiativa"),
  tp_setor_en = c("Transportation", "Energy", "Mining", "Oil and Gas",
                  "Other", "Water Resources", "Nuclear/Radioactive")
)


# point
url <- "https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO/tb_empreendimento_repr_p/FeatureServer/16"

lyr <- arc_open(url)
point_geom <- arc_select(lyr)

point_geom <- point_geom |> 
  left_join(sector_translation, by = "tp_setor")

# line
url <- "https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO/tb_empreendimento_repr_l/FeatureServer/15"

lyr <- arc_open(url)
line_geom <- arc_select(lyr)

line_geom <- line_geom |> 
  left_join(sector_translation, by = "tp_setor")

# polygons
url <- "https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO/tb_empreendimento_repr_a/FeatureServer/14"

lyr <- arc_open(url)
poly_geom <- arc_select(lyr)

poly_geom <- poly_geom |> 
  left_join(sector_translation, by = "tp_setor")

## vizualization
pal <- c(
  "Transportation" = "#66C2A5", "Energy" = "#FC8D62", "Mining" = "#8DA0CB",
  "Oil and Gas" = "#E78AC3", "Other" = "#A6D854",
  "Water Resources" = "#FFD92F", "Nuclear/Radioactive" = "#E5C494"
)

mapview(point_geom, zcol = "objectid", col.regions = pal) +
  mapview(line_geom, zcol = "tp_setor_en", color = pal) +
  mapview(poly_geom, zcol = "tp_setor_en", col.regions = pal)

