from collections import defaultdict
from collections import deque
from functools import cache
from math import inf
from queue import PriorityQueue

from utils.utils import split_lines

ALPHABET = "abcdefghijklmnopqrstuv"


class State:
    def __init__(self, opened, distance, positions) -> None:
        self.opened = opened
        self.distance = distance
        self.positions = positions

    def __repr__(self):
        return (self.opened, self.distance, self.positions).__repr__()

    def update(self, new_key, new_dist, new_position):
        return self.__class__(
            self.opened + (new_key,), self.distance + new_dist, new_position
        )

    def __lt__(self, other):
        own_opened = len(self.opened)
        other_opened = len(other.opened)
        return (
            own_opened > other_opened
            or own_opened == other_opened
            and self.distance < other.distance
        )

    def __hash__(self):
        return hash((self.opened, self.positions))


def sort_complex(x):
    return sorted(x, key=lambda c: (c.imag, c.real))


def overwrite_center(graph, new_center, origin):
    parsed = new_center.splitlines()
    xlen = len(parsed[0])
    ylen = len(parsed)
    center = complex(xlen // 2, ylen // 2)
    origins = set()

    for y, line in enumerate(parsed):
        for x, char in enumerate(line):
            coord = complex(x, y)
            offset = coord - center
            target = origin + offset
            if char != "@":
                if target in graph:
                    graph.pop(target)
            else:
                origins.add(target)

    return graph, tuple(sort_complex(origins))


def parse(lines):
    result = {}
    keys = {}
    origin = None

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char != "#":
                coord = complex(x, y)
                if char.isalpha():
                    # All key locations
                    if char.lower() == char:
                        keys[char] = coord
                    result[coord] = char
                elif char == ".":
                    result[coord] = ""
                elif char == "@":
                    result[coord] = ""
                    origin = coord

    return result, keys, origin


def make_neighbors(coords):
    # Reading order
    shifts = (-1j, -1, 1, 1j)

    # Ignores if units in neighbors
    @cache
    def result(x):
        return set(x + shift for shift in shifts if x + shift in coords.keys())

    return result


def all_shortest_paths(source, goal, graph, exclusions, neighbors):

    dist = defaultdict(lambda: inf)
    dist[source] = 0

    # Store options in prev, recover original by reverse iteration?
    prev = defaultdict(set)
    shortest_dist = inf
    queue = deque([source])
    visited = set()

    while queue:
        current = queue.pop()
        current_dist = dist[current]
        if current_dist > shortest_dist or graph[current] in exclusions:
            continue
        if current == goal:
            shortest_dist = min(shortest_dist, current_dist)
            continue

        alt = current_dist + 1

        for neighbor in neighbors(current):
            if alt < dist[neighbor]:
                prev[neighbor] = {current}
                dist[neighbor] = alt
            # Alternate path found
            elif alt == dist[neighbor]:
                prev[neighbor].add(current)
            # assert alt < dist[neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.appendleft(neighbor)

    return shortest_dist, prev


# Try to find shortest path given opened doors
def confirm_path(paths, graph, source, goal, opened):
    queue = deque([goal])

    while queue:
        next = queue.popleft()
        if next == source:
            return True
        # Is it okay if all shortest paths pass through other unlocked keys?
        char = graph[next]
        if next != goal and char.isalpha() and not char.lower() in opened:
            continue
        before = paths[next]
        queue.extendleft(before)

    return False


# For storing best values
def sort_trailing(data):
    return tuple(sorted(data[:-2]) + [data[-1]])


# Group keys by quadrant
def categorize_keys(letters, midpoint):
    result = {0: set(), 1: set(), 2: set(), 3: set()}
    # Reading order
    for letter, coord in letters.items():
        if coord.real < midpoint:
            if coord.imag < midpoint:
                result[0].add(letter)
            else:
                result[2].add(letter)
        else:
            if coord.imag < midpoint:
                result[1].add(letter)
            else:
                result[3].add(letter)

    return result


def replace_tuple(x, i, replacement):
    return x[:i] + (replacement,) + x[i + 1 :]


# Just track bots separately, treat original as special case
def find_shortest(origins, graph, keys, quadrants, neighbors):
    chars = "".join(sorted(keys.keys()))
    n_keys = len(chars)
    n_origins = len(origins)
    doors = set(chars.upper())
    all_keys = set(chars)
    queue = PriorityQueue()
    dist = defaultdict(lambda: inf)
    shortest_dist = inf
    pairs = {}
    empty = set()
    visited = set()

    # Find all possible first keys for each origin
    # How to consistently order?
    # breakpoint()
    for i, origin in enumerate(origins):
        # All possible chars
        this_chars = quadrants[i]
        for char in this_chars:
            endpoint = keys[char]
            distance, _ = all_shortest_paths(origin, endpoint, graph, doors, neighbors)
            # Path accessible from start
            if distance < inf and confirm_path(_, graph, origin, endpoint, empty):
                start_positions = replace_tuple(origins, i, endpoint)
                state = State(char, distance, replace_tuple(origins, i, endpoint))
                queue.put(state, block=False)
                dist[(char, start_positions)] = distance

    while queue.qsize():
        # Repeat expansion procuedre for each bot, sticking to coords it can acess
        # Make opened a dict with keys for each bot
        current = queue.get(block=False)
        visited.add(current)
        if current.distance >= shortest_dist:
            continue
        # Found goal
        if len(current.opened) == n_keys:
            shortest_dist = min(shortest_dist, current.distance)
            print(shortest_dist)
            print(queue.qsize())
            continue
        # current_key = current.opened[-1]

        # Maybe just return best if queue exceeds certain length
        for i in range(n_origins):
            # Doors still closed
            done = set(current.opened)
            remaining = quadrants[i] - done
            # All keys found in this quadrant, so nothing to do
            # if not len(remaining):
            #     continue

            # Hash to tuple of all bots' keys
            for new_key in remaining:
                # pair = (current_key, new_key)
                current_position = current.positions[i]
                # TODO cache this based on start position, remaining keys
                distance, _ = all_shortest_paths(
                    current_position,
                    keys[new_key],
                    graph,
                    (remaining | set(map(str.upper, remaining))) - {new_key},
                    neighbors,
                )
                # pairs[pair] = [distance, paths, required]
                # distance, paths, required = pairs[pair]
                # Optimize to record minimum opened doors needed for a path to exist
                if distance < inf:

                    # Must beat any other path to this key
                    # Might not be correct for multi-bot case, since other bots'
                    # positions not sorted
                    # breakpoint()
                    new_positions = replace_tuple(current.positions, i, keys[new_key])
                    hash = (
                        "".join(set(current.opened)),
                        new_positions,
                    )
                    if (
                        new_distance := current.distance + distance
                    ) < inf and new_distance < dist[hash]:
                        dist[hash] = new_distance
                        new_keys = current.opened + new_key
                        new_state = State(
                            new_keys,
                            new_distance,
                            new_positions,
                        )
                        if new_state not in visited:
                            queue.put(new_state, block=False)

    return shortest_dist


raw_input = split_lines("inputs/day18.txt")
graph, keys, origin = parse(raw_input)
if origin is None:
    raise ValueError
midpoint = origin.real
neighbors = make_neighbors(graph)
part1 = find_shortest((origin,), graph, keys, {0: set(keys.keys())}, neighbors)
print(part1)

new_center = """@#@
###
@#@
"""


new_graph, origins = overwrite_center(graph, new_center, origin)
# new_graph, keys, _ = parse(split_lines("inputs/day18test.txt"))
# midpoint =
# origins = (6 + 2j, 8 + 2j, 6 + 4j, 8 + 8j)
neighbors = make_neighbors(new_graph)
quadrants = categorize_keys(keys, midpoint)
# quadrants = {0: {"d"}, 1: {"a"}, 2: {"b"}, 3: {"c"}}
part2 = find_shortest(origins, new_graph, keys, quadrants, neighbors)
# Track total distance, discard if behind best
# Track permutations visited
# FOr paths from start node, treat all doors as blocked
# FOr key in keys:
# while unexplored
# if all keys found:
# Mark shortest length
# if key not found
#   if path from this node to key not explored:
# paths[(current, key)] := explore_path(current, key)
# obstructions[(current, key)] := find_obstructions(paths)
# Shortest path viable
# if any (keys already found) in obstructions[(current, key)]
# add node with already explored and new distance and new key to neighbors
# Take path if any of obstructing doors open
