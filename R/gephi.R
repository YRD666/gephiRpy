# ============================================================================
# gephi.R - R interface to gephi-cli Python toolkit
# ============================================================================
#
# Usage:
#   source("R/gephi.R")
#   gephi_init()                              # one-time setup
#   ws <- gephi_import("network.gexf")
#   ws <- gephi_layout(ws, "forceatlas2", duration = 10)
#   gephi_export_image(ws, "output.png")
#
# Requirements:
#   install.packages("reticulate")
#   pip install -e .   (in gephi-cli directory)
#   python download_toolkit.py
# ============================================================================

library(reticulate)

# ─── Internal state ──────────────────────────────────────────────────────────

.gephi_env <- new.env(parent = emptyenv())
.gephi_env$initialized <- FALSE

# ─── Init ────────────────────────────────────────────────────────────────────

#' Initialize gephi-cli Python bridge
#'
#' @param python Path to Python executable (NULL = auto-detect)
#' @param virtualenv Name of virtualenv to use (NULL = system Python)
#' @param conda Name of conda environment (NULL = don't use conda)
#' @export
gephi_init <- function(python = NULL, virtualenv = NULL, conda = NULL) {
  if (!is.null(python)) {
    use_python(python, required = TRUE)
  } else if (!is.null(virtualenv)) {
    use_virtualenv(virtualenv, required = TRUE)
  } else if (!is.null(conda)) {
    use_condaenv(conda, required = TRUE)
  }

  .gephi_env$io_graph   <- import("gephi_cli.io_graph")
  .gephi_env$layout     <- import("gephi_cli.layout")
  .gephi_env$metrics    <- import("gephi_cli.metrics")
  .gephi_env$filters    <- import("gephi_cli.filters")
  .gephi_env$appearance <- import("gephi_cli.appearance")
  .gephi_env$preview    <- import("gephi_cli.preview")
  .gephi_env$generator  <- import("gephi_cli.generator")
  .gephi_env$pipeline   <- import("gephi_cli.pipeline")
  .gephi_env$core       <- import("gephi_cli.core")

  .gephi_env$initialized <- TRUE
  message("gephi-cli initialized successfully.")
  invisible(TRUE)
}

.check_init <- function() {
  if (!.gephi_env$initialized) {
    stop("Call gephi_init() first.", call. = FALSE)
  }
}

# ─── Import / Export ─────────────────────────────────────────────────────────

#' Import a graph file
#'
#' @param file Path to graph file (GEXF, GraphML, GML, CSV, etc.)
#' @param workspace Existing workspace (NULL = new)
#' @param processor "default", "append", or "merge"
#' @return workspace object
#' @export
gephi_import <- function(file, workspace = NULL, processor = "default") {
  .check_init()
  .gephi_env$io_graph$import_graph(file, workspace, processor)
}

#' Import from URL
#'
#' @param url HTTP/HTTPS URL to a graph file
#' @param format Force format ("gexf", "graphml", etc.) or NULL for auto
#' @param workspace Existing workspace (NULL = new)
#' @return workspace object
#' @export
gephi_import_url <- function(url, format = NULL, workspace = NULL) {
  .check_init()
  .gephi_env$io_graph$import_from_url(url, workspace, format = format)
}

#' Import from edge list (data.frame)
#'
#' @param edges data.frame with columns: source, target, and optionally weight
#' @param source_col Name of source column (default "source")
#' @param target_col Name of target column (default "target")
#' @param weight_col Name of weight column (NULL = no weights)
#' @param directed Create directed graph (default TRUE)
#' @param workspace Existing workspace (NULL = new)
#' @return workspace object
#' @export
gephi_import_df <- function(edges, source_col = "source", target_col = "target",
                            weight_col = NULL, directed = TRUE, workspace = NULL) {
  .check_init()
  pd <- import("pandas")
  df <- pd$DataFrame(edges)
  .gephi_env$io_graph$import_from_pandas(
    df, source_col = source_col, target_col = target_col,
    weight_col = weight_col, directed = directed, workspace = workspace
  )
}

#' Import from edge tuples
#'
#' @param edges List of c(source, target) or c(source, target, weight)
#' @param directed Create directed graph (default TRUE)
#' @param workspace Existing workspace (NULL = new)
#' @return workspace object
#' @export
gephi_import_edges <- function(edges, directed = TRUE, workspace = NULL) {
  .check_init()
  # Convert R list to Python-friendly format
  py_edges <- lapply(edges, function(e) {
    if (length(e) == 2) {
      tuple(e[[1]], e[[2]])
    } else {
      tuple(e[[1]], e[[2]], as.numeric(e[[3]]))
    }
  })
  .gephi_env$io_graph$import_from_edge_list(py_edges, directed, workspace)
}

