"""Unit tests for the Sorting Benchmark Lab.

Run from the project root:   python -m unittest discover -s tests -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datasets import CASES, make_input
from sorting_algorithms import (ALGORITHMS, merge_sort, partition,
                                quick_sort)

EDGE_CASES = {
    "empty": [],
    "one element": [7],
    "two sorted": [1, 2],
    "two reversed": [2, 1],
    "all equal": [5, 5, 5, 5, 5],
    "duplicates": [3, 1, 3, 2, 1, 2, 3],
    "negatives": [0, -3, 8, -1, -3, 2],
    "sorted": list(range(1, 21)),
    "reversed": list(range(20, 0, -1)),
    "lecture q5": [9, 4, 7, 1, 6, 3],
    "lecture q6": [3, 8, 2, 5, 1, 4, 7, 6],
}


class TestAllAlgorithms(unittest.TestCase):
    def test_edge_cases(self):
        for name, func in ALGORITHMS.items():
            for label, data in EDGE_CASES.items():
                with self.subTest(algorithm=name, case=label):
                    self.assertEqual(func(data[:]), sorted(data))

    def test_random_arrays_match_builtin(self):
        rng = random.Random(0)
        for name, func in ALGORITHMS.items():
            for _ in range(150):
                data = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
                with self.subTest(algorithm=name):
                    self.assertEqual(func(data[:]), sorted(data))

    def test_benchmark_input_shapes(self):
        for name, func in ALGORITHMS.items():
            for case in CASES:
                with self.subTest(algorithm=name, case=case):
                    data = make_input(case, 500)
                    self.assertEqual(func(data[:]), list(range(1, 501)))

    def test_in_place_algorithms_return_same_list(self):
        for name in ("insertion", "merge", "quick", "quick_random_pivot"):
            data = [3, 1, 2]
            self.assertIs(ALGORITHMS[name](data), data)


class TestLectureAnswers(unittest.TestCase):
    def test_q5_merge_sort_result(self):
        self.assertEqual(merge_sort([9, 4, 7, 1, 6, 3]), [1, 3, 4, 6, 7, 9])

    def test_q6_partition(self):
        a = [3, 8, 2, 5, 1, 4, 7, 6]
        q = partition(a, 0, len(a) - 1)
        self.assertEqual(q + 1, 6)             # 1-based q from the answer key
        self.assertEqual(a[q], 6)              # pivot is in its final place
        self.assertTrue(all(x <= 6 for x in a[:q]))
        self.assertTrue(all(x > 6 for x in a[q + 1:]))
        self.assertEqual(a, [3, 2, 5, 1, 4, 6, 7, 8])  # traced by hand from the pseudocode

    def test_lecture_partition_example(self):
        # Slide: first partition of [2 8 7 1 3 5 6 4], pivot 4
        a = [2, 8, 7, 1, 3, 5, 6, 4]
        q = partition(a, 0, len(a) - 1)
        self.assertEqual(a[q], 4)
        self.assertTrue(all(x <= 4 for x in a[:q]))
        self.assertTrue(all(x > 4 for x in a[q + 1:]))


class Item:
    """A record whose ordering looks only at `key` (to test stability)."""

    def __init__(self, key, tag):
        self.key, self.tag = key, tag

    def __le__(self, other):
        return self.key <= other.key

    def __gt__(self, other):
        return self.key > other.key

    def __lt__(self, other):
        return self.key < other.key


class TestStability(unittest.TestCase):
    """Knowledge-check Q3: merge sort is stable, quicksort (as given) is not."""

    def test_merge_sort_is_stable(self):
        items = [Item(2, "a"), Item(2, "b"), Item(1, "c"), Item(2, "d"), Item(1, "e")]
        result = merge_sort(items[:])
        self.assertEqual([i.tag for i in result], ["c", "e", "a", "b", "d"])

    def test_quick_sort_is_not_stable(self):
        items = [Item(2, "a"), Item(2, "b"), Item(1, "c")]
        result = quick_sort(items[:])
        self.assertEqual([i.tag for i in result], ["c", "b", "a"])  # a and b swapped


class TestDeepInputs(unittest.TestCase):
    def test_quick_sort_does_not_hit_recursion_limit(self):
        # Sorted input with a last-element pivot is the deepest case (n nested partitions
        # if written recursively). The stack-based version must handle it.
        data = list(range(1, 3001))
        self.assertEqual(quick_sort(data[:]), data)
        self.assertEqual(quick_sort(data[::-1]), data)


if __name__ == "__main__":
    unittest.main()
