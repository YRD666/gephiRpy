#' Quick visualization: import, layout, style, export in one call
#'
#' Accepts file paths, data.frames, adjacency matrices, or igraph objects
#' as input. Automatically runs layout, metrics, styling, and exports
#' to PNG/PDF/SVG.
#'
#' @param input Graph file path (string), data.frame, matrix, or igraph object
#' @param output Output image path (PNG/PDF/SVG extension determines format)
#' @param algorithm Layout algorithm (default "forceatlas2")
#' @param duration Layout duration in seconds (default 5)
#' @param width Image width in pixels (default 2048, for PNG only)
#' @param height Image height in pixels (default 2048, for PNG only)
#' @param color_by Attribute for node coloring (default "modularity")
#' @param size_by Attribute for node sizing (NULL = uniform size)
#' @param preset Preview preset: "default", "black_background", "text_outline"
#' @return workspace object (invisibly)
#' @export
#'
#' @examples
#' \dontrun{
#' # From file
#' gephi_quick("network.gexf", "output.png")
#'
#' # From data.frame
#' edges <- data.frame(source = c("A","B","C"), target = c("B","C","A"))
#' gephi_quick(edges, "output.png", duration = 10)
#'
#' # From igraph
#' library(igraph)
#' g <- sample_gnp(100, 0.05)
#' gephi_quick(g, "output.pdf", algorithm = "yifan_hu", preset = "black_background")
#' }
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
    stop("Unsupported input type. Use file path, data.frame, matrix, or igraph.",
         call. = FALSE)
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

  # Export based on file extension
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
