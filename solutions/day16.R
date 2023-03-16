raw_input <- readLines("inputs/day16.txt") |>
    strsplit(split = "") |>
    unlist(use.names = FALSE) |>
    as.integer()

leading_digits <- function(x) {
    x <- abs(x)
    x %/% 10^floor(log(x, 10))
}


naive_fft <- function(input, iterations, pattern) {
    size <- length(input)
    patterns <- vapply(seq_len(size),
        \(x) rep(pattern, each = x, length.out = size + 1)[-1],
        FUN.VALUE = numeric(size)
    ) |>
        t()

    for (i in seq_len(iterations)) {
        input <- abs(patterns %*% input) %% 10
    }
    input
}

pattern <- c(0, 1, 0, -1)
# raw_input <- 1:8
result <- naive_fft(raw_input, 100, pattern)
part1 <- result[1:8] |>
    as.character() |>
    paste(collapse = "")
print(part1)

offset <- as.character(raw_input[1:7]) |>
    as.integer()
