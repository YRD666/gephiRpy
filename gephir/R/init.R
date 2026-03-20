#' Initialize gephi-cli Python bridge
#'
#' Must be called before using any other gephir function.
#' Loads the Python gephi_cli modules via reticulate.
#'
#' @param python Path to Python executable (NULL = auto-detect)
#' @param virtualenv Name of virtualenv to use (NULL = system Python)
#' @param conda Name of conda environment (NULL = don't use conda)
#' @return TRUE (invisibly) on success
#' @export
#'
#' @examples
#' \dontrun{
#' gephi_init()
#' gephi_init(python = "/usr/bin/python3")
#' gephi_init(virtualenv = "gephi-env")
#' }
gephi_init <- function(python = NULL, virtualenv = NULL, conda = NULL) {
  if (!is.null(python)) {
    reticulate::use_python(python, required = TRUE)
  } else if (!is.null(virtualenv)) {
    reticulate::use_virtualenv(virtualenv, required = TRUE)
  } else if (!is.null(conda)) {
    reticulate::use_condaenv(conda, required = TRUE)
  }

  tryCatch({
    .gephi$io_graph   <- reticulate::import("gephi_cli.io_graph")
    .gephi$layout     <- reticulate::import("gephi_cli.layout")
    .gephi$metrics    <- reticulate::import("gephi_cli.metrics")
    .gephi$filters    <- reticulate::import("gephi_cli.filters")
    .gephi$appearance <- reticulate::import("gephi_cli.appearance")
    .gephi$preview    <- reticulate::import("gephi_cli.preview")
    .gephi$generator  <- reticulate::import("gephi_cli.generator")
    .gephi$pipeline   <- reticulate::import("gephi_cli.pipeline")
    .gephi$core       <- reticulate::import("gephi_cli.core")
    .gephi$shortest   <- reticulate::import("gephi_cli.shortest_path")
  }, error = function(e) {
    stop(
      "Failed to import gephi_cli Python package.\n",
      "Make sure it is installed: pip install gephi-cli\n",
      "And that gephi-toolkit JAR is downloaded: python download_toolkit.py\n",
      "Error: ", conditionMessage(e),
      call. = FALSE
    )
  })

  .gephi$initialized <- TRUE
  message("gephir initialized successfully.")
  invisible(TRUE)
}
