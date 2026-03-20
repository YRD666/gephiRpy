#' Generate a graph
#'
#' Generate one of 11 types of graphs: random, scale_free, small_world,
#' complete, star, ring, grid, tree, path, empty, dynamic.
#'
#' @param type Graph type name
#' @param ... Parameters for the specific generator:
#'   \describe{
#'     \item{random}{node_count, wiring_prob, seed}
#'     \item{scale_free}{node_count, m (edges per new node), seed}
#'     \item{small_world}{node_count, k (neighbors), beta (rewiring prob), seed}
#'     \item{complete}{node_count}
#'     \item{star}{node_count}
#'     \item{ring}{node_count}
#'     \item{grid}{rows, cols}
#'     \item{tree}{depth, branching}
#'     \item{path}{node_count}
#'     \item{empty}{node_count}
#'     \item{dynamic}{(no parameters)}
#'   }
#' @return workspace object
#' @export
#'
#' @examples
#' \dontrun{
#' ws <- gephi_generate("random", node_count = 100, wiring_prob = 0.05)
#' ws <- gephi_generate("scale_free", node_count = 500, m = 3)
#' ws <- gephi_generate("small_world", node_count = 200, k = 6, beta = 0.3)
#' ws <- gephi_generate("grid", rows = 10, cols = 10)
#' ws <- gephi_generate("tree", depth = 5, branching = 3)
#' }
gephi_generate <- function(type, ...) {
  .check_init()
  args <- list(...)

  # Parameters that must be integers for Python
  int_params <- c("node_count", "m", "k", "rows", "cols", "depth", "branching", "seed")
  args <- lapply(seq_along(args), function(i) {
    nm <- names(args)[i]
    val <- args[[i]]
    if (!is.null(nm) && nm %in% int_params && is.numeric(val)) {
      as.integer(val)
    } else {
      val
    }
  })
  names(args) <- names(list(...))

  do.call(.gephi$generator$generate, c(list(type), args))
}
