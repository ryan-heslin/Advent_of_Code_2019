from utils.utils import split_lines
from collections import defaultdict
from math import ceil


class Reaction:
    def __init__(self, inputs, outputs) -> None:
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self) -> str:
        return (self.inputs, self.outputs).__repr__()


def reaction_start(n=1):
    result = defaultdict(lambda: 0)
    result["FUEL"] = -n
    return result


def parse_line(line):
    inputs, output = line.split(" => ")
    inputs = inputs.split(", ")
    amounts = {}
    for input in inputs:
        num, el = input.split(" ")
        num = int(num)
        amounts[el] = num
    output = output.split(" ")
    rhs = output[1]
    return rhs, Reaction(amounts, {output[1]: int(output[0])})


def topo_sort(reactions, root):
    order = []
    S = {root}
    done = set()

    while S:
        n = S.pop()
        order.append(n)
        if n in reactions:
            print(reactions[n].inputs.keys())
            new = reactions[n].inputs.keys() - done
            S.update(new)
            done.update(new)
    return order


def calculate_ore(state, reactions):
    unfinished = True
    while unfinished:
        unfinished = False
        for element in set(state.keys()):
            amount = state[element]
            if element != "ORE" and amount < 0:
                unfinished = True
                reaction = reactions[element]
                n = ceil(abs(amount) / reaction.outputs[element])
                state[element] += (n + (element == "FUEL")) * reaction.outputs[element]

                for input_el, input_quantity in reaction.inputs.items():
                    state[input_el] -= n * input_quantity

    return -state["ORE"]


def binary_search(reactions, low, high):
    target = high
    while low < high:
        mid = (low + high) // 2
        new = calculate_ore(reaction_start(mid), reactions)
        if new < target:
            low = mid + 1
        else:
            high = mid
    return low - 1


lines = split_lines("inputs/day14.txt")
reactions = dict(map(parse_line, lines))
assert len(reactions) == len(reactions)
amounts = defaultdict(lambda: 0)
amounts["FUEL"] = 1
part1 = calculate_ore(reaction_start(), reactions)
print(part1)

target = 1000000000000
low = target // part1
part2 = binary_search(reactions, low, target)
print(part2)
