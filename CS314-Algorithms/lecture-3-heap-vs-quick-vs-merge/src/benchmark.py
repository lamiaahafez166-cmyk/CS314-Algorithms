"""Heap sort vs quicksort vs merge sort: Python benchmark (CS314 Lecture 3 lab).

Usage (from the project root):
    python src/benchmark.py                  # full run, n = 1,000 ... 1,000,000 (about 3 minutes)
    python src/benchmark.py --quick          # fast sanity run (about 15 seconds)
    python src/benchmark.py --out some_dir   # write results somewhere else

Three experiments:
  1. TIME          - running time of heap, merge, quick and sorted() on random data
  2. COMPARISONS   - key comparisons of heap, merge and quick vs n log2 n
  3. BUILD-MAX-HEAP- comparisons of BUILD-MAX-HEAP vs n  (it should be linear)

Outputs (in --out, default ./results): time_results.csv, comparisons.csv,
build_heap.csv, environment.txt, run_log.txt-compatible console output and PNG figures.
"""

import argparse
import csv
import math
import os
import statistics
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import env_info
from datasets import make_input
from heap import build_max_heap_counted, heap_sort, heap_sort_counted
from sorting_algorithms import (merge_sort, merge_sort_counted, python_sorted,
                                quick_sort, quick_sort_counted)

FULL_SIZES = [1_000, 3_000, 10_000, 30_000, 100_000, 300_000, 1_000_000]
QUICK_SIZES = [1_000, 3_000, 10_000, 30_000]
COUNT_LIMIT = 300_000        # counted versions are slower; count comparisons up to this n

MAX_RUNS = 5
TIME_BUDGET = 1.0            # stop repeating once the runs so far took more than 1 s

ALGOS = {"heap": heap_sort, "merge": merge_sort, "quick": quick_sort, "python_sorted": python_sorted}
COUNTED = {"heap": heap_sort_counted, "merge": merge_sort_counted, "quick": quick_sort_counted}
LABEL = {"heap": "Heap sort", "merge": "Merge sort", "quick": "Quicksort (last pivot)",
         "python_sorted": "Python sorted()"}
STYLE = {"heap": ("#d62728", "o"), "merge": ("#1f77b4", "s"),
         "quick": ("#ff7f0e", "^"), "python_sorted": ("#2ca02c", "D")}


# ------------------------------------------------------------------ measuring
def measure(func, data):
    expected = sorted(data)
    times = []
    while len(times) < MAX_RUNS and sum(times) < TIME_BUDGET:
        work = data[:]
        start = time.perf_counter()
        result = func(work)
        times.append(time.perf_counter() - start)
        if len(times) == 1:
            assert result == expected, f"{func.__name__} returned a wrong result"
    return statistics.median(times), len(times)


def run_time(sizes):
    rows = []
    for n in sizes:
        data = make_input("random", n)
        for name, func in ALGOS.items():
            t, runs = measure(func, data)
            rows.append({"algorithm": name, "n": n, "time_s": t, "runs": runs})
            print(f"TIME   n={n:>9,}  {LABEL[name]:<24} {t * 1000:12.3f} ms  ({runs} runs)", flush=True)
    return rows


def run_comparisons(sizes):
    rows = []
    for n in sizes:
        if n > COUNT_LIMIT:
            continue
        data = make_input("random", n)
        nlogn = n * math.log2(n)
        for name, func in COUNTED.items():
            result, comps = func(data[:])
            assert result == sorted(data)
            rows.append({"algorithm": name, "n": n, "comparisons": comps,
                         "n_log2_n": nlogn, "ratio": comps / nlogn})
            print(f"COUNT  n={n:>9,}  {LABEL[name]:<24} {comps:>14,} comparisons  "
                  f"({comps / nlogn:.3f} x n log2 n)", flush=True)
    return rows


def run_build(sizes):
    rows = []
    for n in sizes:
        data = make_input("random", n)
        comps = build_max_heap_counted(data)
        rows.append({"n": n, "comparisons": comps, "per_n": comps / n})
        print(f"BUILD  n={n:>9,}  BUILD-MAX-HEAP {comps:>12,} comparisons  ({comps / n:.3f} x n)", flush=True)
    return rows


# ------------------------------------------------------------------- saving
def save_csv(path, rows, fmt):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(list(rows[0].keys()))
        for r in rows:
            w.writerow([fmt.get(k, str)(v) for k, v in r.items()])


def series(rows, algo, key):
    pts = sorted((r["n"], r[key]) for r in rows if r["algorithm"] == algo)
    return [p[0] for p in pts], [p[1] for p in pts]


