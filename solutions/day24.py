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
    return frozenset(result)


def display(num):
    string = bin(num)[2:]
    string = string.zfill(25)
    string = string.translate(string.maketrans({"0": ".", "1": "#"}))
    return "\n".join(string[i : i + 5] for i in range(0, 25, 5))


def display_tuple(x):
    transformed = "".join("#" if el else "." for el in x)
    return "\n".join(transformed[i : i + 5] for i in range(0, 25, 5))


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
    if x > (center * 2) - ncol:
        result.add(center + ncol)
    return frozenset(result)


def simulate(start, neighbors):
    seen = {start}
    repeat = False
    state = start
    size = len(neighbors)

    while not repeat:
        result = []
        for i in reversed(range(size)):
            status = state[i]
            # Read status
            # state >>= 1
            adjacent = (state[pos] for pos in neighbors[i])
            s = sum(adjacent)

            result.append((not status and (s == 1 or s == 2)) or (status and s == 1))
        state = tuple(result)
        repeat = state in seen
        seen.add(state)

    return sum(2**i * el for i, el in enumerate(state))


def recursive_simulate(start, neighbors, iterations=200):
    initial = 0
    state = [start]
    size = 25
    middle = size // 2
    empty = tuple(False for _ in range(size))
    # Skip middle bit due to recursion

    for _ in range(iterations):
        if sum(state[0]) != 0:
            state.insert(0, empty)
        if sum(state[-1]) != 0:
            state.append(empty)

        end = len(state) - 1
        updated = [None] * (end + 1)
        for i, board in enumerate(state):
            result = [False] * size
            for j in reversed(range(size)):
                # Read digit
                # Ignore this space, since it represents inner board
                if j == middle:
                    continue
                status = board[j]
                adjacent = []

                # Inner
                if i < end:
                    adjacent.extend(state[i + 1][pos] for pos in neighbors[1][j])
                adjacent.extend(board[pos] for pos in neighbors[0][j])
                # Outer (list goes from outer to inner)
                if i > initial:
                    adjacent.extend(state[i - 1][pos] for pos in neighbors[-1][j])
                s = sum(adjacent)

                result[j] = (not status and (s == 1 or s == 2)) or (status and s == 1)
            updated[i] = result
        state = updated

    return sum(map(sum, state))


with open("inputs/day24.txt") as f:
    raw_input = f.read().rstrip("\n")

nrow = raw_input.count("\n") + 1
ncol = raw_input.index("\n")
parsed = raw_input.replace("\n", "")
parsed = parsed.translate(parsed.maketrans({"#": "1", ".": "0"}))
start = tuple([bool(int(x)) for x in parsed])

# These are 1-indexed digit positions
neighbors = [get_neighbors(num, nrow, ncol) for num in range(len(parsed))]

part1 = simulate(start, neighbors)
print(part1)

size = nrow * ncol
iter_range = lambda: chain(range(size // 2), range(size // 2 + 1, size))

frame_neighbors = {x: get_neighbors(x, nrow, ncol, True) for x in iter_range()}

# Neighbors on inner grid
inner_neighbors = defaultdict(lambda: frozenset())
inner_neighbors.update(
    {
        7: frozenset(range(0, 5)),
        11: frozenset(range(0, 25, 5)),
        13: frozenset(range(4, 29, 5)),
        17: frozenset(range(20, 25)),
    }
)
# Neighbors on outer grid
outer_neighbors = {x: get_outer_neighbors(x, nrow, ncol) for x in iter_range()}
# -1 is outer, 1 inner
neighbors = {-1: outer_neighbors, 0: frame_neighbors, 1: inner_neighbors}
part2 = recursive_simulate(start, neighbors, iterations=200)
print(part2)
