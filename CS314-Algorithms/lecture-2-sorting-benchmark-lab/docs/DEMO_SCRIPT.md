# Demo script (5 minutes)

Record your screen (or present live) following this order. Times are approximate.

| Time | What to show | What to say |
|---|---|---|
| 0:00–0:30 | The repository on GitHub: `README.md`, folders `src/`, `tests/`, `results/` | "This is the Sorting Benchmark Lab. I compare insertion sort, merge sort, quicksort and Python's `sorted()` on sorted, reversed and random data." |
| 0:30–1:30 | Terminal: `python src/demo.py` | "Here is merge sort tracing `[9, 4, 7, 1, 6, 3]` with `p, q, r`: it divides into halves down to single elements, then merges the sorted runs back. Then PARTITION on `[3, 8, 2, 5, 1, 4, 7, 6]` with pivot 6: the result is `[3, 2, 5, 1, 4, 6, 7, 8]` and `q = 6`." |
| 1:30–2:15 | Terminal: `python -m unittest discover -s tests -v` | "10 tests pass: edge cases (empty, one element, duplicates, sorted, reversed), random arrays against `sorted()`, the lecture examples, and stability: merge sort is stable, quicksort is not." |
| 2:15–3:00 | Terminal: `python src/benchmark.py --quick` (or open `results/run_log.txt`) | "The benchmark times each algorithm on fresh copies, takes the median of up to 5 runs, and checks every result. Quadratic cases are capped at n = 10,000 because they would take hours at 100,000." |
| 3:00–4:15 | `results/benchmark_random.png`, then `normalized_growth.png`, then `quicksort_pivot_choice.png` | "On a log-log plot the slope is the exponent: insertion sort has slope 2, merge sort and quicksort about 1.1 (n log n). The normalized plot is flat, which confirms the growth law. Quicksort with the last pivot is about 300x slower on sorted input; a random pivot fixes it." |
| 4:15–5:00 | `REPORT.md` conclusion and `docs/REFLECTION.md` | "Theory matches practice. Built-in `sorted()` is about 8x faster than my merge sort. If I continued, I would build a hybrid sort that switches to insertion sort below a cutoff size." |

**Tips:** run `python src/benchmark.py --quick` once before recording so you know it works on your machine;
keep the terminal font large; do not read the report, explain the plots.
