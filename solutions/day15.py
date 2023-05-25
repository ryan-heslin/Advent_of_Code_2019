from collections import deque
from functools import cache
from itertools import chain
from operator import attrgetter

from utils import intcode as ic
from utils.utils import split_commas


# n, s, w, e
movements = {
    -1j: 1,
    1j: 2,
    -1: 3,
    1: 4,
}
real = attrgetter("real")
imag = attrgetter("imag")


def display(coords, walls):
    combined = list(chain(coords, walls))
    xmin = int(min(combined, key=real).real)
    xmax = int(max(combined, key=real).real)
    ymin = int(min(combined, key=imag).imag)
    ymax = int(max(combined, key=imag).imag)
    return "\n".join(
        "".join(
            "O"
            if complex(x, y) == system
            else "#"
            if complex(x, y) in walls
            else "."
            if complex(x, y) in coords
            else " "
            for x in range(xmin, xmax + 1)
        )
        for y in range(ymin, ymax + 1)
    )


@cache
def neighbors(coord):
    return (coord - 1, coord + 1, coord - 1j, coord + 1j)


def explore(program, start):
    position = start
    explored = set()
    walls = set()
    path = deque()
    part1 = system = None
    found = False

    gen = program.eval()
    next(gen)

    while True:
        # print(position)
        for shift, code in movements.items():
            target = position + shift
            # print(position)
            if (not len(path) or shift != -path[-1]) and not (
                target in walls or target in explored
            ):
                gen.send((code,))
                result = program.output[-1]
                if result == 0:
                    walls.add(target)
                else:
                    position = target
                    path.append(shift)
                    if not found and result == 2:
                        found = True
                        system = position
                        part1 = len(path)
                    break
                    # Found target
            # Backtrack!
            # Exploration complete
        else:
            explored.add(position)
            if not path:
                break
            reversal = -path.pop()
            code = movements[reversal]
            # Reverses move, so always returns 1
            gen.send((code,))
            position += reversal

    return part1, explored, system, walls


# TODO Dijkstra to find furthest distance from oxygen?


def flood_fill(origin, walls):
    current = (origin,)
    minutes = 0
    done = set()

    while current:
        next = set()
        for coord in current:
            adjacent = neighbors(coord)
            for point in adjacent:
                if point not in done and point not in walls:
                    next.add(point)
                    # coords.remove(point)
        current = next
        minutes += bool(current)
        done.update(current)

    return minutes


code = ic.Program.parse(split_commas("inputs/day15.txt"))
program = ic.Program(code)
part1, visited, system, walls = explore(program, 0)
print(part1)

part2 = flood_fill(system, walls)
print(part2)
