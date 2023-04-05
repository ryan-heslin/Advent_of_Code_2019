import utils.intcode as ic
from utils.utils import split_commas


raw_input = split_commas("inputs/day9.txt")
code = ic.Program.parse(raw_input)

program = ic.Program(code, input=[1])
gen = program.eval(False)
next(gen)
part1 = program.output[-1]
print(part1)

program = ic.Program(code, input=[2])
gen = program.eval(False)
next(gen)
part2 = program.output[-1]
print(part2)
