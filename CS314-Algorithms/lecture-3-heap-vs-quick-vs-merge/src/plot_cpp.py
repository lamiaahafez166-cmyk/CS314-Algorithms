"""Plot the C++ benchmark results (results/cpp_results.csv) and the cache effect.

    python src/plot_cpp.py [results_dir]

Reads  cpp_results.csv  and writes  cpp_time_vs_n.png  and  cpp_cache_effect.png.
"""

import csv
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

LABEL = {"heap": "Heap sort", "merge": "Merge sort", "quick": "Quicksort (last pivot)",
         "std_sort": "std::sort (introsort)"}
STYLE = {"heap": ("#d62728", "o"), "merge": ("#1f77b4", "s"),
         "quick": ("#ff7f0e", "^"), "std_sort": ("#2ca02c", "D")}
INT_BYTES = 4


def load(path):
    rows = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.setdefault(r["algorithm"], []).append((int(r["n"]), float(r["time_ns"])))
    for k in rows:
        rows[k].sort()
    return rows


def l2_bytes(results_dir):
    """Read the L2 cache size (MiB or KiB) from environment.txt if it is there."""
    try:
        for line in open(os.path.join(results_dir, "environment.txt")):
            if line.startswith("L2 cache"):
                value = line.split(":")[1].split("(")[0].strip()
                num, unit = value.split()[:2]
                return float(num) * {"KiB": 1024, "MiB": 1024 ** 2, "GiB": 1024 ** 3}[unit]
    except Exception:
        pass
    return None


def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "results")
    data = load(os.path.join(results_dir, "cpp_results.csv"))
    l2 = l2_bytes(results_dir)

    # 1. time vs n (log-log)
    fig, ax = plt.subplots(figsize=(8, 5.2))
    for algo, pts in data.items():
        color, marker = STYLE[algo]
        ax.loglog([p[0] for p in pts], [p[1] / 1e6 for p in pts], marker=marker,
                  color=color, label=LABEL[algo])
    ax.set_title("C++ (-O2): running time vs n (random input)")
    ax.set_xlabel("n (log scale)")
    ax.set_ylabel("time in ms (log scale)")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(results_dir, "cpp_time_vs_n.png"), dpi=150)
    plt.close(fig)

    # 2. time / (n log2 n): the cache effect
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    for algo, pts in data.items():
        color, marker = STYLE[algo]
        ax.semilogx([p[0] for p in pts], [p[1] / (p[0] * math.log2(p[0])) for p in pts],
                    marker=marker, color=color, label=LABEL[algo])
    if l2:
        n_l2 = l2 / INT_BYTES
        ax.axvline(n_l2, color="gray", linestyle="--", linewidth=1)
        ax.text(n_l2 * 1.05, ax.get_ylim()[1] * 0.95,
                f"array = L2 cache\n({l2 / 1024 ** 2:.0f} MiB = {n_l2:,.0f} ints)",
                fontsize=8, va="top", color="gray")
    ax.set_ylim(bottom=0)
    ax.set_title("C++: nanoseconds per (n log₂ n)   (flat = ideal Θ(n log n))")
    ax.set_xlabel("n (log scale)")
    ax.set_ylabel("ns per (n log₂ n)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(results_dir, "cpp_cache_effect.png"), dpi=150)
    plt.close(fig)
    print("Saved cpp_time_vs_n.png and cpp_cache_effect.png in", os.path.abspath(results_dir))


if __name__ == "__main__":
    main()
