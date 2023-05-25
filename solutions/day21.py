import utils.utils as ut
from utils import intcode as ic

# A, B, C, D detect gap 1, 2, 3, 4 spaces ahead
ASCII_A = 65
NEWLINE = ord("\n")


def translate(lines, command):
    return list(map(ord, lines)) + list(map(ord, command + "\n"))


lines = """NOT A J
NOT B T
AND T J
NOT C T
AND T J
AND D J
"""

# Jumps 4 blocks, so check if  4 blocks away safe
part1_lines = """NOT A J
NOT B T
OR T J
NOT C T
OR T J
AND D J
"""

# One gap or more in three tiles ahead
# Landing point solid, and either followed by solid, or with another solid landing point in reach
part2_lines = """NOT A T
OR T J
NOT B T
OR T J
NOT C T
OR T J
AND D T
AND E T
OR H T
AND D J
AND T J
"""


part1_input = translate(part1_lines, "WALK")
part2_input = translate(part2_lines, "RUN")
code = ic.Program.parse(ut.split_commas("inputs/day21.txt"))
program = ic.Program(code)
gen = program.eval(False)
program.update(part1_input)
next(gen)

print(max(program.output))

program = ic.Program(code)
gen = program.eval(False)
program.update(part2_input)
next(gen)
part2 = max(program.output)
print(part2)
