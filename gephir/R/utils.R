#' Find shortest path between two nodes
#'
#' @param workspace Workspace
#' @param source Source node ID
#' @param target Target node ID
#' @return list with path, distance, etc.
#' @export
gephi_shortest_path <- function(workspace, source, target) {
  .check_init()
  reticulate::py_to_r(.gephi$shortest$get_path_between(
    as.character(source), as.character(target), workspace = workspace
  ))
}

#' List available algorithms, metrics, or generators
#'
#' @param what What to list: "layouts", "metrics", "generators", "filters", "presets"
#' @return character vector of available names
#' @export
gephi_list <- function(what = "layouts") {
  .check_init()
  what <- match.arg(what, c("layouts", "metrics", "generators", "filters", "presets"))

  result <- switch(what,
    layouts = c("forceatlas2", "forceatlas1", "fruchterman_reingold", "yifan_hu",
                "openord", "label_adjust", "noverlap", "random_layout",
                "rotate", "expand", "contract"),
    metrics = c("degree", "pagerank", "modularity", "betweenness", "closeness",
                "eigenvector", "hits", "clustering_coefficient",
                "connected_components", "diameter", "density",
                "avg_degree", "avg_path_length", "avg_clustering"),
    generators = c("random", "scale_free", "small_world", "complete", "star",
                   "ring", "grid", "tree", "path", "empty", "dynamic"),
    filters = c("degree", "giant_component", "k_core", "attribute", "ego",
                "edge_weight", "inter_edges", "partition_count"),
    presets = c("default", "black_background", "text_outline")
  )
  result
}
