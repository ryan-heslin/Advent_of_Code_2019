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

# We just have to backsolve up to the target digit each iteration, since
# the trailing half of digits
# *are all independent* of the first half
backsolve <- function(input, target, iterations = 100) {
    target <- target + 1 # number of digits to skip before
    size <- length(input)
    repetitions <- 10000
    end <- size * repetitions
    start <- max(target %% size, 0)


    # partial vector starting from target end position, then repeat to max length
    vector <- c(
        input[start:size],
        rep(input, length.out = (size * repetitions - target - (size - start)))
    ) |>
        rev()
    endpoint <- length(vector)

    for (iter in seq_len(iterations)) {
        vector <- abs(cumsum(vector)) %% 10
    }
    tail(vector, 8) |>
        rev() |>
        as.character() |>
        paste(collapse = "")
}

raw_input <- readLines("inputs/day16.txt") |>
    strsplit(split = "") |>
    unlist(use.names = FALSE) |>
    as.integer()

# raw_input <- 1:8
pattern <- c(0, 1, 0, -1)
result <- naive_fft(raw_input, 100, pattern)
part1 <- result[1:8] |>
    as.character() |>
    paste(collapse = "")
print(part1)

offset <- as.character(raw_input[1:7]) |>
    paste(collapse = "") |>
    as.integer()

part2 <- backsolve(raw_input, offset)
print(part2)
