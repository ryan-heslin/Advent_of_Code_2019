from collections import defaultdict
from functools import lru_cache
from itertools import chain


# Reversed, 0-indexed, counting down from top left, like number digits
def get_neighbors(x, nrow, ncol, remove_middle=False):
    result = set()
    if x >= ncol:
        result.add(x - ncol)
    if x < (nrow - 1) * ncol:
        result.add(x + ncol)
    if (x + 1) % ncol != 0:  # not left
        result.add(x + 1)
    if (x % ncol) != 0:  # not right
        result.add(x - 1)
    if remove_middle:
        result.discard((nrow * ncol) // 2)
    return result


# Cheating, but oh well
# Outer recursion level
def get_outer_neighbors(x, nrow, ncol):
    result = set()
    center = (nrow * ncol) // 2
    if x < nrow:  # bottom
        result.add(center - ncol)
    if x % ncol == 0:  # right
        result.add(center - 1)
    if (x + 1) % ncol == 0:
        result.add(center + 1)
    if x > center - ncol:
        result.add(center + ncol)
    return result


@lru_cache(maxsize=32)
def nth_digit(num, n):
    return (num >> n) % 2


def biodiversity(num, size):
    return sum(2 ** (size - i - 1) * nth_digit(num, i) for i in range(size - 1, -1, -1))


def hash(arr):
    return int("".join(map(str, arr)))


def simulate(start, neighbors):
    seen = {start}
    repeat = False
    state = start
    size = len(neighbors)

    while not repeat:
        reference = state
        result = 2
        for i in range(size):
            digit = state % 2
            # Read digit
            state >>= 1
            adjacent = (nth_digit(reference, pos) for pos in neighbors[i])
            s = sum(adjacent)

            result += (digit == 0 and (s == 1 or s == 2)) or (s == 1)
            result <<= 1
            print(bin(result))
        state = result >> 1
        repeat = state in seen
        seen.add(state)

    return biodiversity(state, size)


def recursive_simulate(start, neighbors, iterations=200):
    initial = 0
    state = [start]
    size = len(neighbors[0])
    # Skip middle bit due to recursion

    for _ in range(iterations):
        state.insert(0, initial)
        state.append(initial)
        for board, i in enumerate(state[1:-1]):
            pass
            # Check each coord's same-state, outer, and inner neighbors

    return sum(map(int.bit_count, state))


with open("inputs/day24.txt") as f:
    raw_input = f.read().rstrip("\n")

nrow = raw_input.count("\n") + 1
ncol = raw_input.index("\n")
parsed = raw_input.replace("\n", "")
parsed = parsed.translate(parsed.maketrans({"#": "1", ".": "0"}))
start = int(parsed, base=2)

# These are 1-indexed digit positions
neighbors = [get_neighbors(num, nrow, ncol) for num in range(len(parsed))]

part1 = simulate(start, neighbors)
print(part1)

size = nrow * ncol
iter_range = chain(range(size // 2), range(size // 2 + 1, size))
inner_neighbors = defaultdict(lambda: set())
inner_neighbors.update(
    {
        7: list(range(0, 5)),
        11: list(range(0, 25, 5)),
        13: list(range(4, 29, 5)),
        17: list(range(20, 25)),
    }
)
outer_neighbors = dict(zip(iter_range, map(get_outer_neighbors, iter_range)))
