"""Step-by-step demo of heap operations (for the 5-minute walkthrough).

    python src/demo.py

Arrays are printed as Python lists (0-based indices internally); the values match
the knowledge-check answer key of Lecture 3 (questions 5, 6 and 7).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heap import build_max_heap, heap_sort_steps, max_heap_insert


def banner(title):
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():
    banner("Q5  BUILD-MAX-HEAP on [3, 9, 2, 1, 4, 5]")
    a = [3, 9, 2, 1, 4, 5]
    print("Start:", a)
    print("Final:", build_max_heap(a))

    print()
    banner("Q6  HEAPSORT on the max-heap [16, 14, 10, 8, 7, 9, 3, 2, 4, 1]")
    for label, arr, size in heap_sort_steps([16, 14, 10, 8, 7, 9, 3, 2, 4, 1]):
        heap_part, sorted_part = arr[:size], arr[size:]
        print(f"{label:<22} heap({size:>2}) = {heap_part}   sorted tail = {sorted_part}")

    print()
    banner("Q7  INSERT 15 into the max-heap [16, 14, 10, 8, 7, 9, 3]")
    h = [16, 14, 10, 8, 7, 9, 3]
    max_heap_insert(h, 15)
    print("Final:", h)


if __name__ == "__main__":
    main()
