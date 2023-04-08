from functools import reduce
from itertools import groupby
from math import ceil
from operator import add
from operator import attrgetter

from utils.utils import split_lines

# DO regular DFS, after replacing primitives with ore costs
# Discard states if equal or better quantity of all materials reached w/ less ore
# Maybe rank nodes by distance from end
# Topo sort into groups of reactions
# Do minimum amount of reactions in group i to unlock group i + 1

# Compare the same, regardless of quantity
class Output:
    def __init__(self, element, quantity):
        self.element = element
        self.quantity = quantity

    def __repr__(self):
        return f"({self.element}, {self.quantity})"

    def __eq__(self, other):
        return self.element == other.element

    def __mul__(self, number):
        return self.__class__(self.element, self.quantity * number)

    def __hash__(self):
        return hash(self.element)

    def __lt__(self, other):
        return other.element < self.element

    def __add__(self, other):
        return self.quantity + (
            other.quantity if isinstance(other, __class__) else other
        )

    def __radd__(self, other):
        return self.__add__(other)


def parse_quantity(quantity):
    number, product = quantity.split(" ")
    return product, int(number)


def parse(lines):
    result = {}
    # product : {ingred, amount, ..., amount}
    for line in lines:
        ingredients, product = line.split(" => ")
        key = Output(*parse_quantity(product))
        result[key] = tuple(
            [Output(*parse_quantity(prod)) for prod in ingredients.split(", ")]
        )
    return result


def sum_ore(root, tree):
    primitive = "ORE"

    needed = list(tree[root])
    # Output by reaction
    costs = {k.element: k.quantity for k in tree.keys()}
    finished = []

    while needed:
        current = needed.pop()
        parent = tree[current]
        if len(parent) == 1 and parent[0].element == primitive:
            finished.append(current)
        else:
            multiplier = ceil(current.quantity / costs[current.element])
            parent = tuple([pair * multiplier for pair in parent])
            needed.extend(parent)

    # All primitives done, so sum up and compute
    finished.sort()
    print(finished)
    ore = 0

    for _, group in groupby(finished, key=attrgetter("element")):
        group = list(group)
        total = sum(group)
        source = tree[group[0]][0]
        # Track leftover here?
        creations = ceil(total / costs[group[0].element])
        ore += creations * source.quantity

    return ore


raw_input = split_lines("inputs/day14.txt")
tree = parse(raw_input)
root = Output("FUEL", 1)

part1 = sum_ore(root, tree)
print(part1)
# Depth-first for leftovers?
# Start at root
# While not at root:
# Compute cost
# Add leftover
# Only sum all quantities once everything converted into primitives created from
# ore to avoid discarding leftovers
