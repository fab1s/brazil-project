# WHY: retain sf/S2 geographic intersection semantics until Python equivalence is verified.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==4L)
root <- normalizePath(args[[1]])
source(file.path(root,"code/scripts/r/bootstrap.R"))
suppressPackageStartupMessages({library(sf);library(dplyr)})
source(file.path(root,"code/scripts/r/spherical_intersections.R"))
path <- args[[2]]
out <- args[[3]]
code <- args[[4]]
if (!grepl("^[0-9]+$",code)) stop("Municipality must be numeric")
dir.create(out,recursive=TRUE,showWarnings=FALSE)
read_year <- function(year) {
  layer <- if (year==2000) "2000_urban" else as.character(year)
  st_read(path,query=paste0('SELECT * FROM "',layer,'" WHERE CAST(code_tract AS TEXT) LIKE \'',code,'%\''),quiet=TRUE)
}
old <- read_year(2000)
for (year in c(2010,2022)) {
  newer <- read_year(year)
  old_selected <- old |> select(code_tract_2000=code_tract)
  newer_selected <- newer |> select(code_tract_new=code_tract)
  intersections <- indexed_intersections(old_selected,newer_selected)
  cat("Computed",nrow(intersections),"spherical overlaps for",year,"\n")
  areas <- newer_selected
  areas$area_new <- st_area(st_geometry(areas))
  areas <- st_drop_geometry(areas)
  comparisons <- intersections
  comparisons$area_intersection <- st_area(st_geometry(intersections))
  comparisons <- comparisons |>
    left_join(areas,by="code_tract_new",relationship="many-to-many") |>
    mutate(overlap_pct=as.numeric(area_intersection/area_new))
  summary <- comparisons |> st_drop_geometry() |> group_by(code_tract_2000) |>
    summarise(n=n(),over5pct=sum(overlap_pct>0.05),minimum=min(overlap_pct),maximum=max(overlap_pct),total=sum(overlap_pct),.groups="drop") |>
    mutate(change_type=case_when(over5pct==1 & maximum>0.95 ~ "stable",over5pct==1 ~ "reshaped",over5pct>1 ~ "split",TRUE ~ "unmatched"))
  dest <- file.path(out,paste0("intersections_2000_",year,".gpkg"))
  temporary <- paste0(dest,".tmp.gpkg")
  if(file.exists(temporary)) unlink(temporary)
  comparisons$area_intersection <- as.numeric(comparisons$area_intersection)
  comparisons$area_new <- as.numeric(comparisons$area_new)
  st_write(comparisons,temporary,layer="intersections",quiet=TRUE)
  if (!file.rename(temporary,dest)) stop("Cannot publish intersections")
  write.csv(summary,file.path(out,paste0("change_summary_2000_",year,".csv")),row.names=FALSE)
}
