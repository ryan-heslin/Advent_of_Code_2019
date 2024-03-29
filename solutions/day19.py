from itertools import product

import utils.utils as ut
from utils import intcode as ic


def solve(code, side):
    min_threshold = 50

    # If 10 or more in a row, note start and end

    ranges = {}
    x = y = count = x_start = x_end = scan_width = 0
    while scan_width < int(side * 3):
        xes = []
        scan_start = x_start
        scan_end = x_end + 5
        scan_width = scan_end - scan_start

        for x in range(scan_start, scan_end):
            pair = (x, y)
            program = ic.Program(code, input=pair)
            gen = program.eval(False)
            next(gen)
            result = program.output[0]
            if result:
                xes.append(x)
                if x < min_threshold and y < min_threshold:
                    count += 1
                    x_start = x
        if xes != []:
            x_start = xes[0]
            x_end = xes[-1]
        ranges[y] = (x_start, x_end)
        y += 1
    return ranges, count


def find_square(ranges, side):
    for y, rnge in ranges.items():
        left, right = rnge
        endpoint = right - side + 1
        if left is not None and right - left >= side - 1:
            # All 9 rows below don't go beyond bounds
            lower = y + side - 1
            bottom = ranges.get(lower)
            if not lower:
                break
            if right <= bottom[1] and endpoint >= bottom[0]:
                return y, rnge
    return None, None


def display(plot):
    return "\n".join(
        "".join("#" if plot[(x, y)] else "." for x in range(50)) for y in range(50)
    )


def display_ranges(ranges):
    dots = "." * 100
    result = []
    for y in range(100):
        data = ranges.get(y, (None, None))
        if data[0] is not None:
            result.append(
                dots[: data[0]] + ("#" * (data[1] - data[0] + 1)) + dots[data[1] + 1 :]
            )
        else:
            result.append(dots)
    return "\n".join(result)


side = 100
dim = 50
input = product(range(dim), range(dim))
code = ic.Program.parse(ut.split_commas("inputs/day19.txt"))
ranges, part1 = solve(code, side)
print(part1)

y, rnge = find_square(ranges, side)
assert  rnge
part2 = (rnge[1] - side + 1) * 10000 + y
print(part2)
