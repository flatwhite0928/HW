#' Geometric random variable.
#'
#' @param k A number.
#' @param p A number.
#' @return The probability of having the first success on the \code{k} th attempt with a probability \code{p} of succeeding on any one try.
#' @examples
#' Geometric(10, 0.1)
#' Geometric(99, 0.55)
#' @export
Geometric <- function(k, p) {
  if (p>=1 | p<=0) return ("the probabilty should between 0 and 1")
  else
    return (((1-p)^(k-1))*p)
}


