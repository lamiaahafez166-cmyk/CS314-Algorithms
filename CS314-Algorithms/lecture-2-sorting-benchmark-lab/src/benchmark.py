"""Sorting Benchmark Lab: insertion, merge, quick and Python sorted().

Usage (from the project root):
    python src/benchmark.py                 # full run, n = 1,000 ... 100,000
    python src/benchmark.py --quick         # fast sanity run (about 10 seconds)
    python src/benchmark.py --quad-cap 5000 # lower the cap for the O(n^2) cases

Why a cap?  Insertion sort (reversed / random input) and quicksort with a
last-element pivot (sorted / reversed input) do about n^2/2 steps.  In pure
Python, n = 100,000 would take hours, so those combinations run only up to
`--quad-cap` (default 10,000).  Every other combination runs to the full n.

Outputs (in ./results):
    benchmark_results.csv, growth_rates.csv, run_log.txt and the PNG figures.
"""

import argparse
import csv
import math
import os
import statistics
import sys
import time

import matplotlib

matplotlib.use("Agg")  # no GUI needed
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datasets import CASES, make_input
from sorting_algorithms import ALGORITHMS

FULL_SIZES = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000]
QUICK_SIZES = [500, 1_000, 2_000, 5_000]
DEFAULT_QUAD_CAP = 10_000

MAX_RUNS = 5          # at most 5 timed runs per measurement (median is reported)
TIME_BUDGET = 1.0     # stop repeating once the runs so far took more than 1 s

# (algorithm, case) pairs that cost ~n^2/2 steps
QUADRATIC = {
    ("insertion", "reversed"), ("insertion", "random"),
    ("quick", "sorted"), ("quick", "reversed"),
}

LABELS = {
    "insertion": "Insertion sort",
    "merge": "Merge sort",
    "quick": "Quicksort (last pivot)",
    "quick_random_pivot": "Quicksort (random pivot)",
    "python_sorted": "Python sorted()",
}
STYLE = {
    "insertion": ("#d62728", "o"),
    "merge": ("#1f77b4", "s"),
    "quick": ("#ff7f0e", "^"),
    "quick_random_pivot": ("#9467bd", "v"),
    "python_sorted": ("#2ca02c", "D"),
}
MAIN_ALGOS = ["insertion", "merge", "quick", "python_sorted"]  # the four required by the lab


# ---------------------------------------------------------------- measuring
def measure(func, data):
    """Median wall time (s) of func on fresh copies of data, plus the run count."""
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


def run(sizes, quad_cap):
    rows = []
    for n in sizes:
        for case in CASES:
            data = make_input(case, n)
            for name, func in ALGORITHMS.items():
                if (name, case) in QUADRATIC and n > quad_cap:
                    continue
                t, runs = measure(func, data)
                rows.append({"algorithm": name, "case": case, "n": n,
                             "time_s": t, "runs": runs})
                print(f"n={n:>7,}  {case:<8}  {LABELS[name]:<26} {t * 1000:12.3f} ms  ({runs} runs)",
                      flush=True)
    return rows


# ------------------------------------------------------------------ results
def get(rows, algo, case):
    pts = sorted((r["n"], r["time_s"]) for r in rows if r["algorithm"] == algo and r["case"] == case)
    return [p[0] for p in pts], [p[1] for p in pts]


