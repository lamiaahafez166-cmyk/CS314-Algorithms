"""Heap data structure, heap sort and priority-queue operations (CS314, Lecture 3).

The array is 0-indexed, so the lecture's 1-based formulas shift by one:

    lecture (1-based)        this code (0-based)
    PARENT(i) = i // 2       parent(i) = (i - 1) // 2
    LEFT(i)   = 2i           left(i)   = 2i + 1
    RIGHT(i)  = 2i + 1       right(i)  = 2i + 2

MAX-HEAPIFY is written iteratively, so heap sort needs only O(1) extra space
(knowledge-check question 4).  The *_counted versions also return the number of
key comparisons, which the lab asks us to plot against n log2 n.
"""

from typing import Iterator, List, Tuple


# ---------------------------------------------------------------- indices
def parent(i: int) -> int:
    return (i - 1) // 2


def left(i: int) -> int:
    return 2 * i + 1


def right(i: int) -> int:
    return 2 * i + 2


# ---------------------------------------------------------------- MAX-HEAPIFY
def max_heapify(a: List, i: int, heap_size: int) -> None:
    """Sift a[i] down until the subtree rooted at i is a max-heap.

    Assumes the subtrees rooted at left(i) and right(i) are already max-heaps.
    """
    while True:
        l = 2 * i + 1
        r = l + 1
        largest = i
        if l < heap_size and a[l] > a[largest]:
            largest = l
        if r < heap_size and a[r] > a[largest]:
            largest = r
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


def max_heapify_counted(a: List, i: int, heap_size: int) -> int:
    """Same as max_heapify; returns the number of key comparisons performed."""
    comparisons = 0
    while True:
        l = 2 * i + 1
        r = l + 1
        largest = i
        if l < heap_size:
            comparisons += 1
            if a[l] > a[largest]:
                largest = l
        if r < heap_size:
            comparisons += 1
            if a[r] > a[largest]:
                largest = r
        if largest == i:
            return comparisons
        a[i], a[largest] = a[largest], a[i]
        i = largest


# ---------------------------------------------------------------- BUILD-MAX-HEAP
def build_max_heap(a: List) -> List:
    """Turn the array into a max-heap in O(n): heapify from the last parent up to the root."""
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        max_heapify(a, i, n)
    return a


def build_max_heap_counted(a: List) -> int:
    """Build a max-heap in place; return the number of key comparisons."""
    n = len(a)
    comparisons = 0
    for i in range(n // 2 - 1, -1, -1):
        comparisons += max_heapify_counted(a, i, n)
    return comparisons


# ---------------------------------------------------------------- HEAPSORT
def heap_sort(a: List) -> List:
    """Sort a in place (ascending): build a max-heap, then repeatedly extract the maximum."""
    n = len(a)
    build_max_heap(a)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]      # move the current maximum to its final place
        max_heapify(a, 0, end)           # repair the heap of size `end`
    return a


def heap_sort_counted(a: List) -> Tuple[List, int]:
    """Heap sort that also returns the total number of key comparisons."""
    n = len(a)
    comparisons = build_max_heap_counted(a)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        comparisons += max_heapify_counted(a, 0, end)
    return a, comparisons


def heap_sort_steps(a: List) -> Iterator[Tuple[str, List, int]]:
    """Yield (label, array copy, heap_size) after BUILD and after every HEAPSORT iteration.

    Used by the demo and by the tests of knowledge-check question 6.
    """
    n = len(a)
    build_max_heap(a)
    yield "after BUILD-MAX-HEAP", a[:], n
    for it, end in enumerate(range(n - 1, 0, -1), start=1):
        a[0], a[end] = a[end], a[0]
        max_heapify(a, 0, end)
        yield f"after iteration {it}", a[:], end


# ---------------------------------------------------------------- priority queue
def max_heap_insert(a: List, key) -> None:
    """INSERT: append the key and sift it up while it is larger than its parent. O(log n)."""
    a.append(key)
    i = len(a) - 1
    while i > 0 and a[(i - 1) // 2] < a[i]:
        p = (i - 1) // 2
        a[i], a[p] = a[p], a[i]
        i = p


def heap_extract_max(a: List):
    """EXTRACT-MAX: remove and return the largest key. O(log n)."""
    if not a:
        raise IndexError("heap underflow")
    top = a[0]
    last = a.pop()
    if a:
        a[0] = last
        max_heapify(a, 0, len(a))
    return top
