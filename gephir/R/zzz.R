# Package-level environment for Python module references
.gephi <- new.env(parent = emptyenv())
.gephi$initialized <- FALSE

.onLoad <- function(libname, pkgname) {
  # Delay-load: modules are imported on first use via gephi_init()
  invisible()
}

.onAttach <- function(libname, pkgname) {
  packageStartupMessage(
    "gephir ", utils::packageVersion("gephir"),
    " - R interface to Gephi graph toolkit\n",
    "Call gephi_init() to initialize the Python bridge."
  )
}

.check_init <- function() {
  if (!.gephi$initialized) {
    stop("gephi-cli not initialized. Call gephi_init() first.", call. = FALSE)
  }
}
