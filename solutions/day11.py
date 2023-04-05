from collections import defaultdict
from operator import attrgetter

import utils.intcode as ic
from utils.utils import split_commas

real = attrgetter("real")
imag = attrgetter("imag")


def display(coords):
    replacements = {0: " ", 1: "#"}
    xmin = int(min(panels.keys(), key=real).real)
    xmax = int(max(panels.keys(), key=real).real)
    ymin = int(min(panels.keys(), key=imag).imag)
    ymax = int(max(panels.keys(), key=imag).imag)

    return "\n".join(
        "".join(
            replacements[coords[complex(x, y)]] for x in reversed(range(xmin, xmax + 1))
        )
        for y in range(ymin, ymax + 1)
    )


def paint(code, start):
    # left 90, right 90
    rotations = (lambda x: complex(-x.imag, x.real), lambda x: complex(x.imag, -x.real))
    # up
    orientation = -1j
    program = ic.Program(code=code)
    gen = program.eval(False)
    next(gen)
    panels = defaultdict(lambda: 0)
    painted = set()
    position = 0
    panels[position] = start
    result = False

    while result != ic.Exit.COMPLETE:
        # print(panels[position])
        result = gen.send((panels[position],))
        # Need 2 outputs
        # next(gen)
        # done = program.eval()
        color, direction = program.output[-2:]
        # program.clear()
        panels[position] = color
        painted.add(position)
        orientation = rotations[direction](orientation)
        position += orientation

    return panels, painted


code = ic.Program.parse(split_commas("inputs/day11.txt"))
_, part1 = paint(code, 0)

print(len(part1))
panels, _ = paint(code, 1)
print(display(panels))
