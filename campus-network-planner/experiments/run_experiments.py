"""Experiments for the report.  Run from the project root:

    python experiments/run_experiments.py

Writes results/experiments.csv, results/*.png and results/summary.md.
Every graph is solved by all MST algorithms and the totals are compared, so
the experiment doubles as a correctness check.
"""

from __future__ import annotations

import csv
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from campusnet import dijkstra, kruskal, prim, prim_dense, random_graph

OUT = os.path.join(ROOT, "results")
SPARSE_V = [200, 400, 800, 1600, 3200, 6400]     # E about 3V
DENSE_V = [40, 80, 160, 320, 640]                # E about V^2 / 4
SEEDS = [1, 2, 3]
REPEATS = 3


def best_time(fn) -> float:
    best = float("inf")
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t0)
    return best


def run() -> list[dict]:
    rows = []
    cases = [("sparse", n, 2 * n) for n in SPARSE_V] + \
            [("dense", n, n * (n - 1) // 4 - (n - 1)) for n in DENSE_V]
    for kind, n, extra in cases:
        for seed in SEEDS:
            g = random_graph(n, extra, max_cost=10_000, seed=seed)
            fns = {
                "Kruskal": lambda: kruskal(g),
                "Prim (heap)": lambda: prim(g, "v0"),
                "Prim (dense)": lambda: prim_dense(g, "v0"),
                "Dijkstra": lambda: dijkstra(g, "v0"),
            }
            # Prim (dense) is O(V^2) in pure Python; skip it where it would take minutes
            if kind == "sparse" and n > 1600:
                del fns["Prim (dense)"]
            totals = {}
            for name, fn in fns.items():
                r = fn()
                if name != "Dijkstra":
                    totals[name] = r.total
                examined = getattr(r, "examined", None)
                rows.append({
                    "kind": kind, "V": g.V, "E": g.E, "seed": seed, "algo": name,
                    "seconds": best_time(fn), "examined": examined,
                })
            if len(set(totals.values())) != 1:
                raise SystemExit(f"MST algorithms disagree on {kind} V={n} seed={seed}: {totals}")
        print(f"done {kind} V={n}", flush=True)
    return rows


def select(rows, kind, algo):
    return [r for r in rows if r["kind"] == kind and r["algo"] == algo]


def fit(x, y):
    slope, icpt = np.polyfit(x, y, 1)
    pred = slope * np.array(x) + icpt
    ss_res = float(np.sum((np.array(y) - pred) ** 2))
    ss_tot = float(np.sum((np.array(y) - np.mean(y)) ** 2))
    return slope, icpt, 1 - ss_res / ss_tot


def plot_sparse(rows) -> dict:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    stats = {}
    for ax, algos, xlabel, xf, title in (
        (axes[0], ["Kruskal", "Prim (heap)"], "E log2 V", lambda r: r["E"] * math.log2(r["V"]),
         "MST on sparse graphs (E ≈ 3V)"),
        (axes[1], ["Dijkstra"], "(V + E) log2 V", lambda r: (r["V"] + r["E"]) * math.log2(r["V"]),
         "Dijkstra on sparse graphs"),
    ):
        for algo, color in zip(algos, ("#2563eb", "#dc2626")):
            sel = select(rows, "sparse", algo)
            x = [xf(r) for r in sel]
            y = [r["seconds"] * 1000 for r in sel]
            slope, icpt, r2 = fit(x, y)
            stats[algo] = (slope * 1e6, r2)
            ax.scatter(x, y, s=18, alpha=0.7, color=color, label=f"{algo} (R²={r2:.3f})")
            xs = np.linspace(min(x), max(x), 50)
            ax.plot(xs, slope * xs + icpt, color=color, lw=1)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("time (ms)")
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "sparse_time.png"), dpi=140)
    plt.close(fig)
    return stats


def mean_by_v(rows, kind, algo):
    by = {}
    for r in select(rows, kind, algo):
        by.setdefault(r["V"], []).append(r["seconds"])
    xs = sorted(by)
    return xs, [sum(by[v]) / len(by[v]) * 1000 for v in xs]


def plot_dense(rows) -> list[tuple]:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    for algo, color in (("Kruskal", "#2563eb"), ("Prim (heap)", "#dc2626"), ("Prim (dense)", "#16a34a")):
        xs, ys = mean_by_v(rows, "dense", algo)
        axes[0].plot(xs, ys, marker="o", color=color, label=algo)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("V (E ≈ V²/4)")
    axes[0].set_ylabel("mean time (ms)")
    axes[0].set_title("Dense graphs: three MST algorithms")
    axes[0].grid(alpha=0.3, which="both")
    axes[0].legend()

    for algo, color in (("Kruskal", "#2563eb"), ("Prim (heap)", "#dc2626"), ("Prim (dense)", "#16a34a")):
        xs, ys = mean_by_v(rows, "sparse", algo)
        if ys:
            axes[1].plot(xs, ys, marker="o", color=color, label=algo)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("V (E ≈ 3V)")
    axes[1].set_ylabel("mean time (ms)")
    axes[1].set_title("Sparse graphs: three MST algorithms")
    axes[1].grid(alpha=0.3, which="both")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "dense_vs_sparse.png"), dpi=140)
    plt.close(fig)

    table = []
    for v in DENSE_V:
        row = [v]
        for algo in ("Kruskal", "Prim (heap)", "Prim (dense)"):
            xs, ys = mean_by_v(rows, "dense", algo)
            row.append(ys[xs.index(v)])
        table.append(tuple(row))
    return table


def early_stop(rows) -> list[tuple]:
    out = []
    for kind in ("sparse", "dense"):
        by = {}
        for r in select(rows, kind, "Kruskal"):
            by.setdefault(r["V"], []).append(r["examined"] / r["E"])
        for v in sorted(by):
            out.append((kind, v, sum(by[v]) / len(by[v])))
    return out


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    rows = run()
    with open(os.path.join(OUT, "experiments.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    stats = plot_sparse(rows)
    dense = plot_dense(rows)
    stops = early_stop(rows)

    lines = ["# Experiment summary (generated)", "",
             "All MST algorithms returned the same total cost on every graph.", "",
             "## Linear fit of time against the predicted growth (sparse graphs)", "",
             "| Algorithm | x axis | slope (ns per unit) | R² |", "|---|---|---|---|"]
    xax = {"Kruskal": "E log2 V", "Prim (heap)": "E log2 V", "Dijkstra": "(V+E) log2 V"}
    for algo, (slope, r2) in stats.items():
        lines.append(f"| {algo} | {xax[algo]} | {slope:.3f} | {r2:.4f} |")
    lines += ["", "## Dense graphs (E ≈ V²/4), mean time in ms of 3 graphs", "",
              "| V | E | Kruskal | Prim (heap) | Prim (dense) |", "|---:|---:|---:|---:|---:|"]
    for v, k, p, pd in dense:
        lines.append(f"| {v} | {v * (v - 1) // 4} | {k:.1f} | {p:.1f} | {pd:.1f} |")
    lines += ["", "## Fraction of the sorted cables Kruskal examined before stopping", "",
              "| Graph | V | examined / E |", "|---|---:|---:|"]
    for kind, v, frac in stops:
        lines.append(f"| {kind} | {v} | {frac:.2f} |")
    with open(os.path.join(OUT, "summary.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
