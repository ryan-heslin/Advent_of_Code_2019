parse <- function(lines) {
    gsub("[^0-9,-]+", "", lines) |>
        paste(collapse = ",") |>
        strsplit(",") |>
        unlist() |>
        strtoi() |>
        matrix(nrow = length(lines), byrow = TRUE) |>
        t()
}


update_velocity <- function(positions, combinations, selections) {
    first <- positions[, combinations[, 1]]
    second <- positions[, combinations[, 2]]
    comp <- adjust(first, second)
    combine <- function(x) rowSums(comp[, x[[1]]] %*% x[[2]])
    sapply(selections, combine)
}

adjust <- function(x, y) {
    ((x > y) * -1) + (x < y)
}

simulate <- function(moons, iterations) {
    n_rows <- nrow(moons)
    combinations <- dim(moons)[[2]] |>
        combn(m = 2) |>
        t()

    selections <- seq_len(ncol(moons)) |>
        unique() |>
        lapply(\(x){
            targets <- which(combinations == x, arr.ind = TRUE)
            targets[, 2][targets[, 2] == 2] <- -1
            list(targets[, 1], diag(targets[, 2]))
        })


    done <- FALSE
    rows <- seq_len(n_rows)
    periods <- rep(NA_integer_, 3)
    initials <- asplit(moons, MARGIN = 1)

    i <- 0
    while (i < iterations && !done) {
        i <- i + 1
        moons[, , "velocity"] <- update_velocity(moons[, , "position"], combinations, selections) + moons[, , "velocity"]
        moons[, , "position"] <- moons[, , "position"] + moons[, , "velocity"]
        result <- mapply(identical, initials, asplit(moons, MARGIN = 1))
        # found <- which(result)
        periods[result & is.na(periods)] <- i
        done <- !any(is.na(periods))
        # if (any(!is.na(periods))) {
        #     browser()
        # }
        # print(i)
        # print(moons)
    }
    list(moons, periods)
}

energy <- function(state) {
    state <- abs(state)
    (colSums(state[, , "position"]) %*% colSums(state[, , "velocity"]))[[1]]
}

gcd <- function(a, b, d = 0) {
    if (a == b) {
        return(a * 2^d)
    } else if (a %% 2 == 0 && b %% 2 == 0) {
        return(gcd(a / 2, b / 2, d + 1))
    } else if (a %% 2 == 0) {
        return(gcd(a / 2, b, d))
    } else if (b %% 2 == 0) {
        return(gcd(a, b / 2, d))
    } else {
        if (a < b) {
            tmp <- b
            b <- a
            a <- tmp
        }
        c <- a - b
        return(gcd(c / 2, b, d))
    }
}


lcm <- function(numbers) {
    increments <- numbers
    while (length(unique(numbers)) > 1) {
        target <- numbers == min(numbers)
        if (sum(target) > 1) {
            target <- target & increments == min(increments[target])
        }
        numbers[target] <- numbers[target] + increments[target]
    }
    unique(numbers)
}

raw_input <- readLines("inputs/day12.txt")
positions <- parse(raw_input)

moons <- array(c(positions, rep(0, prod(dim(positions)))),
    dim = c(dim(positions), 2),
    dimnames = list(c("x", "y", "z"), c("Io", "Europa", "Ganymede", "Callisto"), c("position", "velocity"))
)

updated <- simulate(moons, 1000)[[1]]
part1 <- energy(updated)
print(part1)

cycles <- simulate(moons, Inf)[[2]]
gcds <- combn(cycles, m = 2, FUN = \(x) gcd(x[[1]], x[[2]]))
lcms <- combn(cycles, m = 2, FUN = prod) / gcds
new <- gcd(cycles[[1]], lcms[[3]])
part2 <- (cycles[[1]] * lcms[[3]]) / new

print(as.character(part2))
