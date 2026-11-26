# Demo script (5 minutes)

| Time | What to show | What to say |
|---|---|---|
| 0:00–0:30 | The GitHub repository: `README.md`, folders `src/`, `cpp/`, `tests/`, `results/` | "I compare heap sort with merge sort and quicksort. Heap sort is Θ(n log n) and in place, but in practice it is slower. I want to measure the gap and explain it." |
| 0:30–1:30 | Terminal: `python src/demo.py` | "BUILD-MAX-HEAP on [3, 9, 2, 1, 4, 5] gives [9, 4, 5, 1, 3, 2]. HEAPSORT swaps the root with the last element, shrinks the heap and repairs it with MAX-HEAPIFY; the sorted tail grows from the right. Inserting 15 sifts it up to the second position. These match the answer key." |
| 1:30–2:00 | Terminal: `python -m unittest discover -s tests -v` | "17 tests: edge cases, random arrays against `sorted()`, the heap property, the lecture's answers, and stability: heap sort is not stable, merge sort is." |
| 2:00–3:00 | `results/comparisons.png` and `results/build_heap_linear.png` | "Counting comparisons: all three follow n log n, but heap sort needs about 2.0x more than merge sort because each sift-down level makes two comparisons. BUILD-MAX-HEAP uses about 1.88 n comparisons, so it is linear." |
| 3:00–4:15 | `results/cpp_cache_effect.png` | "In C++ the cost per n log n is flat for quicksort and merge sort, but heap sort goes from 4.4 to 8.1 ns once the array no longer fits in the 2 MiB L2 cache. A sift-down jumps from index i to 2i+1, so deep levels touch different cache lines, while quicksort and merge sort read sequentially." |
| 4:15–5:00 | `REPORT.md` conclusion and `docs/REFLECTION.md` | "Use the library sort; use heap sort when memory is tight and a worst-case guarantee matters, or inside introsort; use a heap for priority queues. Next I would read hardware cache-miss counters to confirm the explanation." |

**Tips:** run `python src/benchmark.py --quick --out /tmp/quick` once before recording; keep the terminal font large;
explain the plots instead of reading the report.
