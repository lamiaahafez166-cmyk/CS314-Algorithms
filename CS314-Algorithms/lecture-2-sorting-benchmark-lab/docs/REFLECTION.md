# Reflection

> Draft based on my actual results. Edit it so it is in your own words.

## What surprised me?

1. **How big the pivot effect is.** Quicksort has the same average complexity as merge sort, yet with a last-element
   pivot it took about 2.3 seconds on a *sorted* array of 10,000 elements, against 8 milliseconds on a random one. A
   one-line change (a random pivot) brought it back to about 9 ms.
2. **Insertion sort can beat the "better" algorithms.** On already sorted input at n = 100,000 it finished in about
   5 ms, while merge sort needed about 94 ms. Asymptotic complexity depends on the input, not only on the algorithm.
3. **Python's `sorted()` is much faster than my merge sort** (about 8x on random data) even though both are
   O(n log n). Constant factors, implementation language and exploiting existing order matter a lot.
4. **A recursive quicksort would crash.** With a last-element pivot, sorted input needs n nested calls, which exceeds
   Python's recursion limit, so I had to use an explicit stack.
5. **The answer key and the pseudocode disagree slightly.** Tracing PARTITION on `[3, 8, 2, 5, 1, 4, 7, 6]` by hand
   gives `[3, 2, 5, 1, 4, 6, 7, 8]` (q = 6), while the key lists the last two elements as `8, 7`. The pivot position q
   is the same, and both arrays satisfy the partition property.

## What would I do next?

* Build the **Hybrid Sort: Find the Cutoff** project: switch to insertion sort below a size k and measure the best k.
* Add a **median-of-three** pivot and compare it with the random pivot.
* Repeat the experiment in C++ or Java to see how much of the gap to `sorted()` comes from Python itself, and extend
  n to 10⁶.
* Count comparisons as well as time, to get machine-independent evidence like in the Lecture 1 project.
