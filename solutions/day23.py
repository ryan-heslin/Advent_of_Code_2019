# Subclass Program to have private input queue but output queue shared with other programs
# Private output queue to collect three items, then write to common output to avoid race condition
# Override program.write to do this
# Write wrapper to read three instructions at once
import pandas as pd

data = {
    "Numbers": [10, 20, 30, 40, 60, 0.55, 1, 0.2, 0.9, 0.8],
    "Letters": ["A", "B", "A", "B", "A", "A", "A", "B", "B", "B"],
}

df = pd.DataFrame(data)

from collections import defaultdict


def apply_discount(data, values, letters):
    df = data.copy()
    discounts = defaultdict(lambda: 1)
    discounts["A"] = 0.95
    df[values] *= df[letters].map(discounts)
    return df


apply_discount(data, "Numbers", "Letters")
