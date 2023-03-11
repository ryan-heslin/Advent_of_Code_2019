from enum import Enum
from time import sleep

import utils.intcode as ic
import utils.utils as ut


class Graphics(Enum):
    SCORE = -1
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4


def draw(numbers, grid, ball=None, paddle=None, score=None):
    n_instructions = 3
    ball_found = paddle_found = False
    # Just follow the ball!
    PADDLE = Graphics.PADDLE.value
    EMPTY = Graphics.EMPTY.value
    SCORE = Graphics.SCORE.value
    BALL = Graphics.BALL.value

    for i in range(0, len(numbers), n_instructions):
        x, y, color = numbers[i : (i + n_instructions)]
        if x == SCORE and y == EMPTY:
            score = color
        else:
            coord = complex(x, y)
            grid[coord] = color
            if not ball_found and color == BALL:
                ball = coord
                ball_found = True
            elif not paddle_found and color == PADDLE:
                paddle = coord
                paddle_found = True

    return grid, ball, paddle, score


def play(code):
    code = dict(code)
    code[0] = 2
    program = ic.Program(code=code)
    BALL = Graphics.BALL.value
    BLOCK = Graphics.BLOCK.value
    replacements = {
        Graphics.EMPTY.value: " ",
        Graphics.WALL.value: "#",
        Graphics.BLOCK.value: "X",
        Graphics.PADDLE.value: "_",
        BALL: "O",
    }

    grid = {0: BLOCK}
    score = None
    # Runs to first read of empty input queue
    gen = program.eval(False)
    result = next(gen)
    ball = paddle = score = None

    while result != ic.Exit.COMPLETE:
        grid, ball, paddle, score = draw(program.output, grid, ball, paddle, score)
        # Just follow the ball!
        movement = (int(ball.real - paddle.real),)
        # print(movement)
        # print(program.output)
        # print(f"Score: {score}")
        # print(ut.display(grid, replacements, reverse=False))
        program.clear()
        # movement = None
        # while movement is None:
        #     movement = inputs.get(input("Move: "))
        result = gen.send(movement)
    _, _, _, result = draw(program.output, grid, ball, paddle, score)
    return result
    # sleep(1)
    # result = next(gen)
    # TODO:
    # First move under paddle, before direction established
    # Count until next impact
    # Feed that many of direction value
    # Get new direction
    # Repeat

    return score


code = ic.Program.parse(ut.split_commas("inputs/day13.txt"))
program = ic.Program(code)
gen = program.eval(False)
next(gen)
result = program.output

grid, _, _, _ = draw(result, {})
part1 = sum(v == Graphics.BLOCK.value for v in grid.values())
print(part1)


xmin = ymin = 0
xmax = int(max(grid.keys(), key=ut.real).real)
ymax = int(max(grid.keys(), key=ut.imag).imag)
part2 = play(code)
print(part2)
