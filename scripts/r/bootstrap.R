# CONTRACT: root is supplied by the caller; all libraries/caches stay inside the project.
Sys.setenv(RENV_PATHS_ROOT=file.path(root,".cache/renv"),
           RENV_PATHS_CACHE=file.path(root,".cache/renv/cache"),
           RENV_PATHS_LIBRARY=file.path(root,"renv/library"),
           RENV_PATHS_SANDBOX=file.path(root,".cache/renv/sandbox"),
           RENV_CONFIG_CONSENT="TRUE",
           RENV_CONFIG_SYNCHRONIZED_CHECK="FALSE",
           RENV_CONFIG_SANDBOX_ENABLED="FALSE")
.libPaths(c(file.path(root,"renv/bootstrap"),.libPaths()))
if (!requireNamespace("renv",quietly=TRUE)) stop("Run Rscript scripts/r/restore.R from the project root")
renv::load(root)
