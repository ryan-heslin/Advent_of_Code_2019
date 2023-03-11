from utils.intcode import Program
from utils.utils import split_commas


def find_values(code, target):
    replacements = {1: 0, 2: 0}

    for _ in range(100):
        for _ in range(100):
            this = Program(code).modify(replacements)
            try:
                this.eval()
                if this.code[0] == target:
                    return replacements.values()
            except:
                pass
            replacements[2] += 1
        replacements[1] += 1
        replacements[2] = 0
    return (0, 0)


code = Program.parse(split_commas("inputs/day2.txt"))
program = Program(code).modify({1: 12, 2: 2})
program.eval()
part1 = program.code[0]
print(part1)

noun, verb = find_values(code, 19690720)
part2 = noun * 100 + verb
print(part2)
