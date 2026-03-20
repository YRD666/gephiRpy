#' Run a graph metric
#'
#' @param workspace Workspace
#' @param name Metric name: "degree", "pagerank", "modularity", "betweenness",
#'   "closeness", "eigenvector", "hits", "clustering_coefficient",
#'   "connected_components", "diameter", "density", "avg_degree",
#'   "avg_path_length", "avg_clustering"
#' @param ... Additional metric parameters (e.g. resolution for modularity)
#' @return list with metric results
#' @export
gephi_metric <- function(workspace, name, ...) {
  .check_init()
  reticulate::py_to_r(.gephi$metrics$run_metric(name, workspace, ...))
}

#' Run all metrics at once
#'
#' @param workspace Workspace
#' @return list of all metric results
#' @export
gephi_all_metrics <- function(workspace) {
  .check_init()
  reticulate::py_to_r(.gephi$metrics$run_all_metrics(workspace))
}
