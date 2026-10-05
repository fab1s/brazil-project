# Compare Python to the current original R calculations using only local copied inputs.
args <- commandArgs(trailingOnly=TRUE)
root <- normalizePath(args[[1]])
code <- if (length(args)>1L) args[[2]] else "3106200"
if (!grepl("^[0-9]+$",code)) stop("Municipality must be numeric")
source(file.path(root,"scripts/r/bootstrap.R"))
suppressPackageStartupMessages({library(sf);library(dplyr);library(readr);library(arrow);library(ggplot2);library(tidyr)})
base <- file.path(root,"data/intermediate",paste0("municipality_",code))
reference <- file.path(base,"r_reference")
dir.create(reference,recursive=TRUE,showWarnings=FALSE)
setwd(reference)
if (file.exists("reference_status.txt")) unlink("reference_status.txt")
# Restrict cached inputs identically to the explicitly selected validation scope.
read_local <- function(year,dataset) {
  path <- file.path(root,"data/raw/ibge/census",paste0(year,"_tracts_",dataset,"_v0.5.0.parquet"))
  requested_ids <- as.character(if (year == 2010) unique(lookup_2010$id_2010) else unique(lookup_2022$id_2022))
  arrow::open_dataset(path) |> filter(code_tract %in% requested_ids) |> collect()
}
lookup_path <- file.path(root,"data/processed/ibge/Data/lookup.gpkg")
where <- function(id) paste0("CAST(\"",id,"\" AS TEXT) LIKE '",code,"%'")
lookup_2010 <- st_read(lookup_path,layer="2010",quiet=TRUE)
lookup_2022 <- st_read(lookup_path,layer="2022",quiet=TRUE)
base_geom_2022 <- st_read(file.path(root,"data/processed/ibge/Data/base_geometry_2022.gpkg"),query=paste0('SELECT * FROM "base_geometry_2022" WHERE ',where("id_2022")),quiet=TRUE)
selected_ids <- unique(base_geom_2022$common_id)
lookup_2010 <- filter(lookup_2010,common_id %in% selected_ids)
lookup_2022 <- filter(lookup_2022,common_id %in% selected_ids)
base_geom_2022 <- st_read(file.path(root,"data/processed/ibge/Data/base_geometry_2022.gpkg"),query=paste0("SELECT * FROM base_geometry_2022 WHERE common_id IN (",paste(selected_ids,collapse=","),")"),quiet=TRUE)
group_sizes <- read_csv(file.path(root,"data/raw/ibge/Data/group_sizes.csv"),show_col_types=FALSE) |> filter(common_id %in% lookup_2022$common_id)
census_data_2010_pessoa <- read_local(2010,"Pessoa")
census_data_2010_domicilio <- read_local(2010,"Domicilio")
census_data_2022_basico <- read_local(2022,"Basico")
census_data_2022_pessoas <- read_local(2022,"Pessoas")
census_data_2022_domicilios <- read_local(2022,"Domicilio")
census_data_2010_responsavelrenda <- read_local(2010,"ResponsavelRenda")
census_data_2022_responsavelrenda <- read_local(2022,"ResponsavelRenda")
inflation_factor <- 6645.74/3200.06
chunks <- function(path) {
  lines <- readLines(path,warn=FALSE)
  result <- list(); inside <- FALSE; label <- ""; code_lines <- character()
  for (line in lines) {
    if (!inside && grepl('^```\\{r',line)) {
      inside <- TRUE;label <- sub('^```\\{r ?([^}]*)\\}.*$','\\1',line);code_lines <- character()
    } else if (inside && grepl('^```$',line)) {
      result[[length(result)+1L]] <- list(label=label,code=paste(code_lines,collapse="\n"));inside <- FALSE
    } else if (inside) code_lines <- c(code_lines,line)
  }
  result
}
original <- file.path(root,"archive/original_code/Scripts_Data/IBGE/IBGE Census - Temporal Comparison.qmd")
for (chunk in chunks(original)) {
  if (chunk$label %in% c("libraries","data_import","save")) next
  cat("Reference chunk",chunk$label,"\n")
  eval(parse(text=chunk$code),envir=.GlobalEnv)
}
for (name in ls(envir=.GlobalEnv)) {
  value <- get(name,envir=.GlobalEnv)
  if (is.data.frame(value) && (grepl('_common$',name) || grepl('_change$',name) || name %in% c("brown_sf","black_brown_sf"))) {
    write.csv(st_drop_geometry(value),paste0(name,".csv"),row.names=FALSE,na="")
  }
}
chart_path <- file.path(root,"archive/original_code/CS2Nordic/Brazil Poroject - Charts.qmd")
for (chunk in chunks(chart_path)) eval(parse(text=chunk$code),envir=.GlobalEnv)
for (name in c("chart_data","chart_data_2022","year_summary","income_box_data")) write.csv(get(name),paste0(name,".csv"),row.names=FALSE,na="")
write.csv(data.frame(income_cutoff=income_cutoffs),"income_cutoffs.csv",row.names=FALSE)

writeLines("completed",file.path(reference,"reference_status.txt"))
