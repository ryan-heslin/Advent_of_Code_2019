from itertools import permutations
from math import inf

import utils.intcode as ic
from utils.utils import split_commas


def run_cycle(perm, code):
    last = 0
    programs = []
    for digit in perm:
        current = ic.Program(code, input=(last, digit))
        current.eval()
        last = current.output[-1]
        programs.append(current)
    return programs


def try_permutations(code, permutations):
    best = -inf

    for perm in permutations:
        result = run_cycle(perm, code)
        best = max(best, result[-1].output[-1])

    return best


def cycle_permutations(code, permutations):
    best = -inf
    for perm in permutations:
        programs = run_cycle(perm, code)
        last_value = None
        previous = programs[-1].output[-1]

        # Final value on final halt is returned
        while last_value is None:
            for program in programs:
                program.update([previous])
                # True only if halt code encountered
                last_value = program.eval()
                previous = program.output[-1]
        best = max(best, previous)
    return best


# For part 2, feed phase inputs only first time: thereafter, input signals

raw_input = split_commas("inputs/day7.txt")
code = ic.Program.parse(raw_input)
n_amplifiers = 5
perms = permutations(range(n_amplifiers))
part1 = try_permutations(code, perms)
print(part1)

part2 = cycle_permutations(code, permutations(range(n_amplifiers, n_amplifiers * 2)))
print(part2)