def save_results(rows, out_dir):
    with open(os.path.join(out_dir, "benchmark_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["algorithm", "case", "n", "time_s", "runs"])
        for r in rows:
            w.writerow([r["algorithm"], r["case"], r["n"], f"{r['time_s']:.8f}", r["runs"]])


def growth_rates(rows, min_n=2_000):
    """Fit time ~ c * n^k on a log-log scale; return {(algo, case): k}."""
    out = {}
    for algo in ALGORITHMS:
        for case in CASES:
            x, y = get(rows, algo, case)
            pts = [(a, b) for a, b in zip(x, y) if a >= min_n]
            if len(pts) >= 3:
                k = np.polyfit(np.log([p[0] for p in pts]), np.log([p[1] for p in pts]), 1)[0]
                out[(algo, case)] = float(k)
    return out


def save_growth(rates, out_dir):
    with open(os.path.join(out_dir, "growth_rates.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["algorithm", "case", "fitted_exponent_k"])
        for (algo, case), k in rates.items():
            w.writerow([algo, case, f"{k:.2f}"])


# -------------------------------------------------------------------- plots
def plot_case(rows, case, out):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    for algo in MAIN_ALGOS:
        x, y = get(rows, algo, case)
        if x:
            color, marker = STYLE[algo]
            ax.loglog(x, [v * 1000 for v in y], marker=marker, color=color, label=LABELS[algo])
    xs = sorted({r["n"] for r in rows})
    # reference curves (in ms, anchored at merge sort's smallest n)
    x, y = get(rows, "merge", case)
    n0, t0 = x[0], y[0] * 1000
    ax.loglog(xs, [t0 * (n * math.log2(n)) / (n0 * math.log2(n0)) for n in xs],
              "--", color="gray", linewidth=1.2, label="reference  n log n")
    ax.loglog(xs, [t0 * (n / n0) ** 2 for n in xs],
              ":", color="black", linewidth=1.2, label="reference  n²")
    ax.set_title(f"Running time vs n  -  {case} input")
    ax.set_xlabel("n (number of elements, log scale)")
    ax.set_ylabel("time in ms (log scale)")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_normalized(rows, out):
    """Flat line = the algorithm follows the growth law used for the division."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: time / (n log2 n) for the n log n algorithms (random input)
    for algo in ("merge", "quick", "quick_random_pivot", "python_sorted"):
        x, y = get(rows, algo, "random")
        color, marker = STYLE[algo]
        ax1.semilogx(x, [t / (n * math.log2(n)) * 1e9 for n, t in zip(x, y)],
                     marker=marker, color=color, label=LABELS[algo])
    ax1.set_title("Random input:  time / (n log₂ n)\nflat line = Θ(n log n)")
    ax1.set_xlabel("n (log scale)")
    ax1.set_ylabel("nanoseconds per (n log₂ n)")
    ax1.set_ylim(bottom=0)
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8.5)

    # Right: time / n^2 for the quadratic cases
    for algo, case in (("insertion", "random"), ("insertion", "reversed"),
                       ("quick", "sorted"), ("quick", "reversed")):
        x, y = get(rows, algo, case)
        color, marker = STYLE[algo]
        ls = "-" if case == "reversed" else "--"
        ax2.semilogx(x, [t / (n * n) * 1e9 for n, t in zip(x, y)], marker=marker,
                     color=color, linestyle=ls, label=f"{LABELS[algo]}, {case}")
    ax2.set_title("Quadratic cases:  time / n²\nflat line = Θ(n²)")
    ax2.set_xlabel("n (log scale)")
    ax2.set_ylabel("nanoseconds per n²")
    ax2.set_ylim(bottom=0)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8.5)

    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_pivot(rows, out):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    spec = [("quick", "sorted", "#d62728", "-", "o"),
            ("quick", "reversed", "#ff7f0e", "-", "^"),
            ("quick", "random", "#1f77b4", "--", "s"),
            ("quick_random_pivot", "sorted", "#2ca02c", "-", "D"),
            ("quick_random_pivot", "reversed", "#9467bd", "-", "v")]
    for algo, case, color, ls, marker in spec:
        x, y = get(rows, algo, case)
        # keep the comparison on the sizes where the last-pivot version actually ran on sorted data
        limit = max(get(rows, "quick", "sorted")[0])
        pts = [(a, b) for a, b in zip(x, y) if a <= limit]
        ax.loglog([p[0] for p in pts], [p[1] * 1000 for p in pts], marker=marker,
                  color=color, linestyle=ls, label=f"{LABELS[algo]}, {case}")
    ax.set_title("Pivot choice: last element vs random")
    ax.set_xlabel("n (log scale)")
    ax.set_ylabel("time in ms (log scale)")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------- main
def main():
    parser = argparse.ArgumentParser(description="Sorting Benchmark Lab")
    parser.add_argument("--quick", action="store_true", help="small sizes for a fast sanity run")
    parser.add_argument("--quad-cap", type=int, default=DEFAULT_QUAD_CAP,
                        help="largest n for the O(n^2) combinations (default 10000)")
    args = parser.parse_args()

    sizes = QUICK_SIZES if args.quick else FULL_SIZES
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    rows = run(sizes, args.quad_cap)
    save_results(rows, out_dir)
    rates = growth_rates(rows, min_n=sizes[1] if args.quick else 2_000)
    save_growth(rates, out_dir)

    for case in CASES:
        plot_case(rows, case, os.path.join(out_dir, f"benchmark_{case}.png"))
    plot_normalized(rows, os.path.join(out_dir, "normalized_growth.png"))
    plot_pivot(rows, os.path.join(out_dir, "quicksort_pivot_choice.png"))
    print(f"\nDone. Results saved in {os.path.abspath(out_dir)}")


if __name__ == "__main__":
    main()
