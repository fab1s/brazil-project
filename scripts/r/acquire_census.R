# WHY: censobr/geobr retain their versioned source selection and metadata behavior.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L)
root <- normalizePath(args[[1]])
out <- args[[2]]
source(file.path(root,"scripts/r/bootstrap.R"))
for (p in c("censobr", "geobr", "arrow", "sf", "jsonlite")) {
  if (!requireNamespace(p, quietly = TRUE)) stop(paste("Restore missing package", p))
}
dir.create(out, recursive = TRUE, showWarnings = FALSE)
for (year in c(2000, 2010, 2022)) {
  datasets <- switch(as.character(year), `2000` = "Basico", `2010` = c("Pessoa", "Domicilio", "ResponsavelRenda"), `2022` = c("Basico", "Pessoas", "Domicilio", "ResponsavelRenda"))
  for (dataset in datasets) {
    dest <- file.path(out, paste0(year, "_tracts_", dataset, "_v0.5.0.parquet"))
    if (file.exists(dest)) next
    value <- censobr::read_tracts(year = year, dataset = dataset, as_data_frame = TRUE)
    if (!"code_tract" %in% names(value) || anyNA(value$code_tract) || anyDuplicated(value$code_tract)) stop("Invalid census keys")
    arrow::write_parquet(value, paste0(dest, ".tmp"))
    if (!file.rename(paste0(dest, ".tmp"), dest)) stop("Cannot publish acquired input")
  }
}
# Boundary acquisition is isolated from routine processing and only fills absent inputs.
tract_path <- file.path(root, "data/raw/ibge/Data/ibge_census_tracts.gpkg")
if (!file.exists(tract_path)) {
  dir.create(dirname(tract_path), recursive = TRUE, showWarnings = FALSE)
  temporary <- paste0(tract_path, ".tmp.gpkg")
  for (year in c(2000, 2010, 2022)) {
    for (zone in if (year == 2000) c("urban", "rural") else "all") {
      value <- if (year == 2000) geobr::read_census_tract(year = year, code_tract = "all", zone = zone) else geobr::read_census_tract(year = year, code_tract = "all")
      layer <- if (year == 2000) paste0(year, "_", zone) else as.character(year)
      sf::st_write(value, temporary, layer = layer, quiet = TRUE)
    }
  }
  if (!file.rename(temporary, tract_path)) stop("Cannot publish acquired boundaries")
}
jsonlite::write_json(list(packages = c(censobr = as.character(packageVersion("censobr")), geobr = as.character(packageVersion("geobr"))), acquired_at = format(Sys.time(), tz = "UTC")), file.path(out, "acquisition_provenance.json"), pretty = TRUE, auto_unbox = TRUE)
