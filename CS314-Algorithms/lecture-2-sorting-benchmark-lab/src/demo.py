"""Step-by-step demo of merge sort and PARTITION (for the 5-minute walkthrough).

    python src/demo.py

Indices are printed 1-based (p, q, r) to match the lecture's pseudocode and
the answer key of the knowledge-check questions 5 and 6.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sorting_algorithms import merge, partition


def traced_merge_sort(a, p, r, depth=0):
    pad = "    " * depth
    if p < r:
        q = (p + r) // 2
        print(f"{pad}DIVIDE  p={p + 1} q={q + 1} r={r + 1}   {a[p:r + 1]}  ->  {a[p:q + 1]} | {a[q + 1:r + 1]}")
        traced_merge_sort(a, p, q, depth + 1)
        traced_merge_sort(a, q + 1, r, depth + 1)
        merge(a, p, q, r)
        print(f"{pad}MERGE   p={p + 1} q={q + 1} r={r + 1}   ->  {a[p:r + 1]}")


def main():
    print("=" * 66)
    print("MERGE-SORT trace on [9, 4, 7, 1, 6, 3]")
    print("=" * 66)
    a = [9, 4, 7, 1, 6, 3]
    traced_merge_sort(a, 0, len(a) - 1)
    print("Final:", a)

    print()
    print("=" * 66)
    print("PARTITION on [3, 8, 2, 5, 1, 4, 7, 6]  (pivot = last element = 6)")
    print("=" * 66)
    b = [3, 8, 2, 5, 1, 4, 7, 6]
    q = partition(b, 0, len(b) - 1)
    print("Array after PARTITION:", b)
    print("q (1-based pivot position):", q + 1)
    print("Left of pivot (<= 6):", b[:q], "   Right of pivot (> 6):", b[q + 1:])


if __name__ == "__main__":
    main()
