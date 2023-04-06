from collections import defaultdict
from collections import deque
from functools import cache
from math import inf
from queue import PriorityQueue

from utils.utils import split_lines

ALPHABET = "abcdefghijklmnopqrstuv"


class State:
    def __init__(self, opened, distance, position) -> None:
        self.opened = opened
        self.distance = distance
        self.position = position

    def __repr__(self):
        return (self.opened, self.distance, self.position).__repr__()

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


def all_shortest_paths(source, goal, graph, exclusions):

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
        if graph[next].isupper() and not graph[next].lower() in opened:
            continue
        if next == source:
            return True
        before = paths[next]
        queue.extendleft(before)

    return False


# For storing best values
def sort_trailing(data):
    return tuple(sorted(data[:-2]) + [data[-1]])


# Just track bots separately, treat original as special case
def find_shortest(origin, graph, keys):
    chars = "".join(sorted(keys.keys()))
    n_keys = len(chars)
    doors = set(chars.upper())
    all_keys = set(chars)
    queue = PriorityQueue()
    dist = defaultdict(lambda: inf)
    shortest_dist = inf
    pairs = {}

    # Find all possible first keys
    for char in chars:
        endpoint = keys[char]
        distance, _ = all_shortest_paths(origin, endpoint, graph, doors)
        # Path accessible from start
        if distance < inf:
            state = State(char, distance, endpoint)
            queue.put(state, block=False)
            dist[char] = distance

    empty = set()
    while queue.qsize():
        current = queue.get(block=False)
        if current.distance >= shortest_dist:
            continue
        # Found goal
        if len(current.opened) == n_keys:
            shortest_dist = min(shortest_dist, current.distance)
            print(shortest_dist)
            continue
        # Maybe optimize this to only run once per combination
        current_key = current.opened[-1]
        # Doors still closed
        remaining = all_keys - set(current.opened)

        for new_key in remaining:
            pair = (current_key, new_key)
            if pair not in pairs:
                distance, paths = all_shortest_paths(
                    keys[current_key], keys[new_key], graph, empty
                )
                pairs[pair] = (distance, paths)
            else:
                distance, paths = pairs[pair]
            if distance < inf and confirm_path(
                paths, graph, current.position, keys[new_key], current.opened
            ):
                # Must beat any other path to this key
                new_keys = current.opened + new_key
                hash = tuple(sorted(current.opened)) + (new_key,)
                if (
                    new_distance := current.distance + distance
                ) < inf and new_distance < dist[hash]:
                    dist[hash] = new_distance
                    new_state = State(new_keys, new_distance, keys[new_key])
                    queue.put(new_state, block=False)

    return shortest_dist


raw_input = split_lines("inputs/day18.txt")
graph, keys, origin = parse(raw_input)
neighbors = make_neighbors(graph)
part1 = find_shortest(origin, graph, keys)
print(part1)
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
