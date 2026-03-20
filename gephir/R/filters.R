#' Filter by degree range
#'
#' @param workspace Workspace
#' @param min Minimum degree (NULL = no lower bound)
#' @param max Maximum degree (NULL = no upper bound)
#' @return list with filter results
#' @export
gephi_filter_degree <- function(workspace, min = NULL, max = NULL) {
  .check_init()
  min_val <- if (!is.null(min)) as.integer(min) else NULL
  max_val <- if (!is.null(max)) as.integer(max) else NULL
  reticulate::py_to_r(.gephi$filters$filter_by_degree(min_val, max_val, workspace))
}

#' Keep giant component only
#'
#' @param workspace Workspace
#' @return list with filter results
#' @export
gephi_filter_giant <- function(workspace) {
  .check_init()
  reticulate::py_to_r(.gephi$filters$filter_giant_component(workspace))
}

#' K-core filter
#'
#' @param workspace Workspace
#' @param k Core number threshold
#' @return list with filter results
#' @export
gephi_filter_kcore <- function(workspace, k) {
  .check_init()
  reticulate::py_to_r(.gephi$filters$filter_k_core(as.integer(k), workspace))
}

#' Filter by node attribute
#'
#' @param workspace Workspace
#' @param column Attribute column name
#' @param value Attribute value to keep
#' @return list with filter results
#' @export
gephi_filter_attribute <- function(workspace, column, value) {
  .check_init()
  # Convert numeric to integer for Java compatibility
  if (is.numeric(value) && value == as.integer(value)) {
    value <- as.integer(value)
  }
  reticulate::py_to_r(.gephi$filters$filter_by_attribute(column, value, workspace))
}

#' Ego network filter
#'
#' @param workspace Workspace
#' @param node_id Center node ID
#' @param depth Depth of ego network (default 1)
#' @return list with filter results
#' @export
gephi_filter_ego <- function(workspace, node_id, depth = 1L) {
  .check_init()
  reticulate::py_to_r(.gephi$filters$filter_ego(node_id, as.integer(depth), workspace))
}

#' Reset all filters
#'
#' @param workspace Workspace
#' @return list with result
#' @export
gephi_filter_reset <- function(workspace) {
  .check_init()
  reticulate::py_to_r(.gephi$filters$reset_filter(workspace))
}
