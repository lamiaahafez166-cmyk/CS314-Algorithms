"""Sorting algorithms used in the empirical analysis project.

Contains:
    - insertion_sort / insertion_sort_counted   (the algorithm studied in Lecture 1)
    - merge_sort / merge_sort_counted           (divide-and-conquer baseline)

Two versions of each algorithm are provided on purpose:
    * the *plain* version is used for TIMING (no counters, so no extra overhead);
    * the *counted* version is used for COUNTING comparisons and shifts.
"""

from typing import List, Tuple


# --------------------------------------------------------------------------
# Insertion Sort
# --------------------------------------------------------------------------
def insertion_sort(arr: List[int]) -> List[int]:
    """Sort `arr` in place (ascending) with insertion sort and return it.

    Follows the pseudocode from the lecture (0-indexed):
        for i = 1 to n-1:
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j+1] = arr[j]      # shift right
                j = j - 1
            arr[j+1] = key
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def insertion_sort_counted(arr: List[int]) -> Tuple[List[int], int, int]:
    """Same as `insertion_sort` but also returns (sorted_arr, comparisons, shifts).

    comparisons = number of times `arr[j] > key` is evaluated (key comparisons).
    shifts      = number of times an element is moved one position to the right.
    """
    comparisons = 0
    shifts = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                shifts += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
    return arr, comparisons, shifts


# --------------------------------------------------------------------------
# Merge Sort
# --------------------------------------------------------------------------
def _merge(left: List[int], right: List[int]) -> List[int]:
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def merge_sort(arr: List[int]) -> List[int]:
    """Return a new sorted list (ascending) using merge sort."""
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    return _merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))


def merge_sort_counted(arr: List[int]) -> Tuple[List[int], int]:
    """Merge sort that also returns the number of key comparisons."""
    comparisons = 0

    def merge_count(left, right):
        nonlocal comparisons
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    def sort(a):
        if len(a) <= 1:
            return a[:]
        mid = len(a) // 2
        return merge_count(sort(a[:mid]), sort(a[mid:]))

    return sort(arr), comparisons
