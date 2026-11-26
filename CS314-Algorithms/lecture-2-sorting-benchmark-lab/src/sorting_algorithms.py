"""Sorting algorithms for the Sorting Benchmark Lab (CS314, Lecture 2).

Algorithms
----------
* insertion_sort            - incremental, O(n^2) worst case
* merge_sort                - divide and conquer, Theta(n log n), stable
* quick_sort                - divide and conquer, LAST-element pivot (as in the lecture)
* quick_sort_random_pivot   - bonus variant used to study the worst case
* python_sorted             - Python's built-in sorted() (Timsort), the reference

All functions sort the list IN PLACE and return it (except python_sorted,
which returns a new list), so the same call pattern works for every algorithm.

The recursive algorithms follow the lecture's pseudocode (p, q, r indices).
Quicksort uses an explicit stack instead of recursion: with a last-element
pivot, sorted or reversed input would need n nested calls and crash Python's
recursion limit (default 1000) for n > ~1000.
"""

import random
from typing import List

_rng = random.Random(12345)  # fixed seed -> reproducible random pivots


# --------------------------------------------------------------------------
# Insertion sort
# --------------------------------------------------------------------------
def insertion_sort(a: List) -> List:
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


# --------------------------------------------------------------------------
# Merge sort  (MERGE-SORT(A, p, r) / MERGE(A, p, q, r) from the lecture)
# --------------------------------------------------------------------------
def merge(a: List, p: int, q: int, r: int) -> None:
    """Merge the sorted runs a[p..q] and a[q+1..r] (0-indexed, inclusive)."""
    left = a[p:q + 1]
    right = a[q + 1:r + 1]
    n_left, n_right = len(left), len(right)
    i = j = 0
    k = p
    while i < n_left and j < n_right:
        if left[i] <= right[j]:      # "<=" keeps equal keys in order -> stable
            a[k] = left[i]
            i += 1
        else:
            a[k] = right[j]
            j += 1
        k += 1
    while i < n_left:
        a[k] = left[i]
        i += 1
        k += 1
    while j < n_right:
        a[k] = right[j]
        j += 1
        k += 1


def merge_sort(a: List, p: int = 0, r: int = None) -> List:
    if r is None:
        r = len(a) - 1
    if p < r:
        q = (p + r) // 2             # DIVIDE
        merge_sort(a, p, q)          # CONQUER left
        merge_sort(a, q + 1, r)      # CONQUER right
        merge(a, p, q, r)            # COMBINE
    return a


# --------------------------------------------------------------------------
# Quicksort  (PARTITION(A, p, r) with pivot = A[r], Lomuto scheme)
# --------------------------------------------------------------------------
def partition(a: List, p: int, r: int) -> int:
    """Partition a[p..r] around the pivot a[r]; return the pivot's final index."""
    pivot = a[r]
    i = p - 1
    for j in range(p, r):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[r] = a[r], a[i + 1]
    return i + 1


def _quick_sort(a: List, random_pivot: bool) -> List:
    stack = [(0, len(a) - 1)]
    while stack:
        p, r = stack.pop()
        if p < r:
            if random_pivot:
                k = _rng.randint(p, r)
                a[k], a[r] = a[r], a[k]
            q = partition(a, p, r)
            stack.append((p, q - 1))
            stack.append((q + 1, r))
    return a


def quick_sort(a: List) -> List:
    """Quicksort with the LAST element as pivot (Lab requirement)."""
    return _quick_sort(a, random_pivot=False)


def quick_sort_random_pivot(a: List) -> List:
    """Bonus: quicksort with a random pivot (avoids the sorted/reversed worst case)."""
    return _quick_sort(a, random_pivot=True)


# --------------------------------------------------------------------------
# Reference
# --------------------------------------------------------------------------
def python_sorted(a: List) -> List:
    return sorted(a)


ALGORITHMS = {
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "quick_random_pivot": quick_sort_random_pivot,
    "python_sorted": python_sorted,
}
