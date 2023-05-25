from collections import defaultdict
from math import inf
from queue import PriorityQueue

from utils.utils import split_lines


def complex2tuple(x):
    return (int(x.real), int(x.imag))


def parse(lines, single=None):
    neighbors = defaultdict(lambda: set())
    directions = (-1j, 1, 1j, -1)
    portals = {}
    margin = 2
    cutoff = 1 - margin
    conversion = complex(-margin, -margin)
    xmin = ymin = 0
    xmax = ymax = len(raw_input) - (margin * 2) - 1

    def is_outer(coord):
        return (
            coord.real == xmin
            or coord.real == xmax
            or coord.imag == ymin
            or coord.imag == ymax
        )

    for y, line in enumerate(lines[:cutoff]):
        for x, char in enumerate(line[:cutoff]):
            coord = complex(x, y)
            converted_coord = coord + conversion

            if char == ".":
                # For each neighbor of char:
                for direction in directions:
                    neighbor = coord + direction
                    converted_neighbor = neighbor + conversion
                    neighbor_char = lines[int(neighbor.imag)][int(neighbor.real)]

                    if neighbor_char == ".":
                        neighbors[converted_coord].add(converted_neighbor)
                    elif neighbor_char.isalpha():
                        next_neighbor = (
                            neighbor + direction
                        )  # Keep moving that direction
                        next_char = lines[int(next_neighbor.imag)][
                            int(next_neighbor.real)
                        ]
                        # Add other letter to form name, reversing if right or down
                        name = (
                            neighbor_char + next_char
                            if direction in (1, 1j)
                            else next_char + neighbor_char
                        )
                        if single and name not in single:
                            key = name if is_outer(converted_coord) else name.lower()
                            portals[key] = converted_coord

                            # Add each endpoint as other's neighbors
                            # If both endpoints known:
                            if portals.get(other := key.swapcase()):
                                neighbors[portals[key]].add(portals[other])
                                neighbors[portals[other]].add(portals[key])
                        else:
                            portals[name] = converted_coord
    return neighbors, portals


def dijkstra(graph, start, follow_portals=True):
    i = 0

    dist = defaultdict(lambda: inf)
    dist[start] = 0

    Q = PriorityQueue()
    Q.put((dist[start], i, start), block=False)

    while Q.qsize():
        cost, _, current_node = Q.get(block=False)
        for neighbor in graph[current_node]:
            alt = cost + 1
            if (follow_portals or abs(neighbor - current_node) == 1) and alt < dist[
                neighbor
            ]:
                i += 1
                dist[neighbor] = alt
                Q.put((alt, i, neighbor), block=False)
    dist.pop(start)
    return dist


def recurse_dijkstra(graph, start, goal, depths):

    dist = defaultdict(lambda: inf)
    dist[(start, 0)] = depth = i = 0

    Q = PriorityQueue()
    Q.put((dist[(start, 0)], depth, i, start), block=False)

    while Q.qsize():
        cost, depth, _, current_node = Q.get(block=False)
        if current_node == goal and depth == 0:
            return cost

        delta_depth = depths[current_node]
        for neighbor, distance in graph[current_node].items():
            # In outermost layer, so can't move outward
            if depth == 0 and distance == 1 and delta_depth == -1:
                continue
            alt = cost + distance
            new_depth = depth
            if distance == 1:  # stepping through portal, so changing recursion level
                new_depth += depths[current_node]

            record = (neighbor, new_depth)
            if alt < dist[record]:
                i += 1
                dist[record] = alt
                Q.put((alt, new_depth, i, neighbor), block=False)

    return inf


def connect_portals(portals, graph):
    connections = defaultdict(lambda: {})
    targets = set(portals.values())
    done = set()

    for source in targets:
        if True or source not in done:
            result = dijkstra(graph, source, follow_portals=False)
            done.add(source)
            for node, distance in result.items():
                if node in targets:
                    done.add(node)
                    connections[source][node] = distance
                    connections[node][source] = distance

    # Missing nodes are inaccessible at either end
    return connections


raw_input = split_lines("inputs/day20.txt")
start = "AA"
end = "ZZ"
endpoints = (start, end)
graph, portals = parse(raw_input, endpoints)
start_coord = portals[start]
end_coord = portals[end]
part1 = dijkstra(graph, start_coord)[end_coord]
print(part1)

connections = connect_portals(portals, graph)
depths = {}
for name, node in portals.items():
    if name not in endpoints:
        if name == name.lower():
            depths[node] = 1
        else:
            depths[node] = -1
        other = name.swapcase()
        other_coord = portals[other]
        connections[other_coord][node] = 1
        connections[node][other_coord] = 1

depths[start_coord] = depths[end_coord] = 0
part2 = recurse_dijkstra(connections, start_coord, end_coord, depths)
print(part2)
