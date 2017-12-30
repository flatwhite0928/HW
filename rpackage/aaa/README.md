
<!-- README.md is generated from README.Rmd. Please edit that file -->
aaa
===

The goal of aaa is to help compute the probability of geometric distribution.

Example
-------

This is a basic example which shows you how to solve a common problem:

``` r
## basic example code
# The probability of having the first success on the kth attempt with a probability p of succeeding on any one try.
library(aaa)
k=11
p=0.2
probability=Geometric(k, p)
probability
#> [1] 0.02147484
```
