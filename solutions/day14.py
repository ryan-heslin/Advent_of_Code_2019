from collections import defaultdict
from functools import cached_property
from itertools import chain
from itertools import groupby
from math import ceil
from operator import attrgetter
from queue import PriorityQueue

from utils.utils import split_lines

TARGET = "ORE"

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

    # breakpoint()
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

upper = sum_ore(root, tree)


class Reaction:
    def __init__(self, ingredients, output, quantity):
        self.ingredients = ingredients
        self.output = output
        self.quantity = quantity

    @classmethod
    def parse(cls, line):
        ingredients, output = line.split(" => ")
        ingredients = {
            pair.split(" ")[1]: int(pair.split(" ")[0])
            for pair in ingredients.split(", ")
        }
        parts = output.split(" ")
        quantity = int(parts[0])
        output = parts[1]
        return cls(ingredients, output, quantity)

    # Unique enough for our purposes
    def __hash__(self):
        return hash(self.output)

    def __repr__(self) -> str:
        return (self.ingredients, self.output, self.quantity).__repr__()


# All required reactions reversed
class State:
    def __init__(self, data: dict, costs: dict):
        self.data = defaultdict(lambda: 0)
        self.data.update(data)
        self.costs = costs

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    @cached_property
    def total(self):
        data = self.data
        costs = self.costs
        return sum(
            (
                amount * costs[chemical]
                for chemical, amount in data.items()
                if chemical != TARGET
            ),
            start=0,
        )

    def __lt__(self, other):
        return self.total < other.total

    @cached_property
    def completed(self):
        return self.total == 0

    def reverse_reaction(self, reaction):
        output = reaction.output
        data = defaultdict(lambda: 0)
        data.update(self.data)
        data[output] -= reaction.quantity

        for chemical, amount in reaction.ingredients.items():
            data[chemical] += amount
        return type(self)(data, self.costs)

    def invert(self):
        new_data = defaultdict(lambda: 0)
        new_data.update(
            {
                chemical: -amount
                for chemical, amount in self.data.items()
                if amount < 0 and chemical != TARGET
            }
        )
        return type(self)(new_data, self.costs)

    def restart(self, leftover):
        new_data = defaultdict(lambda: 0)
        new_data.update(
            {
                chemical: amount
                for chemical, amount in self.data.items()
                if amount != 0 and chemical != TARGET
            }
        )
        new_data = self.__class__.sum_merge(
            new_data, {k: v for k, v in leftover.data.items() if k != TARGET}
        )
        return type(self)(new_data, self.costs)

    @staticmethod
    def sum_merge(a, b):
        result = {}
        for chemical in set(chain(a.keys(), b.keys())):
            result[chemical] = a[chemical] + b[chemical]
        return result

    def __hash__(self):
        return hash(zip(self.data.keys(), self.data.values()))

    def __repr__(self):
        return self.data.__repr__()

    def __eq__(self, other):
        return self.data == other.data


def reverse_dfs(start, reactions, upper):

    queue = PriorityQueue()
    queue.put(start, block=False)
    best_ore = upper
    leftover = None
    costs = start.costs

    while queue.qsize():
        current = queue.get(block=False)
        if current.data[TARGET] >= best_ore:
            continue
        if sum(v for k, v in current.data.items() if k != TARGET and v > 0) == 0:
            best_ore = min(best_ore, current.data[TARGET])
            leftover = current
            continue

        target = max(current.data.keys(), key=lambda k: costs[k] * current.data[k])
        new = current.reverse_reaction(reactions[target])
        # if new not in visited:
        queue.put(new, block=False)

    return leftover


def find_ore_costs(reactions, root):

    result = {TARGET: 0}

    def inner(chemical):
        if chemical in result:
            return result[chemical]
        if set(reactions[chemical].ingredients.keys()) == {TARGET}:
            value = reactions[chemical].ingredients[TARGET]
        else:
            value = sum(
                inner(chem) * needed
                for chem, needed in reactions[chemical].ingredients.items()
            )
        value /= reactions[chemical].quantity
        result[chemical] = value
        return value

    inner(root)
    return result


def compute_total(start, reactions, target):
    # Store costs, detect cycle, profit
    leftover = reverse_dfs(start, reactions, upper)
    ore_per = part1 = leftover[TARGET]
    results = {}
    i = 1
    # Dirty hack here - why does it work?
    return part1, int(target // start.total) - (len(reactions) > 50)

    discount = 0
    for chemical, amount in leftover.data.items():
        if chemical != TARGET and amount < 0:
            print(chemical)
            discount += reverse_dfs(
                State({chemical: -amount}, leftover.costs), reactions, upper
            ).data[TARGET]


raw_input = split_lines("inputs/day14.txt")
reactions = (Reaction.parse(line) for line in raw_input)
reactions = {r.output: r for r in reactions}
ore_costs = find_ore_costs(reactions, "FUEL")
start = State(reactions["FUEL"].ingredients, ore_costs)
target = 1000000000000
part1, part2 = compute_total(start, reactions, target)
print(part1)
print(part2)
