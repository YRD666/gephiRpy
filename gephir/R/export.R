#' Export graph to file
#'
#' @param workspace Workspace to export
#' @param file Output file path (GEXF, GraphML, GML, CSV, etc.)
#' @return file path (invisibly)
#' @export
gephi_export <- function(workspace, file) {
  .check_init()
  .gephi$io_graph$export_graph(file, workspace)
  invisible(file)
}

#' Export to data.frames
#'
#' @param workspace Workspace
#' @return list with \code{$edges} and \code{$nodes} data.frames
#' @export
gephi_to_df <- function(workspace) {
  .check_init()
  result <- .gephi$io_graph$export_to_pandas(workspace)
  list(
    edges = reticulate::py_to_r(result[[1]]),
    nodes = reticulate::py_to_r(result[[2]])
  )
}

#' Export to igraph object
#'
#' @param workspace Workspace
#' @return igraph graph object
#' @export
gephi_to_igraph <- function(workspace) {
  .check_init()
  if (!requireNamespace("igraph", quietly = TRUE)) {
    stop("Package 'igraph' is required: install.packages('igraph')", call. = FALSE)
  }
  dfs <- gephi_to_df(workspace)
  if (nrow(dfs$edges) == 0) {
    return(igraph::make_empty_graph(n = nrow(dfs$nodes)))
  }
  igraph::graph_from_data_frame(dfs$edges, directed = TRUE, vertices = dfs$nodes)
}

#' Get graph information
#'
#' @param workspace Workspace
#' @return list with node_count, edge_count, etc.
#' @export
gephi_info <- function(workspace) {
  .check_init()
  reticulate::py_to_r(.gephi$io_graph$get_graph_info(workspace))
}

#' Validate graph structure
#'
#' @param workspace Workspace
#' @return list with structural quality report
#' @export
gephi_validate <- function(workspace) {
  .check_init()
  reticulate::py_to_r(.gephi$io_graph$validate_graph(workspace))
}

#' List nodes in workspace
#'
#' @param workspace Workspace
#' @param limit Max nodes to return (0 = all)
#' @return data.frame of nodes
#' @export
gephi_nodes <- function(workspace, limit = 50L) {
  .check_init()
  nodes <- .gephi$io_graph$list_nodes(workspace, as.integer(limit))
  do.call(rbind, lapply(nodes, as.data.frame, stringsAsFactors = FALSE))
}

#' List edges in workspace
#'
#' @param workspace Workspace
#' @param limit Max edges to return (0 = all)
#' @return data.frame of edges
#' @export
gephi_edges <- function(workspace, limit = 50L) {
  .check_init()
  edges <- .gephi$io_graph$list_edges(workspace, as.integer(limit))
  do.call(rbind, lapply(edges, as.data.frame, stringsAsFactors = FALSE))
}
