# Numerical geometry-engine check on an explicit small scope; archived code is read-only.
args <- commandArgs(trailingOnly=TRUE)
root <- normalizePath(args[[1]])
code <- if(length(args)>1L) args[[2]] else "3106200"
if(!grepl("^[0-9]+$",code)) stop("Municipality must be numeric")
source(file.path(root,"code/scripts/r/bootstrap.R"))
suppressPackageStartupMessages({library(sf);library(dplyr);library(igraph)})
out <- file.path(root,"data/intermediate",paste0("municipality_",code),"harmonisation_reference")
dir.create(out,recursive=TRUE,showWarnings=FALSE)
path <- file.path(root,"data/raw/ibge/Data/ibge_census_tracts.gpkg")
read_year <- function(year) st_read(path,query=paste0('SELECT * FROM "',year,'" WHERE CAST(code_tract AS TEXT) LIKE \'',code,'%\''),quiet=TRUE)
census_tract_2010 <- read_year(2010)
census_tract_2022 <- read_year(2022)
lines <- readLines(file.path(root,"data/archive/original_code/Scripts_Data/IBGE/IBGE - Census tract harmonisation.qmd"),warn=FALSE)
start <- which(lines=='```{r harmonisation}')+1L
end <- which(seq_along(lines)>start & lines=='```')[1L]-1L
eval(parse(text=paste(lines[start:end],collapse="\n")))
write.csv(crosswalk,file.path(out,"crosswalk.csv"),row.names=FALSE)
write.csv(crosswalk_grouped,file.path(out,"crosswalk_grouped.csv"),row.names=FALSE)
st_write(base_geom_2022,file.path(out,"base.gpkg"),delete_dsn=TRUE,quiet=TRUE)
