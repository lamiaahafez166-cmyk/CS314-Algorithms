"""Merge sort, quicksort and Python's sorted(), with optional comparison counters.

These are the algorithms heap sort is compared with (same code idea as Lecture 2):
    * merge_sort  - divide and conquer, Theta(n log n), O(n) extra space
    * quick_sort  - last-element pivot (as in the lecture); iterative with an explicit
                    stack so that it cannot hit Python's recursion limit
    * python_sorted - the built-in sorted() (Timsort), used as a reference

A comparison is counted every time two KEYS of the input are compared
(`left[i] <= right[j]` in merge, `a[j] <= pivot` in partition).
"""

from typing import List, Tuple


# ------------------------------------------------------------------ merge sort
def merge(a: List, p: int, q: int, r: int) -> None:
    left = a[p:q + 1]
    right = a[q + 1:r + 1]
    n_left, n_right = len(left), len(right)
    i = j = 0
    k = p
    while i < n_left and j < n_right:
        if left[i] <= right[j]:
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
        q = (p + r) // 2
        merge_sort(a, p, q)
        merge_sort(a, q + 1, r)
        merge(a, p, q, r)
    return a


def _merge_counted(a: List, p: int, q: int, r: int) -> int:
    left = a[p:q + 1]
    right = a[q + 1:r + 1]
    n_left, n_right = len(left), len(right)
    i = j = 0
    k = p
    comparisons = 0
    while i < n_left and j < n_right:
        comparisons += 1
        if left[i] <= right[j]:
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
    return comparisons


def merge_sort_counted(a: List) -> Tuple[List, int]:
    total = 0

    def sort(p: int, r: int) -> None:
        nonlocal total
        if p < r:
            q = (p + r) // 2
            sort(p, q)
            sort(q + 1, r)
            total += _merge_counted(a, p, q, r)

    sort(0, len(a) - 1)
    return a, total


# ------------------------------------------------------------------ quicksort
def partition(a: List, p: int, r: int) -> int:
    """Lomuto partition around the pivot a[r]; returns the pivot's final index."""
    pivot = a[r]
    i = p - 1
    for j in range(p, r):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[r] = a[r], a[i + 1]
    return i + 1


def quick_sort(a: List) -> List:
    stack = [(0, len(a) - 1)]
    while stack:
        p, r = stack.pop()
        if p < r:
            q = partition(a, p, r)
            stack.append((p, q - 1))
            stack.append((q + 1, r))
    return a


def quick_sort_counted(a: List) -> Tuple[List, int]:
    comparisons = 0
    stack = [(0, len(a) - 1)]
    while stack:
        p, r = stack.pop()
        if p < r:
            comparisons += r - p          # partition compares a[j] with the pivot r - p times
            q = partition(a, p, r)
            stack.append((p, q - 1))
            stack.append((q + 1, r))
    return a, comparisons


# ------------------------------------------------------------------ reference
def python_sorted(a: List) -> List:
    return sorted(a)
