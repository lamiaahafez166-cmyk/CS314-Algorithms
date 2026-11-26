import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sorting import (insertion_sort, insertion_sort_counted,
                     merge_sort, merge_sort_counted)


class TestSorting(unittest.TestCase):
    def test_edge_cases(self):
        for data in ([], [1], [2, 1], [1, 1, 1], [3, 3, 1, 2, 2]):
            self.assertEqual(insertion_sort(data[:]), sorted(data))
            self.assertEqual(merge_sort(data[:]), sorted(data))

    def test_random_arrays(self):
        rng = random.Random(0)
        for _ in range(200):
            data = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
            self.assertEqual(insertion_sort(data[:]), sorted(data))
            self.assertEqual(insertion_sort_counted(data[:])[0], sorted(data))
            self.assertEqual(merge_sort(data[:]), sorted(data))
            self.assertEqual(merge_sort_counted(data[:])[0], sorted(data))

    def test_lecture_worked_example(self):
        # Slide 30: sorting [7, 3, 9, 2, 5] -> 8 compares, 6 shifts
        arr, comps, shifts = insertion_sort_counted([7, 3, 9, 2, 5])
        self.assertEqual(arr, [2, 3, 5, 7, 9])
        self.assertEqual((comps, shifts), (8, 6))

    def test_lecture_numerical_problem(self):
        # Answer key: [4,3,2,1] -> 6 comparisons, 6 shifts
        self.assertEqual(insertion_sort_counted([4, 3, 2, 1])[1:], (6, 6))
        # [1,2,3,4] -> 3 comparisons, 0 shifts
        self.assertEqual(insertion_sort_counted([1, 2, 3, 4])[1:], (3, 0))

    def test_worst_and_best_formulas(self):
        for n in (5, 10, 100):
            _, c, s = insertion_sort_counted(list(range(n, 0, -1)))
            self.assertEqual(c, n * (n - 1) // 2)
            self.assertEqual(s, n * (n - 1) // 2)
            _, c, s = insertion_sort_counted(list(range(n)))
            self.assertEqual((c, s), (n - 1, 0))


if __name__ == "__main__":
    unittest.main()
