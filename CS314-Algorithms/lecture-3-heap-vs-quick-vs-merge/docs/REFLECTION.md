# Reflection

> Draft based on my actual results. Edit it so it is in your own words.

## What surprised me?

1. **Heap sort does about twice as many comparisons as merge sort** (2.0x at n = 300,000), even though both are
   Θ(n log n). Big-O hides the constant: each level of a sift-down needs two comparisons.
2. **The cache effect is big and clear.** In C++ heap sort's cost per n log₂ n rose from 4.4 to 8.1 ns
   (1.86x) while quicksort's stayed almost flat (1.04x). Two algorithms with the same
   complexity can differ by 2.6x because of how they touch memory.
3. **BUILD-MAX-HEAP really is linear.** I measured about 1.88·n comparisons for every n from 10³ to 10⁶, which matches the
   proof from the lecture that it is O(n) and not O(n log n).
4. **Python hides the hardware.** Python was about 29x slower than C++ for heap sort, and the interpreter's overhead made it much harder to
   see the memory effect. The language I measure in changes what I can learn.
5. **Heap sort is not stable, even for two elements.** Sorting two equal keys swapped them, which I turned into a unit test.

## What would I do next?

* Read **hardware cache-miss counters** (for example `perf stat`) to confirm the cache explanation directly.
* Try **bottom-up heap sort** and a **4-ary heap** (the d-ary Heap Experiment project) to see whether fewer levels
  and better locality close the gap.
* Implement **introsort** (quicksort with a heap sort fallback) and compare it with `std::sort`.
* Repeat the experiment on my own computer and compare the cache size and the position of the jump.
