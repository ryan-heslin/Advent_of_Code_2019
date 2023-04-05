from functools import reduce

import utils.utils as ut
from utils import intcode as ic

# A, B, C, D detect gap 1, 2, 3, 4 spaces ahead
ASCII_A = 65
NEWLINE = ord("\n")


def translate(lines):
    return list(map(ord, lines)) + list(map(ord, "WALK\n"))
    # lines = [[ord(chr) for chr in line] for line in lines]
    # return reduce(lambda x, y: x + [NEWLINE] + y, lines)


lines = """NOT A J
NOT B T
AND T J
NOT C T
AND T J
AND D J
"""

# lines = "NOT A J\n"
# Jumps 4 blocks, so check if  4 blocks away safe
lines = """NOT A J
NOT B T
OR T J
NOT C T
OR T J
NOT D T
AND D J
"""

input = translate(lines)
code = ic.Program.parse(ut.split_commas("inputs/day21.txt"))
program = ic.Program(code)
gen = program.eval(False)
program.update(input)
next(gen)
# next(gen)
# next(gen)
# next(gen)

print("".join(map(chr, program.output)))
