"""Experiments: running time vs |V|+|E|, and BFS vs DFS path length / work.

Run from the project root:  python experiments/run_experiments.py
Writes results/*.csv and results/*.png
"""

from __future__ import annotations

import csv
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from mazesolver import bfs, dfs, dijkstra, generate_maze

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
SIZES = [21, 41, 81, 161, 321, 641, 961]
LOOP_PROBS = [0.0, 0.05]          # perfect maze, and maze with loops
SEEDS = [1, 2, 3, 4, 5]           # 5 random mazes per (size, loop_prob)
REPEATS = 3                       # timing: best of 3, to reduce noise


def best_time(solver, maze) -> float:
    best = float("inf")
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        solver(maze)
        best = min(best, time.perf_counter() - t0)
    return best


def run() -> list[dict]:
    rows = []
    for loops in LOOP_PROBS:
        for n in SIZES:
            for seed in SEEDS:
                maze = generate_maze(n, n, loops, seed)
                v, e = maze.open_cells(), maze.edge_count()
                for solver in (bfs, dfs, dijkstra):
                    res = solver(maze)
                    rows.append({
                        "loops": loops, "size": maze.rows, "seed": seed,
                        "V": v, "E": e, "V_plus_E": v + e,
                        "algo": res.name, "moves": res.path_moves,
                        "explored": res.explored_count,
                        "seconds": best_time(solver, maze),
                    })
            print(f"done loops={loops} size={n}", flush=True)
    return rows


def save_csv(rows: list[dict]) -> None:
    with open(os.path.join(OUT, "experiments.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def fit_line(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * np.array(x) + intercept
    ss_res = float(np.sum((np.array(y) - pred) ** 2))
    ss_tot = float(np.sum((np.array(y) - np.mean(y)) ** 2))
    return slope, intercept, 1 - ss_res / ss_tot


def plot_time(rows) -> dict:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    stats = {}
    for ax, loops in zip(axes, LOOP_PROBS):
        for algo, color in (("BFS", "#2563eb"), ("DFS", "#dc2626")):
            sel = [r for r in rows if r["loops"] == loops and r["algo"] == algo]
            x = [r["V_plus_E"] for r in sel]
            y = [r["seconds"] * 1000 for r in sel]
            slope, icpt, r2 = fit_line(x, y)
            stats[(loops, algo)] = (slope * 1000, r2)  # microseconds per unit
            ax.scatter(x, y, s=14, alpha=0.6, color=color, label=f"{algo} (R²={r2:.3f})")
            xs = np.linspace(min(x), max(x), 50)
            ax.plot(xs, slope * xs + icpt, color=color, lw=1)
        kind = "perfect maze" if loops == 0 else f"loops p={loops}"
        ax.set_title(f"Running time vs |V|+|E|  ({kind})")
        ax.set_xlabel("|V| + |E|")
        ax.set_ylabel("time (ms)")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "time_vs_V_plus_E.png"), dpi=140)
    plt.close(fig)
    return stats


def plot_work(rows) -> dict:
    """Time against the number of cells actually expanded (early exit makes
    the work smaller than |V|+|E|, so this is the fairer x axis)."""
    fig, ax = plt.subplots(figsize=(5.5, 4.3))
    stats = {}
    for algo, color in (("BFS", "#2563eb"), ("DFS", "#dc2626")):
        sel = [r for r in rows if r["algo"] == algo]
        x = [r["explored"] for r in sel]
        y = [r["seconds"] * 1000 for r in sel]
        slope, icpt, r2 = fit_line(x, y)
        stats[algo] = (slope * 1000, r2)
        ax.scatter(x, y, s=10, alpha=0.5, color=color, label=f"{algo} (R²={r2:.3f})")
        xs = np.linspace(min(x), max(x), 50)
        ax.plot(xs, slope * xs + icpt, color=color, lw=1)
    ax.set_title("Running time vs cells explored (all mazes)")
    ax.set_xlabel("cells explored")
    ax.set_ylabel("time (ms)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "time_vs_explored.png"), dpi=140)
    plt.close(fig)
    return stats


def aggregate(rows, loops, algo, size, key):
    vals = [r[key] for r in rows if r["loops"] == loops and r["algo"] == algo and r["size"] == size]
    return statistics.mean(vals)


def plot_compare(rows) -> list[tuple]:
    sizes = sorted({r["size"] for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    table = []
    loops = 0.05
    for ax, key, title in (
        (axes[0], "moves", "Path length (moves)"),
        (axes[1], "explored", "Cells explored"),
    ):
        for algo, color in (("BFS", "#2563eb"), ("DFS", "#dc2626")):
            ys = [aggregate(rows, loops, algo, s, key) for s in sizes]
            ax.plot(sizes, ys, marker="o", color=color, label=algo)
        ax.set_title(f"{title}, mazes with loops (p={loops}), mean of {len(SEEDS)}")
        ax.set_xlabel("maze side length")
        ax.set_yscale("log")
        ax.grid(alpha=0.3, which="both")
        ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "bfs_vs_dfs.png"), dpi=140)
    plt.close(fig)
    for s in sizes:
        table.append((
            s,
            aggregate(rows, loops, "BFS", s, "moves"), aggregate(rows, loops, "DFS", s, "moves"),
            aggregate(rows, loops, "BFS", s, "explored"), aggregate(rows, loops, "DFS", s, "explored"),
        ))
    return table


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    rows = run()
    save_csv(rows)
    stats = plot_time(rows)
    table = plot_compare(rows)
    work = plot_work(rows)

    lines = ["# Experiment summary (generated)", "",
             "## Linear fit of time against |V|+|E|", "",
             "| Mazes | Algorithm | slope (µs per unit of V+E) | R² |", "|---|---|---|---|"]
    for (loops, algo), (slope, r2) in stats.items():
        kind = "perfect" if loops == 0 else f"loops p={loops}"
        lines.append(f"| {kind} | {algo} | {slope:.3f} | {r2:.4f} |")
    lines += ["", "## Linear fit of time against cells explored (all mazes)", "",
              "| Algorithm | slope (µs per explored cell) | R² |", "|---|---|---|"]
    for algo, (slope, r2) in work.items():
        lines.append(f"| {algo} | {slope:.3f} | {r2:.4f} |")
    lines += ["", "## BFS vs DFS on mazes with loops (p=0.05), mean of 5 mazes", "",
              "| Side | BFS moves | DFS moves | BFS explored | DFS explored |", "|---|---|---|---|---|"]
    for s, bm, dm, be, de in table:
        lines.append(f"| {s} | {bm:.0f} | {dm:.0f} | {be:.0f} | {de:.0f} |")
    with open(os.path.join(OUT, "summary.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
