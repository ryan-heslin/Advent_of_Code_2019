import re
from functools import reduce
from math import floor
from math import log2

from utils.utils import split_lines


def slam_shuffle(cards, instructions):
    length = len(cards)

    def create(f, n):
        def result(c):
            return f(c, n)

        return result

    def parse(instructions):
        pattern = re.compile(r"\s(?=-?\d+)")
        replacements = {"cut": cut, "deal with increment": increment}
        result = [None] * len(instructions)
        # breakpoint()

        for i, line in enumerate(instructions):
            parts = re.split(pattern, line)
            if len(parts) == 1:
                result[i] = new_stack
            else:
                number = int(parts[1])
                function = replacements[parts[0]]
                result[i] = create(function, number)

        return result

    def new_stack(cards):
        cards.reverse()
        return cards

    def cut(cards, number):
        if number < 0:
            number += length
        return cards[number:] + cards[:number]

    def increment(cards, number):
        new = [None] * length
        target_index = source_index = 0

        while source_index < length:
            assert new[target_index] is None
            new[target_index] = cards[source_index]
            target_index += number
            target_index %= length
            source_index += 1

        return new

    instructions = parse(instructions)

    i = 0
    # Repeats a sequence of 10006 cards, all but 9529
    # print(cards)
    for operation in instructions:
        cards = operation(cards)
        i += 1

    return cards


def parse_congruences(raw):
    n = len(raw)
    result = [None] * n

    for i, el in enumerate(raw_input):
        if el == "deal into new stack":
            result[i] = (-1, -1)
        else:
            parts = el.split(" ")
            k = int(parts[-1])
            if parts[0] == "cut":
                result[i] = (1, -k)
            else:
                result[i] = (k, 0)

    return result


def multiply_congruences(x, y, modulus):
    a = (x[0] * y[0]) % modulus
    b = (x[1] * y[0] + y[1]) % modulus
    return (a, b)


def pow_compose(f, k, modulus):
    result = (1, 0)
    while k > 0:
        if k % 2 != 0:
            result = multiply_congruences(result, f, modulus)
        k //= 2
        f = multiply_congruences(f, f, modulus)
    return result


raw_input = split_lines("inputs/day22.txt")
part1_cards = 10007

new_order = slam_shuffle(list(range(part1_cards)), raw_input)
part1 = new_order.index(2019)
print(part1)

part2_cards = 119315717514047
n_iterations = 101741582076661


# Both
b = 0
m = 1
a, b = reduce(
    lambda a, b: multiply_congruences(a, b, part2_cards), parse_congruences(raw_input)
)

a_final, b_final = pow_compose((a, b), n_iterations, part2_cards)
target = 2020
part2 = ((target - b_final) * pow(a_final, part2_cards - 2, part2_cards)) % part2_cards
assert ((a_final * part2 + b_final) % part2_cards) == target
print(part2)
