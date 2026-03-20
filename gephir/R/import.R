#' Import a graph file
#'
#' @param file Path to graph file (GEXF, GraphML, GML, CSV, Pajek, DOT, GDF, JSON)
#' @param workspace Existing workspace (NULL = create new)
#' @param processor Import processor: "default", "append", or "merge"
#' @return workspace object
#' @export
gephi_import <- function(file, workspace = NULL, processor = "default") {
  .check_init()
  .gephi$io_graph$import_graph(file, workspace, processor)
}

#' Import from URL
#'
#' @param url HTTP/HTTPS URL to a graph file
#' @param format Force format ("gexf", "graphml", etc.) or NULL for auto-detect
#' @param workspace Existing workspace (NULL = create new)
#' @return workspace object
#' @export
gephi_import_url <- function(url, format = NULL, workspace = NULL) {
  .check_init()
  .gephi$io_graph$import_from_url(url, workspace, format = format)
}

#' Import from data.frame (edge list)
#'
#' @param edges data.frame with at least source and target columns
#' @param source_col Name of source column (default "source")
#' @param target_col Name of target column (default "target")
#' @param weight_col Name of weight column (NULL = no weights)
#' @param directed Create directed graph (default TRUE)
#' @param workspace Existing workspace (NULL = create new)
#' @return workspace object
#' @export
gephi_import_df <- function(edges, source_col = "source", target_col = "target",
                            weight_col = NULL, directed = TRUE, workspace = NULL) {
  .check_init()
  pd <- reticulate::import("pandas")
  df <- pd$DataFrame(edges)
  .gephi$io_graph$import_from_pandas(
    df, source_col = source_col, target_col = target_col,
    weight_col = weight_col, directed = directed, workspace = workspace
  )
}

#' Import from edge tuples
#'
#' @param edges List of vectors: c(source, target) or c(source, target, weight)
#' @param directed Create directed graph (default TRUE)
#' @param workspace Existing workspace (NULL = create new)
#' @return workspace object
#' @export
#'
#' @examples
#' \dontrun{
#' edges <- list(c("A", "B"), c("B", "C", 2.0), c("C", "A", 1.5))
#' ws <- gephi_import_edges(edges)
#' }
gephi_import_edges <- function(edges, directed = TRUE, workspace = NULL) {
  .check_init()
  py_edges <- lapply(edges, function(e) {
    if (length(e) == 2) {
      reticulate::tuple(e[[1]], e[[2]])
    } else if (length(e) >= 3) {
      reticulate::tuple(e[[1]], e[[2]], as.numeric(e[[3]]))
    } else {
      stop("Each edge must have at least 2 elements (source, target).", call. = FALSE)
    }
  })
  .gephi$io_graph$import_from_edge_list(py_edges, directed, workspace)
}

#' Import from adjacency matrix
#'
#' @param mat Numeric matrix (0 = no edge, >0 = edge weight)
#' @param labels Node labels (NULL = 0,1,2,...)
#' @param directed Create directed graph (default TRUE)
#' @param workspace Existing workspace (NULL = create new)
#' @return workspace object
#' @export
gephi_import_matrix <- function(mat, labels = NULL, directed = TRUE, workspace = NULL) {
  .check_init()
  py_mat <- reticulate::r_to_py(as.matrix(mat))
  py_labels <- if (!is.null(labels)) as.list(as.character(labels)) else NULL
  .gephi$io_graph$import_from_adjacency_matrix(py_mat, py_labels, directed, workspace)
}

#' Import from igraph object
#'
#' @param g An igraph graph object
#' @param workspace Existing workspace (NULL = create new)
#' @return workspace object
#' @export
gephi_import_igraph <- function(g, workspace = NULL) {
  .check_init()
  if (!requireNamespace("igraph", quietly = TRUE)) {
    stop("Package 'igraph' is required: install.packages('igraph')", call. = FALSE)
  }

  el <- igraph::as_edgelist(g)
  weights <- if ("weight" %in% igraph::edge_attr_names(g)) {
    igraph::E(g)$weight
  } else {
    rep(1.0, igraph::ecount(g))
  }
  directed <- igraph::is_directed(g)

  edges <- lapply(seq_len(nrow(el)), function(i) {
    reticulate::tuple(as.character(el[i, 1]), as.character(el[i, 2]), as.numeric(weights[i]))
  })

  .gephi$io_graph$import_from_edge_list(edges, directed, workspace)
}
