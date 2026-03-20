#' Apply preview preset
#'
#' @param workspace Workspace
#' @param preset Preset name: "default", "black_background", "text_outline"
#' @return workspace (invisibly)
#' @export
gephi_preset <- function(workspace, preset = "default") {
  .check_init()
  .gephi$preview$apply_preset(preset, workspace)
  invisible(workspace)
}

#' Configure preview settings
#'
#' @param workspace Workspace
#' @param ... Preview properties: show_labels, edge_opacity, node_opacity,
#'   edge_color, node_border_width, label_font, etc.
#' @return list with applied settings
#' @export
gephi_preview <- function(workspace, ...) {
  .check_init()
  reticulate::py_to_r(.gephi$preview$configure_preview(workspace, ...))
}

#' Export to PNG image
#'
#' @param workspace Workspace
#' @param file Output PNG path
#' @param width Image width in pixels (default 1024)
#' @param height Image height in pixels (default 1024)
#' @return file path (invisibly)
#' @export
gephi_export_image <- function(workspace, file, width = 1024L, height = 1024L) {
  .check_init()
  .gephi$preview$export_image(file, as.integer(width), as.integer(height), workspace)
  invisible(file)
}

#' Export to PDF
#'
#' @param workspace Workspace
#' @param file Output PDF path
#' @return file path (invisibly)
#' @export
gephi_export_pdf <- function(workspace, file) {
  .check_init()
  .gephi$preview$export_pdf(file, workspace)
  invisible(file)
}

#' Export to SVG
#'
#' @param workspace Workspace
#' @param file Output SVG path
#' @return file path (invisibly)
#' @export
gephi_export_svg <- function(workspace, file) {
  .check_init()
  .gephi$preview$export_svg(file, workspace)
  invisible(file)
}