#' Import from adjacency matrix
#'
#' @param mat Numeric matrix (0 = no edge, >0 = edge weight)
#' @param labels Node labels (NULL = 0,1,2,...)
#' @param directed Default TRUE
#' @param workspace Existing workspace
#' @return workspace object
#' @export
gephi_import_matrix <- function(mat, labels = NULL, directed = TRUE, workspace = NULL) {
  .check_init()
  py_mat <- r_to_py(as.matrix(mat))
  py_labels <- if (!is.null(labels)) as.list(as.character(labels)) else NULL
  .gephi_env$io_graph$import_from_adjacency_matrix(py_mat, py_labels, directed, workspace)
}

#' Import from igraph object
#'
#' @param g An igraph graph object
#' @param workspace Existing workspace (NULL = new)
#' @return workspace object
#' @export
gephi_import_igraph <- function(g, workspace = NULL) {
  .check_init()
  if (!requireNamespace("igraph", quietly = TRUE)) {
    stop("Package 'igraph' is required.", call. = FALSE)
  }

  # Convert igraph to edge list
  el <- igraph::as_edgelist(g)
  weights <- if ("weight" %in% igraph::edge_attr_names(g)) {
    igraph::E(g)$weight
  } else {
    rep(1.0, igraph::ecount(g))
  }
  directed <- igraph::is_directed(g)

  edges <- lapply(seq_len(nrow(el)), function(i) {
    tuple(as.character(el[i, 1]), as.character(el[i, 2]), as.numeric(weights[i]))
  })

  .gephi_env$io_graph$import_from_edge_list(edges, directed, workspace)
}

#' Export graph to file
#'
#' @param workspace Workspace to export
#' @param file Output file path (GEXF, GraphML, GML, CSV, etc.)
#' @export
gephi_export <- function(workspace, file) {
  .check_init()
  .gephi_env$io_graph$export_graph(file, workspace)
  invisible(file)
}

#' Export to data.frame
#'
#' @param workspace Workspace
#' @return list with $edges and $nodes data.frames
#' @export
gephi_to_df <- function(workspace) {
  .check_init()
  result <- .gephi_env$io_graph$export_to_pandas(workspace)
  list(
    edges = py_to_r(result[[1]]),
    nodes = py_to_r(result[[2]])
  )
}

#' Export to igraph
#'
#' @param workspace Workspace
#' @return igraph graph object
#' @export
gephi_to_igraph <- function(workspace) {
  .check_init()
  if (!requireNamespace("igraph", quietly = TRUE)) {
    stop("Package 'igraph' is required.", call. = FALSE)
  }
  dfs <- gephi_to_df(workspace)
  if (nrow(dfs$edges) == 0) {
    return(igraph::make_empty_graph(n = nrow(dfs$nodes)))
  }
  g <- igraph::graph_from_data_frame(dfs$edges, directed = TRUE, vertices = dfs$nodes)
  g
}

# ─── Graph Info ──────────────────────────────────────────────────────────────

#' Get graph information
#'
#' @param workspace Workspace
#' @return list with node_count, edge_count, etc.
#' @export
gephi_info <- function(workspace) {
  .check_init()
  py_to_r(.gephi_env$io_graph$get_graph_info(workspace))
}

#' Validate graph structure
#'
#' @param workspace Workspace
#' @return list with structural report and issues
#' @export
gephi_validate <- function(workspace) {
  .check_init()
  py_to_r(.gephi_env$io_graph$validate_graph(workspace))
}

#' List nodes
#'
#' @param workspace Workspace
#' @param limit Max nodes (0 = all)
#' @return data.frame of nodes
#' @export
gephi_nodes <- function(workspace, limit = 50L) {
  .check_init()
  nodes <- .gephi_env$io_graph$list_nodes(workspace, as.integer(limit))
  do.call(rbind, lapply(nodes, as.data.frame, stringsAsFactors = FALSE))
}

#' List edges
#'
#' @param workspace Workspace
#' @param limit Max edges (0 = all)
#' @return data.frame of edges
#' @export
gephi_edges <- function(workspace, limit = 50L) {
  .check_init()
  edges <- .gephi_env$io_graph$list_edges(workspace, as.integer(limit))
  do.call(rbind, lapply(edges, as.data.frame, stringsAsFactors = FALSE))
}

# ─── Generate ───────────────────────────────────────────────────────────────

