import re
from functools import cache
from itertools import product

import utils.utils as ut
from utils import intcode as ic


def to_ascii(string):
    return map(ord, string)


def parse(output):
    x = y = 0
    x = -1
    newline = 10
    path = 35
    void = 46
    result = set()
    start = None
    for num in output:
        if num == newline:
            x = -1
            y += 1j
        else:
            x += 1
            if num != void:
                coord = x + y
                if num != path:
                    start = (coord, num)
                result.add(coord)
    return result, start


def verify_path(origin, direction, coords, path):
    position = origin
    traversed = set((origin,))

    while path:
        current = path.pop(0)
        if current == "L":
            direction = complex(direction.imag, -direction.real)
        elif current == "R":
            direction = complex(-direction.imag, direction.real)
        else:
            for _ in range(0, int(current)):
                position += direction
                assert position in coords
                traversed.add(position)
    assert traversed == coords


def parse2(output):
    x = y = 0
    x = -1
    newline = 10
    void = 46
    result = {}
    for num in output:
        if num == newline:
            x = -1
            y += 1j
        else:
            x += 1
            if num != void:
                coord = x + y
                result[coord] = chr(num)
    return result


def display(coords):
    xmin = int(min(coords, key=ut.real).real)
    xmax = int(max(coords, key=ut.real).real)
    ymin = int(min(coords, key=ut.imag).imag)
    ymax = int(max(coords, key=ut.imag).imag)
    xes = range(xmin, xmax + 1)

    return "\n".join(
        "".join(coords.get(complex(x, y), " ") for x in xes)
        for y in range(ymin, ymax + 1)
    )


def make_neighbors(xmin, xmax, ymin, ymax):
    @cache
    def neighbors(coord):
        x = coord.real
        y = coord.imag
        result = set()
        if x > xmin:
            result.add(coord - 1)
        if x < xmax:
            result.add(coord + 1)
        if y > ymin:
            result.add(coord - 1j)
        if y < ymax:
            result.add(coord + 1j)
        return result

    return neighbors


def calibrate(coords):

    result = 0
    for coord in coords:
        this_neighbors = neighbors(coord)
        if len(this_neighbors) == 4 and len(this_neighbors & coords) == 4:
            result += coord.real * coord.imag
    return result


def follow(coords, origin, direction):

    directions = {
        -1: {-1j: "R", 1j: "L"},
        1: {1j: "R", -1j: "L"},
        -1j: {1: "R", -1: "L"},
        1j: {-1: "R", 1: "L"},
    }
    movements = []
    position = origin
    displacement = 0

    while True:
        next = position + direction
        # Hit corner or end
        if next not in coords:
            movements.append(str(displacement))
            options = directions[direction]

            for new_direction, char in options.items():
                if position + new_direction in coords:
                    direction = new_direction
                    movements.append(char)
                    displacement = 0
                    break
            else:
                # Hit end
                break
        else:
            displacement += 1
            position = next
    return movements[1:]


def translate_match(match):
    original = match.string
    codes = ("A", "B", "C")
    for i, g in enumerate(match.groups()):
        original = re.sub(g, codes[i], original)
    return re.sub(",+", ",", ",".join(original))


def make_functions(directions, limit=20):
    def format_regex(x, y, z):
        # I apologize
        return r"{}".format(
            f"^([LR\\d,]{{{x}}}),\\1*([LR\\d,]{{{y}}}),(?:(?:\\1|\\2),)*([LR\\d,]{{{z}}}),(?:(?:\\1|\\2|\\3),)+(?:\\1|\\2|\\3)$"
        )

    iter = range(limit, 0, -1)
    combos = product(iter, iter, iter)
    for combo in combos:
        regex = format_regex(*combo)

        if m := re.match(regex, directions):
            replacements = translate_match(m)
            if len(replacements) <= limit:
                return replacements, m.groups()


code = ic.Program.parse(ut.split_commas("inputs/day17.txt"))
program = ic.Program(code)
gen = program.eval(False)
next(gen)
output = program.output

coords, start = parse(output)
start, orientation = start
neighbors = make_neighbors(
    ut.xmin(coords), ut.xmax(coords), ut.ymin(coords), ut.ymax(coords)
)

part1 = int(calibrate(coords))
print(part1)

directions = {60: -1, 62: 1, 94: -1j, 118: 1j}
orientation = directions[orientation]
movements = follow(coords, start, orientation)
# verify_path(start, orientation, coords, movements)
instructions = ",".join(movements)
grouping, groups = make_functions(instructions)

newline = ord("\n")

functions = to_ascii(grouping)
program[0] = 2


# Correct input causes fail
main = list(to_ascii(grouping))
main.append(newline)
functions = list(to_ascii("\n".join(groups) + "\n"))
end = [ord("n"), newline]
routine = main + functions + end

next(gen)
gen.send(routine)

part2 = max(program.output)
print(part2)
