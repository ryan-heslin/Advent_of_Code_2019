from collections import deque
from itertools import combinations

import utils.intcode as ic
from utils.utils import split_commas

NEWLINE = ord("\n")
SPACE = ord(" ")
DEADLY = (
    "molten lava",
    "infinite loop",
    "photons",
    "giant electromagnet",
    "escape pod",
)
DIRECTIONS = {"north": -1j, "south": 1j, "east": 1, "west": -1}
OPPOSITES = {"north": "south", "south": "north", "east": "west", "west": "east"}

# Find all items, then try all combinations until correct

# Record current path from origin at all times so each step can be reversed


def read_item(item):
    return item.lstrip("- ")


def read_line_options(parts, header):
    try:
        line = parts.index(header)
    except:
        return None

    line += 1
    result = []
    while parts[line].startswith("-"):
        result.append(read_item(parts[line]))
        line += 1
    return result


# List items present in a room
def parse_output(program):
    parts = [p for p in to_chars(program.output).splitlines() if len(p)]
    name = parts[0].strip("==").strip(" ")

    doors = items = None
    doors = read_line_options(parts, "Doors here lead:")
    items = read_line_options(parts, "Items here:")
    is_goal = name == "Security Checkpoint"
    program.clear()
    return {"doors": doors, "items": items, "is_goal": is_goal, "name": name}


def current_items(gen, program):
    gen.send(COMMANDS["inv"])
    items = to_chars(program.output)
    result = [read_item(item) for item in items if item.startswith("-")]
    program.clear()
    return result


def handle_items(gen, program, items, command):
    for item in items:
        gen.send(command + [SPACE] + to_ascii(item))
        # print(to_chars(program.output))
        program.clear()


def drop_all(gen, program, items):
    handle_items(gen, program, items, COMMANDS["drop"])


def try_combinations(gen, program, direction, items):
    n = len(items)
    drop_all(gen, program, items)
    command = COMMANDS[direction]

    for length in range(1, n + 1):
        combos = combinations(items, r=length)
        for combo in combos:
            handle_items(gen, program, combo, COMMANDS["take"])
            gen.send(command)
            result = to_chars(program.output).splitlines()

            if not any(
                line.startswith('A loud, robotic voice says "Alert!') for line in result
            ):
                return int("".join(filter(str.isdigit, result[-1])))
            drop_all(gen, program, combo)
            program.clear()

    raise ValueError("No success")
    # handle_items(program, )


def follow_path(gen, program, path):
    for move in path:
        gen.send(COMMANDS[move])
        program.clear()


def find_password(program):
    current = 0
    current_path = deque([])
    paths_from_start = {}
    unexplored = {}

    gen = program.eval(False)
    next(gen)
    goal = goal_direction = direction = None
    items = set()

    while True:
        data = parse_output(program)
        current = data["name"]
        if current not in paths_from_start:
            paths_from_start[current] = tuple(current_path)
            if data["doors"]:
                unexplored[current] = [
                    d
                    for d in data["doors"]
                    if (not current_path or d != OPPOSITES[direction])
                ]
            if data["items"] and not any(item in DEADLY for item in data["items"]):
                items.update(data["items"])
                handle_items(gen, program, data["items"], COMMANDS["take"])
            if data["is_goal"]:
                goal = current
                assert len(unexplored[current]) == 1
                goal_direction = unexplored[current][0]
        program.clear()

        remaining = unexplored.get(current)
        if remaining:
            direction = remaining.pop()
            current_path.append(direction)
        # Fully explored, so backtrack
        else:
            direction = OPPOSITES[current_path.pop()]
        if not remaining:
            unexplored.pop(current, None)
        gen.send(COMMANDS[direction])
        # current += DIRECTIONS[direction]

        # Not backtracking, so append path
        # sleep(1)
        if goal is not None and not len(unexplored):
            break

    # All items retrieved, so go back to origin and toward goal
    current_path.reverse()
    follow_path(gen, program, [OPPOSITES[dir] for dir in current_path])
    follow_path(gen, program, paths_from_start[goal])
    return try_combinations(gen, program, goal_direction, items)


def to_ascii(text):
    return list(map(ord, text)) + [NEWLINE]


def to_chars(chars):
    return "".join(chr(c) for c in chars)


# For interactive use
def run(program):
    gen = program.eval(False)
    commands = {
        command[0]: command
        for command in ("north", "south", "east", "west", "take", "drop", "inv")
    }
    next(gen)
    print(to_chars(program.output))
    program.clear()

    while True:
        while True:
            new = input("Command: ")
            parts = new.split(" ")
            if parts[0] and commands.get(parts[0][0]):
                break
        parts[0] = commands.get(parts[0][0])
        gen.send(to_ascii(" ".join(parts)))
        print(to_chars(program.output))
        program.clear()


raw_input = split_commas("inputs/day25.txt")
program = ic.Program(code=ic.Program.parse(raw_input))
COMMANDS = {
    "north": to_ascii("north"),
    "south": to_ascii("south"),
    "east": to_ascii("east"),
    "west": to_ascii("west"),
    "inv": to_ascii("inv"),
    "take": to_ascii("take")[:-1],
    "drop": to_ascii("drop")[:-1],
}
part1 = find_password(program)
print(part1)