#' Generate a graph
#'
#' @param type Graph type: "random", "scale_free", "small_world", "complete",
#'   "star", "ring", "grid", "tree", "path", "empty", "dynamic"
#' @param ... Parameters for the specific generator
#' @return workspace object
#' @export
#'
#' @examples
#' ws <- gephi_generate("random", node_count = 100, wiring_prob = 0.05)
#' ws <- gephi_generate("scale_free", node_count = 500, m = 3)
#' ws <- gephi_generate("small_world", node_count = 200, k = 6, beta = 0.3)
#' ws <- gephi_generate("grid", rows = 10, cols = 10)
#' ws <- gephi_generate("tree", depth = 4, branching = 3)
gephi_generate <- function(type, ...) {
  .check_init()
  args <- list(...)
  # Convert R integers
  args <- lapply(args, function(x) {
    if (is.integer(x)) as.numeric(x) else x
  })
  do.call(.gephi_env$generator$generate, c(list(type), args))
}

# ─── Layout ─────────────────────────────────────────────────────────────────

#' Run a layout algorithm
#'
#' @param workspace Workspace
#' @param algorithm Algorithm name (e.g. "forceatlas2", "yifan_hu", "fruchterman_reingold")
#' @param iterations Number of iterations (ignored if duration is set)
#' @param duration Run time in seconds (recommended for force-directed)
#' @param auto_tune Auto-tune FA2 parameters (default TRUE)
#' @param ... Additional algorithm parameters
#' @return list with layout results
#' @export
gephi_layout <- function(workspace, algorithm, iterations = 100L,
                         duration = NULL, auto_tune = TRUE, ...) {
  .check_init()
  params <- list(...)
  result <- .gephi_env$layout$run_layout(
    algorithm, as.integer(iterations), workspace,
    duration = duration, auto_tune = auto_tune
  )
  # Apply extra params if any
  if (length(params) > 0) {
    result <- do.call(.gephi_env$layout$run_layout, c(
      list(algorithm, as.integer(iterations), workspace,
           duration = duration, auto_tune = auto_tune),
      params
    ))
  }
  py_to_r(result)
}

#' Normalize layout positions
#'
#' @param workspace Workspace
#' @param scale Target coordinate range (default 1000)
#' @return list with normalize results
#' @export
gephi_normalize <- function(workspace, scale = 1000) {
  .check_init()
  py_to_r(.gephi_env$layout$normalize_layout(workspace, scale))
}

# ─── Metrics ─────────────────────────────────────────────────────────────────

#' Run a graph metric
#'
#' @param workspace Workspace
#' @param name Metric name ("degree", "pagerank", "modularity", "betweenness", etc.)
#' @param ... Additional metric parameters
#' @return list with metric results
#' @export
gephi_metric <- function(workspace, name, ...) {
  .check_init()
  py_to_r(.gephi_env$metrics$run_metric(name, workspace, ...))
}

#' Run all metrics
#'
#' @param workspace Workspace
#' @return list of all metric results
#' @export
gephi_all_metrics <- function(workspace) {
  .check_init()
  py_to_r(.gephi_env$metrics$run_all_metrics(workspace))
}

# ─── Filters ─────────────────────────────────────────────────────────────────

#' Filter by degree range
#' @export
gephi_filter_degree <- function(workspace, min = NULL, max = NULL) {
  .check_init()
  py_to_r(.gephi_env$filters$filter_by_degree(min, max, workspace))
}

#' Keep giant component only
#' @export
gephi_filter_giant <- function(workspace) {
  .check_init()
  py_to_r(.gephi_env$filters$filter_giant_component(workspace))
}

#' K-core filter
#' @export
gephi_filter_kcore <- function(workspace, k) {
  .check_init()
  py_to_r(.gephi_env$filters$filter_k_core(as.integer(k), workspace))
}

#' Reset all filters
#' @export
gephi_filter_reset <- function(workspace) {
  .check_init()
  py_to_r(.gephi_env$filters$reset_filter(workspace))
}

# ─── Appearance ──────────────────────────────────────────────────────────────

#' Color nodes by modularity class
#' @export
gephi_color_modularity <- function(workspace) {
  .check_init()
  py_to_r(.gephi_env$appearance$color_nodes_by_modularity(workspace))
}

#' Color nodes by partition attribute
#' @export
gephi_color_partition <- function(workspace, column) {
  .check_init()
  py_to_r(.gephi_env$appearance$color_nodes_by_partition(column, workspace))
}

#' Set uniform node color (RGB 0-255)
#' @export
gephi_color_nodes <- function(workspace, r, g, b) {
  .check_init()
  .gephi_env$appearance$set_all_nodes_color(
    as.integer(r), as.integer(g), as.integer(b), workspace
  )
  invisible(workspace)
}

