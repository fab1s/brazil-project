root <- normalizePath(getwd())
# Run from the project root; never install into an unisolated global library.
if (!requireNamespace("renv", quietly = TRUE)) {
  bootstrap <- file.path(getwd(), "renv/bootstrap")
  dir.create(bootstrap, recursive = TRUE, showWarnings = FALSE)
  install.packages("renv", lib = bootstrap, repos = "https://cloud.r-project.org")
  .libPaths(c(bootstrap, .libPaths()))
}
source(file.path(root,"scripts/r/bootstrap.R"))
renv::restore(project = root, prompt = FALSE)
