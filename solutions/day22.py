import re

from utils.utils import split_lines


class Deck:
    def __init__(self, size) -> None:
        self.cards = list(range(size))
        self.left = 0
        self.right = size - 1

    def new_stack(self):
        self.cards.reverse()


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
    seen = [cards[2020]]
    # Repeats a sequence of 10006 cards, all but 9529
    while True:
        for operation in instructions:
            cards = operation(cards)
        if cards[2020] in seen:
            breakpoint()
        seen.append(cards[2020])
        i += 1

    return cards


raw_input = split_lines("inputs/day22.txt")
n_cards = 10007
new_order = slam_shuffle(list(range(n_cards)), raw_input)
part1 = new_order.index(2019)
print(part1)


# Both are prime, which cannot be coincidence
n_cards = 119315717514047
n_iterations = 101741582076661


# cut k: (b, m) => (b+k, m)
# incrememnt k: (b, m) => (b, m + 2k)?
# Each ordering is a linear congruence mod n_cards
# (default: 0 + 1x)
# Translate each operation to effect on congruences
# Reduce shuffle sequence to single congruence (b, m)
# Then the answer is (geometric series of b to r, m^r) (r := number of iterations)
# Compute these huge numbers using modular exponentiation or extended Euclidean algorithm?