#' Size nodes by attribute
#' @export
gephi_size_by <- function(workspace, column, min_size = 10, max_size = 50) {
  .check_init()
  py_to_r(.gephi_env$appearance$set_node_size_by_attribute(column, min_size, max_size, workspace))
}

#' Set node labels
#' @export
gephi_labels <- function(workspace, column = NULL) {
  .check_init()
  py_to_r(.gephi_env$appearance$set_node_labels(column, workspace))
}

# ─── Preview & Export ────────────────────────────────────────────────────────

#' Apply preview preset
#' @export
gephi_preset <- function(workspace, preset = "default") {
  .check_init()
  .gephi_env$preview$apply_preset(preset, workspace)
  invisible(workspace)
}

#' Configure preview settings
#' @export
gephi_preview <- function(workspace, ...) {
  .check_init()
  py_to_r(.gephi_env$preview$configure_preview(workspace, ...))
}

#' Export to PNG image
#'
#' @param workspace Workspace
#' @param file Output PNG path
#' @param width Image width (default 1024)
#' @param height Image height (default 1024)
#' @return file path (invisibly)
#' @export
gephi_export_image <- function(workspace, file, width = 1024L, height = 1024L) {
  .check_init()
  .gephi_env$preview$export_image(file, as.integer(width), as.integer(height), workspace)
  invisible(file)
}

#' Export to PDF
#' @export
gephi_export_pdf <- function(workspace, file) {
  .check_init()
  .gephi_env$preview$export_pdf(file, workspace)
  invisible(file)
}

#' Export to SVG
#' @export
gephi_export_svg <- function(workspace, file) {
  .check_init()
  .gephi_env$preview$export_svg(file, workspace)
  invisible(file)
}

# ─── Pipeline ────────────────────────────────────────────────────────────────

#' Run YAML pipeline
#'
#' @param config_file Path to YAML pipeline file
#' @return list of step results
#' @export
gephi_pipeline <- function(config_file) {
  .check_init()
  py_to_r(.gephi_env$pipeline$run_pipeline(config_file))
}

# ─── Convenience ─────────────────────────────────────────────────────────────

#' Quick visualization: import, layout, style, export in one call
#'
#' @param input Graph file path, data.frame, igraph, or adjacency matrix
#' @param output Output image path (PNG/PDF/SVG)
#' @param algorithm Layout algorithm (default "forceatlas2")
#' @param duration Layout duration in seconds (default 5)
#' @param width Image width (default 2048)
#' @param height Image height (default 2048)
#' @param color_by Attribute for node coloring (default "modularity")
#' @param size_by Attribute for node sizing (NULL = uniform)
#' @param preset Preview preset (default "default")
#' @return workspace object (invisibly)
#' @export
gephi_quick <- function(input, output, algorithm = "forceatlas2", duration = 5,
                        width = 2048L, height = 2048L,
                        color_by = "modularity", size_by = NULL,
                        preset = "default") {
  .check_init()

  # Import based on input type
  if (is.character(input) && length(input) == 1 && file.exists(input)) {
    ws <- gephi_import(input)
  } else if (is.data.frame(input)) {
    ws <- gephi_import_df(input)
  } else if (is.matrix(input)) {
    ws <- gephi_import_matrix(input)
  } else if (inherits(input, "igraph")) {
    ws <- gephi_import_igraph(input)
  } else {
    stop("Unsupported input type. Use file path, data.frame, matrix, or igraph.")
  }

  # Layout
  gephi_layout(ws, algorithm, duration = duration)
  gephi_normalize(ws)

  # Metrics & styling
  if (identical(color_by, "modularity")) {
    tryCatch(gephi_metric(ws, "modularity"), error = function(e) NULL)
    tryCatch(gephi_color_modularity(ws), error = function(e) NULL)
  }
  if (!is.null(size_by)) {
    tryCatch(gephi_size_by(ws, size_by), error = function(e) NULL)
  }

  # Labels
  gephi_labels(ws)

  # Preview
  gephi_preset(ws, preset)
  gephi_preview(ws, show_labels = TRUE, edge_opacity = 40)

  # Export
  ext <- tolower(tools::file_ext(output))
  if (ext == "png") {
    gephi_export_image(ws, output, as.integer(width), as.integer(height))
  } else if (ext == "pdf") {
    gephi_export_pdf(ws, output)
  } else if (ext == "svg") {
    gephi_export_svg(ws, output)
  } else {
    gephi_export(ws, output)
  }

  message(sprintf("Exported to %s", output))
  invisible(ws)
}
