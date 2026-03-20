#' Run a layout algorithm
#'
#' @param workspace Workspace
#' @param algorithm Algorithm name: "forceatlas2", "forceatlas1", "fruchterman_reingold",
#'   "yifan_hu", "openord", "label_adjust", "noverlap", "random_layout",
#'   "rotate", "expand", "contract"
#' @param iterations Number of iterations (used when duration is NULL)
#' @param duration Run time in seconds (recommended for force-directed layouts)
#' @param auto_tune Auto-tune ForceAtlas2 parameters based on graph size (default TRUE)
#' @param ... Additional algorithm-specific parameters
#' @return list with layout results (algorithm, iterations, elapsed time)
#' @export
gephi_layout <- function(workspace, algorithm, iterations = 100L,
                         duration = NULL, auto_tune = TRUE, ...) {
  .check_init()
  result <- .gephi$layout$run_layout(
    algorithm, as.integer(iterations), workspace,
    duration = duration, auto_tune = auto_tune, ...
  )
  reticulate::py_to_r(result)
}

#' Normalize layout positions
#'
#' Rescales node positions to fit within a target coordinate range,
#' with outlier clamping via percentile-based normalization.
#'
#' @param workspace Workspace
#' @param scale Target coordinate range (default 1000)
#' @param percentile Percentile for outlier clamping (default 0.05)
#' @param margin_ratio Margin ratio (default 0.05)
#' @return list with normalization results
#' @export
gephi_normalize <- function(workspace, scale = 1000, percentile = 0.05,
                            margin_ratio = 0.05) {
  .check_init()
  reticulate::py_to_r(.gephi$layout$normalize_layout(
    workspace, scale, percentile, margin_ratio
  ))
}
