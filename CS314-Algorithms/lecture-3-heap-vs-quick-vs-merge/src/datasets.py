"""Input generators."""

import random
from typing import List

CASES = ("sorted", "reversed", "random")


def make_input(case: str, n: int, seed: int = 42) -> List[int]:
    """Distinct integers 1..n arranged as `case` (random = a seeded shuffle)."""
    if case == "sorted":
        return list(range(1, n + 1))
    if case == "reversed":
        return list(range(n, 0, -1))
    if case == "random":
        data = list(range(1, n + 1))
        random.Random(seed + n).shuffle(data)
        return data
    raise ValueError(f"unknown case: {case!r}")
