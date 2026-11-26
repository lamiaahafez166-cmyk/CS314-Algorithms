"""Unit tests. Run from the project root:   python -m unittest discover -s tests -v"""

import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datasets import CASES, make_input
from heap import (build_max_heap, build_max_heap_counted, heap_extract_max,
                  heap_sort, heap_sort_counted, heap_sort_steps, left,
                  max_heap_insert, max_heapify, parent, right)
from sorting_algorithms import (merge_sort, merge_sort_counted, python_sorted,
                                quick_sort, quick_sort_counted)

ALGORITHMS = {
    "heap": heap_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "python_sorted": python_sorted,
}

EDGE_CASES = {
    "empty": [],
    "one element": [7],
    "two sorted": [1, 2],
    "two reversed": [2, 1],
    "all equal": [5, 5, 5, 5, 5],
    "duplicates": [3, 1, 3, 2, 1, 2, 3],
    "negatives": [0, -3, 8, -1, -3, 2],
    "sorted": list(range(1, 31)),
    "reversed": list(range(30, 0, -1)),
}


def is_max_heap(a, size=None):
    size = len(a) if size is None else size
    return all(a[parent(i)] >= a[i] for i in range(1, size))


class TestSorting(unittest.TestCase):
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
                    self.assertEqual(func(make_input(case, 400)), list(range(1, 401)))

    def test_counted_versions_sort_correctly(self):
        rng = random.Random(1)
        for counted in (heap_sort_counted, merge_sort_counted, quick_sort_counted):
            for _ in range(100):
                data = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
                result, comps = counted(data[:])
                self.assertEqual(result, sorted(data))
                self.assertGreaterEqual(comps, 0)


class TestHeapBasics(unittest.TestCase):
    def test_index_formulas(self):
        # 0-based version of PARENT / LEFT / RIGHT
        self.assertEqual((left(0), right(0)), (1, 2))
        self.assertEqual((left(3), right(3)), (7, 8))
        self.assertEqual((parent(1), parent(2), parent(8)), (0, 0, 3))

    def test_max_heapify_repairs_root(self):
        a = [1, 14, 10, 8, 7, 9, 3, 2, 4]   # only the root violates the heap property
        max_heapify(a, 0, len(a))
        self.assertTrue(is_max_heap(a))

    def test_build_max_heap_gives_heap_property(self):
        rng = random.Random(2)
        for _ in range(100):
            a = [rng.randint(0, 99) for _ in range(rng.randint(0, 70))]
            self.assertTrue(is_max_heap(build_max_heap(a)))

    def test_build_is_linear(self):
        # BUILD-MAX-HEAP does at most 2n key comparisons (it is O(n), not O(n log n))
        for n in (100, 1000, 10000):
            data = make_input("random", n)
            self.assertLessEqual(build_max_heap_counted(data), 2 * n)


class TestLectureAnswers(unittest.TestCase):
    """Knowledge-check answer key of Lecture 3."""

    def test_q5_build_max_heap(self):
        self.assertEqual(build_max_heap([3, 9, 2, 1, 4, 5]), [9, 4, 5, 1, 3, 2])

    def test_q6_heapsort_iterations(self):
        steps = list(heap_sort_steps([16, 14, 10, 8, 7, 9, 3, 2, 4, 1]))
        label, arr, size = steps[1]
        self.assertEqual((arr, size), ([14, 8, 10, 4, 7, 9, 3, 2, 1, 16], 9))
        label, arr, size = steps[2]
        self.assertEqual((arr, size), ([10, 8, 9, 4, 7, 1, 3, 2, 14, 16], 8))
        self.assertEqual(steps[-1][1], [1, 2, 3, 4, 7, 8, 9, 10, 14, 16])

    def test_q7_insert(self):
        a = [16, 14, 10, 8, 7, 9, 3]
        max_heap_insert(a, 15)
        self.assertEqual(a, [16, 15, 10, 14, 7, 9, 3, 8])

    def test_task_scheduler_order_from_lecture(self):
        # Tasks A(3), B(9), C(5), D(7): EXTRACT-MAX order is B, D, C, A
        heap = []
        for priority, name in [(3, "A"), (9, "B"), (5, "C"), (7, "D")]:
            max_heap_insert(heap, (priority, name))
        order = [heap_extract_max(heap)[1] for _ in range(4)]
        self.assertEqual(order, ["B", "D", "C", "A"])

    def test_extract_max_underflow(self):
        with self.assertRaises(IndexError):
            heap_extract_max([])


class Item:
    """Record compared only by `key`, to test stability."""

    def __init__(self, key, tag):
        self.key, self.tag = key, tag

    def __gt__(self, other):
        return self.key > other.key

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key


class TestStabilityAndComplexity(unittest.TestCase):
    def test_heap_sort_is_not_stable(self):
        # Q3: "No, equal keys can change order"
        items = [Item(1, "a"), Item(1, "b")]
        self.assertEqual([i.tag for i in heap_sort(items[:])], ["b", "a"])

    def test_merge_sort_is_stable(self):
        items = [Item(2, "a"), Item(2, "b"), Item(1, "c"), Item(2, "d")]
        self.assertEqual([i.tag for i in merge_sort(items[:])], ["c", "a", "b", "d"])

    def test_comparison_counts_scale_like_n_log_n(self):
        n = 4096
        data = make_input("random", n)
        nlogn = n * math.log2(n)
        _, heap_c = heap_sort_counted(data[:])
        _, merge_c = merge_sort_counted(data[:])
        _, quick_c = quick_sort_counted(data[:])
        self.assertLess(merge_c, nlogn)           # merge sort: about n log2 n - 1.25 n
        self.assertLess(heap_c, 2.1 * nlogn)      # heap sort: about 2 n log2 n
        self.assertGreater(heap_c, merge_c)       # heap sort compares more than merge sort
        self.assertLess(quick_c, 2.0 * nlogn)

    def test_heap_sort_in_place_returns_same_list(self):
        data = [3, 1, 2]
        self.assertIs(heap_sort(data), data)


if __name__ == "__main__":
    unittest.main()
