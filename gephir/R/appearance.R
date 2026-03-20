#' Color nodes by modularity class
#'
#' Run modularity metric first if not already computed.
#'
#' @param workspace Workspace
#' @return result (invisibly)
#' @export
gephi_color_modularity <- function(workspace) {
  .check_init()
  reticulate::py_to_r(.gephi$appearance$color_nodes_by_modularity(workspace))
}

#' Color nodes by partition attribute
#'
#' @param workspace Workspace
#' @param column Attribute column name for partitioning
#' @return result (invisibly)
#' @export
gephi_color_partition <- function(workspace, column) {
  .check_init()
  reticulate::py_to_r(.gephi$appearance$color_nodes_by_partition(column, workspace))
}

#' Set uniform node color (RGB 0-255)
#'
#' @param workspace Workspace
#' @param r Red value (0-255)
#' @param g Green value (0-255)
#' @param b Blue value (0-255)
#' @return workspace (invisibly)
#' @export
gephi_color_nodes <- function(workspace, r, g, b) {
  .check_init()
  .gephi$appearance$set_all_nodes_color(
    as.integer(r), as.integer(g), as.integer(b), workspace
  )
  invisible(workspace)
}

#' Set uniform edge color (RGB 0-255)
#'
#' @param workspace Workspace
#' @param r Red value (0-255)
#' @param g Green value (0-255)
#' @param b Blue value (0-255)
#' @return workspace (invisibly)
#' @export
gephi_color_edges <- function(workspace, r, g, b) {
  .check_init()
  .gephi$appearance$set_all_edges_color(
    as.integer(r), as.integer(g), as.integer(b), workspace
  )
  invisible(workspace)
}

#' Size nodes by attribute
#'
#' @param workspace Workspace
#' @param column Attribute column name (e.g. "pageranks", "Degree")
#' @param min_size Minimum node size (default 10)
#' @param max_size Maximum node size (default 50)
#' @return result
#' @export
gephi_size_by <- function(workspace, column, min_size = 10, max_size = 50) {
  .check_init()
  reticulate::py_to_r(.gephi$appearance$set_node_size_by_attribute(
    column, min_size, max_size, workspace
  ))
}

#' Set node labels
#'
#' @param workspace Workspace
#' @param column Column to use for labels (NULL = default "Label" column)
#' @return result
#' @export
gephi_labels <- function(workspace, column = NULL) {
  .check_init()
  reticulate::py_to_r(.gephi$appearance$set_node_labels(column, workspace))
}
