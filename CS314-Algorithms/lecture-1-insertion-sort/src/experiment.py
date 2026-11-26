"""Empirical analysis of Insertion Sort (compared with Merge Sort).

Run from the project root:
    python src/experiment.py            # full experiment (n up to 5000)
    python src/experiment.py --quick    # fast sanity run (n up to 1000)

Outputs (in ./results):
    results.csv, time_vs_n.png, time_vs_n_loglog.png,
    operations_vs_n.png, insertion_vs_merge.png
"""

import argparse
import csv
import os
import random
import time

import matplotlib

matplotlib.use("Agg")  # no GUI needed
import matplotlib.pyplot as plt

from sorting import (insertion_sort, insertion_sort_counted,
                     merge_sort, merge_sort_counted)

SEED = 42
FULL_SIZES = [100, 500, 1000, 2000, 3000, 4000, 5000]
QUICK_SIZES = [100, 250, 500, 1000]
CASES = ["sorted", "reverse", "random"]
REPEATS = 5  # each time measurement = average of REPEATS runs (reduces noise)

COLORS = {"sorted": "#2e8b57", "reverse": "#d62728", "random": "#1f77b4"}


def make_input(case, n, rng):
    if case == "sorted":
        return list(range(1, n + 1))
    if case == "reverse":
        return list(range(n, 0, -1))
    data = list(range(1, n + 1))
    rng.shuffle(data)
    return data


def time_sort(func, data):
    """Average wall time (seconds) of func over REPEATS fresh copies."""
    total = 0.0
    for _ in range(REPEATS):
        copy = data[:]
        start = time.perf_counter()
        func(copy)
        total += time.perf_counter() - start
    return total / REPEATS


def run(sizes):
    rng = random.Random(SEED)
    rows = []
    for n in sizes:
        for case in CASES:
            data = make_input(case, n, rng)

            # correctness check against Python's built-in sort
            expected = sorted(data)
            assert insertion_sort(data[:]) == expected
            assert merge_sort(data[:]) == expected

            _, comps, shifts = insertion_sort_counted(data[:])
            _, merge_comps = merge_sort_counted(data[:])
            t_ins = time_sort(insertion_sort, data)
            t_mrg = time_sort(merge_sort, data)

            rows.append({
                "n": n, "case": case,
                "insertion_time_s": t_ins, "merge_time_s": t_mrg,
                "insertion_comparisons": comps, "insertion_shifts": shifts,
                "merge_comparisons": merge_comps,
            })
            print(f"n={n:>5} {case:<8} insertion={t_ins*1000:9.3f} ms  "
                  f"merge={t_mrg*1000:8.3f} ms  comps={comps:>9} shifts={shifts:>9}")
    return rows


def save_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            r = dict(r)
            r["insertion_time_s"] = f"{r['insertion_time_s']:.6f}"
            r["merge_time_s"] = f"{r['merge_time_s']:.6f}"
            w.writerow(r)


def series(rows, case, key):
    pts = sorted((r["n"], r[key]) for r in rows if r["case"] == case)
    return [p[0] for p in pts], [p[1] for p in pts]


def _finish(fig, ax, title, xlabel, ylabel, out, legend_title=None):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3, which="both")
    ax.legend(title=legend_title)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_time(rows, out):
    fig, ax = plt.subplots(figsize=(8, 5))
    for case in CASES:
        x, y = series(rows, case, "insertion_time_s")
        ax.plot(x, [v * 1000 for v in y], marker="o", color=COLORS[case], label=case)
    _finish(fig, ax, "Insertion Sort: running time vs input size",
            "n (number of elements)", "time (ms)", out, legend_title="input type")


def plot_loglog(rows, out):
    fig, ax = plt.subplots(figsize=(8, 5))
    for case in CASES:
        x, y = series(rows, case, "insertion_time_s")
        ax.loglog(x, [v * 1000 for v in y], marker="o", color=COLORS[case], label=case)
    xs = sorted({r["n"] for r in rows})
    x0 = xs[0]
    t_lin = next(r for r in rows if r["case"] == "sorted" and r["n"] == x0)["insertion_time_s"] * 1000
    t_quad = next(r for r in rows if r["case"] == "reverse" and r["n"] == x0)["insertion_time_s"] * 1000
    ax.loglog(xs, [t_lin * (n / x0) for n in xs], "--", color="gray", label="reference slope 1 (~ n)")
    ax.loglog(xs, [t_quad * (n / x0) ** 2 for n in xs], ":", color="black", label="reference slope 2 (~ n²)")
    _finish(fig, ax, "Log-log view: the slope reveals the growth order",
            "n (log scale)", "time in ms (log scale)", out)


def plot_operations(rows, out):
    fig, ax = plt.subplots(figsize=(8, 5))
    xs = sorted({r["n"] for r in rows})
    for case in CASES:
        x, y = series(rows, case, "insertion_comparisons")
        ax.plot(x, y, marker="o", color=COLORS[case], label=f"{case} (measured)")
    ax.plot(xs, [n * (n - 1) / 2 for n in xs], "k--", linewidth=1, label="n(n-1)/2 (theory: worst)")
    ax.plot(xs, [n - 1 for n in xs], "--", color="gray", linewidth=1, label="n-1 (theory: best)")
    _finish(fig, ax, "Insertion Sort: key comparisons vs n",
            "n (number of elements)", "comparisons", out)


def plot_vs_merge(rows, out):
    fig, ax = plt.subplots(figsize=(8, 5))
    x, y = series(rows, "random", "insertion_time_s")
    ax.plot(x, [v * 1000 for v in y], marker="o", color="#d62728", label="Insertion Sort  O(n²)")
    x, y = series(rows, "random", "merge_time_s")
    ax.plot(x, [v * 1000 for v in y], marker="s", color="#1f77b4", label="Merge Sort  O(n log n)")
    _finish(fig, ax, "Random input: Insertion Sort vs Merge Sort",
            "n (number of elements)", "time (ms)", out)


def main():
    parser = argparse.ArgumentParser(description="Empirical analysis of Insertion Sort")
    parser.add_argument("--quick", action="store_true", help="smaller sizes for a fast run")
    args = parser.parse_args()

    sizes = QUICK_SIZES if args.quick else FULL_SIZES
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    rows = run(sizes)
    save_csv(rows, os.path.join(out_dir, "results.csv"))
    plot_time(rows, os.path.join(out_dir, "time_vs_n.png"))
    plot_loglog(rows, os.path.join(out_dir, "time_vs_n_loglog.png"))
    plot_operations(rows, os.path.join(out_dir, "operations_vs_n.png"))
    plot_vs_merge(rows, os.path.join(out_dir, "insertion_vs_merge.png"))
    print(f"\nDone. Files saved in: {os.path.abspath(out_dir)}")


if __name__ == "__main__":
    main()