# -------------------------------------------------------------------- plots
def _finish(fig, ax, title, xlabel, ylabel, out, **kw):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_time(rows, out):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    for algo in ALGOS:
        x, y = series(rows, algo, "time_s")
        color, marker = STYLE[algo]
        ax.loglog(x, [v * 1000 for v in y], marker=marker, color=color, label=LABEL[algo])
    xs = sorted({r["n"] for r in rows})
    x, y = series(rows, "merge", "time_s")
    n0, t0 = x[0], y[0] * 1000
    ax.loglog(xs, [t0 * (n * math.log2(n)) / (n0 * math.log2(n0)) for n in xs],
              "--", color="gray", label="reference  n log n")
    _finish(fig, ax, "Python: running time vs n (random input)",
            "n (log scale)", "time in ms (log scale)", out)


def plot_normalized(rows, out):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    for algo in ALGOS:
        x, y = series(rows, algo, "time_s")
        color, marker = STYLE[algo]
        ax.semilogx(x, [t / (n * math.log2(n)) * 1e9 for n, t in zip(x, y)],
                    marker=marker, color=color, label=LABEL[algo])
    ax.set_ylim(bottom=0)
    _finish(fig, ax, "Python: time / (n log₂ n)   (flat = Θ(n log n))",
            "n (log scale)", "nanoseconds per (n log₂ n)", out)


def plot_comparisons(rows, out):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
    for algo in COUNTED:
        color, marker = STYLE[algo]
        x, y = series(rows, algo, "comparisons")
        _, nl = series(rows, algo, "n_log2_n")
        ax1.loglog(nl, y, marker=marker, color=color, label=LABEL[algo])
        _, ratio = series(rows, algo, "ratio")
        ax2.semilogx(x, ratio, marker=marker, color=color, label=LABEL[algo])
    lims = ax1.get_xlim()
    ax1.loglog(lims, lims, "--", color="gray", label="y = n log₂ n")
    ax1.set_xlim(lims)
    ax1.set_title("Comparisons vs n log₂ n")
    ax1.set_xlabel("n log₂ n (log scale)")
    ax1.set_ylabel("key comparisons (log scale)")
    ax1.grid(alpha=0.3, which="both")
    ax1.legend(fontsize=9)

    # asymptotic constants (leading terms); measured ratios approach them slowly
    # because each count also has a negative term of order n
    xmax = max(r["n"] for r in rows)
    for level, text in ((2.0, "heap sort: constant 2"),
                        (1.39, "quicksort: constant 2 ln 2 ≈ 1.39"),
                        (1.0, "merge sort: constant 1")):
        ax2.axhline(level, color="lightgray", linestyle=":")
        ax2.text(xmax, level + 0.03, text, fontsize=8, color="gray", ha="right")
    ax2.set_title("Comparisons / (n log₂ n)")
    ax2.set_xlabel("n (log scale)")
    ax2.set_ylabel("comparisons per n log₂ n")
    ax2.set_ylim(0, 2.4)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=9, loc="lower left")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_build(rows, out):
    fig, ax = plt.subplots(figsize=(8, 5))
    x = [r["n"] for r in rows]
    ax.semilogx(x, [r["per_n"] for r in rows], marker="o", color="#d62728",
                label="BUILD-MAX-HEAP measured")
    ax.axhline(2, color="black", linestyle="--", label="upper bound 2n")
    ax.set_ylim(0, 2.5)
    _finish(fig, ax, "BUILD-MAX-HEAP is O(n): comparisons per element stay constant",
            "n (log scale)", "comparisons / n", out)


# --------------------------------------------------------------------- main
def main():
    parser = argparse.ArgumentParser(description="Heap sort vs quicksort vs merge sort (Python)")
    parser.add_argument("--quick", action="store_true", help="small sizes for a fast sanity run")
    parser.add_argument("--out", default=None, help="output directory (default: ./results)")
    args = parser.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = args.out or os.path.join(here, "..", "results")
    os.makedirs(out_dir, exist_ok=True)
    sizes = QUICK_SIZES if args.quick else FULL_SIZES

    env_info.write(out_dir)
    time_rows = run_time(sizes)
    comp_rows = run_comparisons(sizes)
    build_rows = run_build(sizes)

    save_csv(os.path.join(out_dir, "time_results.csv"), time_rows, {"time_s": lambda v: f"{v:.8f}"})
    save_csv(os.path.join(out_dir, "comparisons.csv"), comp_rows,
             {"n_log2_n": lambda v: f"{v:.1f}", "ratio": lambda v: f"{v:.4f}"})
    save_csv(os.path.join(out_dir, "build_heap.csv"), build_rows, {"per_n": lambda v: f"{v:.4f}"})

    plot_time(time_rows, os.path.join(out_dir, "python_time_vs_n.png"))
    plot_normalized(time_rows, os.path.join(out_dir, "python_normalized.png"))
    plot_comparisons(comp_rows, os.path.join(out_dir, "comparisons.png"))
    plot_build(build_rows, os.path.join(out_dir, "build_heap_linear.png"))
    print(f"\nDone. Results saved in {os.path.abspath(out_dir)}")


if __name__ == "__main__":
    main()
