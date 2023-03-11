import utils.intcode as ic
from utils.utils import split_commas

raw_input = split_commas("inputs/day5.txt")
code = ic.Program.parse(raw_input)
program = ic.Program(code=code, input=[1])
program.run_to_exhaustion()

output = program.output
part1 = output[-1]
print(part1)

program = ic.Program(code=code, input=[5])
program.run_to_exhaustion()
part2 = program.output[-1]
print(part2)
