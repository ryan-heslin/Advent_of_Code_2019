from fractions import Fraction
from itertools import chain
from math import copysign
from operator import itemgetter

from utils.utils import split_lines


def parse(lines):
    result = set()

    for j, line in enumerate(lines):
        for i, char in enumerate(line):
            if char == "#":
                result.add(complex(i, j))
    return result


def count_asteroids(point, asteroids, diags):
    # Limit to actual coordinates
    found = set()
    used = set()
    for offset in diags:
        if offset not in used:
            used.add(offset)
            current = point
            # Check every point along diagonal
            while xmin <= current.real <= xmax and ymin <= current.imag <= ymax:
                current += offset
                # If already known asteroid, abort, since it blocks view
                if current in asteroids:
                    if current not in found:
                        found.add(current)
                    break
    for offset in (1, -1, 1j, -1j):
        current = point
        while 0 <= current.real <= xmax and 0 <= current.imag <= ymax:
            current += offset
            if current in asteroids:
                found.add(current)
                break

    return len(found)


def create_diags(coord, xmax, ymax):
    x = int(coord.real)
    y = int(coord.imag)
    result = set()

    lower_x = -x
    upper_x = xmax - x
    lower_y = -y
    upper_y = ymax - y
    for dx in filter(lambda x: x != 0, range(lower_x, upper_x + 1)):
        for dy in filter(lambda x: x != 0, range(lower_y, upper_y + 1)):
            normalized = Fraction(dx, dy)
            num = copysign(normalized.numerator, dx)
            denom = copysign(normalized.denominator, dy)
            result.add(complex(num, denom))
    return result


def sort_quadrant(quadrant, key, initial):
    return [initial] + list(sorted(quadrant, key=key))


def order_diags(diags):
    # Order quadrants separately, going clockwise
    # Assume four cardinal directions absent to avoid dealing with zeroes
    plus_minus = set()
    plus_plus = set()
    minus_plus = set()
    minus_minus = set()

    for coord in diags:
        # Choose quadrant based on signs
        sgn_x = copysign(1, coord.real)
        sgn_y = copysign(1, coord.imag)

        if sgn_x == 1:
            if sgn_y == 1:
                plus_plus.add(coord)
            else:
                plus_minus.add(coord)
        else:
            if sgn_y == 1:
                minus_plus.add(coord)
            else:
                minus_minus.add(coord)

    plus_minus = sort_quadrant(plus_minus, lambda c: c.real / abs(c.imag), -1j)
    plus_plus = sort_quadrant(plus_plus, lambda c: c.imag / c.real, 1)
    minus_plus = sort_quadrant(minus_plus, lambda c: abs(c.real) / c.imag, 1j)
    minus_minus = sort_quadrant(minus_minus, lambda c: abs(c.imag) / abs(c.real), -1)
    return chain(plus_minus, plus_plus, minus_plus, minus_minus)


def destroy(asteroids, diags, center, xmin, xmax, ymin, ymax, target=200):
    i = 0

    while True:
        for diag in diags:
            current = center
            while xmin <= current.real <= xmax and ymin <= current.real <= ymax:
                current += diag
                if current in asteroids:
                    asteroids.remove(current)
                    i += 1
                    break
            if i == target:
                return current


def transform_coord(coord):
    return coord.real * 100 + coord.imag


raw_input = split_lines("inputs/day10.txt")
xmin = ymin = 0
xmax = len(raw_input[0]) - 1
ymax = len(raw_input) - 1

asteroids = parse(raw_input)
result = (
    (
        point,
        count_asteroids(point, asteroids, create_diags(point, xmax=xmax, ymax=ymax)),
    )
    for point in asteroids
)
station, part1 = max(result, key=itemgetter(1))
print(part1)

diags = order_diags(create_diags(station, xmax, ymax))
n_200 = destroy(asteroids, diags, station, xmin, xmax, ymin, ymax)
part2 = int(transform_coord(n_200))
print(part2)
