#' Run YAML pipeline
#'
#' Execute a multi-step workflow defined in a YAML file.
#'
#' @param config_file Path to YAML pipeline file
#' @return list of step results
#' @export
#'
#' @examples
#' \dontrun{
#' # workflow.yaml:
#' # steps:
#' #   - action: generate
#' #     type: scale_free
#' #     nodes: 500
#' #   - action: layout
#' #     algorithm: forceatlas2
#' #     duration: 10
#' #   - action: export
#' #     file: output.png
#' results <- gephi_pipeline("workflow.yaml")
#' }
gephi_pipeline <- function(config_file) {
  .check_init()
  reticulate::py_to_r(.gephi$pipeline$run_pipeline(config_file))
}
