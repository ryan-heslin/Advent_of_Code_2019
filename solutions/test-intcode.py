#  Tests from Kache's post at https://www.reddit.com/r/adventofcode/comments/e8aw9j/2019_day_9_part_1_how_to_fix_203_error/
import utils.intcode as ic


def run_test(code, expected):
    code = dict(enumerate(code))
    print(code)
    program = ic.Program(code)
    gen = program.eval(False)
    next(gen)
    assert program.output == expected


data = [
    [[109, -1, 4, 1, 99], [-1]],
    [[109, -1, 104, 1, 99], [1]],
    [[109, -1, 204, 1, 99], [109]],
    [[109, 1, 9, 2, 204, -6, 99], [204]],
    [[109, 1, 109, 9, 204, -6, 99], [204]],
    [[109, 1, 209, -1, 204, -106, 99], [204]],
    [[109, 1, 3, 3, 204, 2, 99], []],
    [[109, 1, 203, 2, 204, 2, 99], []],
]

for pair in data:
    run_test(pair[0], pair[1])
