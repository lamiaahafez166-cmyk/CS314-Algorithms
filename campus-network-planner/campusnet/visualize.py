"""Pictures of the campus graph (matplotlib). Node positions come from the
`pos` lines of the data file, or from a circular layout if they are missing."""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .graph import Edge, Graph
from .mst import MSTResult
from .shortest import ShortestPaths

GRAY, ORANGE, GREEN, RED, BLUE = "#9ca3af", "#f59e0b", "#16a34a", "#dc2626", "#2563eb"


def layout(g: Graph) -> dict[str, tuple[float, float]]:
    if all(n in g.pos for n in g.nodes):
        return dict(g.pos)
    n = g.V
    return {
        name: (math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n))
        for i, name in enumerate(g.nodes)
    }


def _edge_key(e: Edge) -> frozenset:
    return frozenset((e.u, e.v))


def draw_graph(g: Graph, ax, highlight=(), colors=None, title="", node_text=None, dashed=()):
    """Draw g. `highlight` edges are thick; `colors` maps an edge key to a color."""
    pos = layout(g)
    hl = {_edge_key(e) for e in highlight}
    dashed_keys = {_edge_key(e) for e in dashed}
    colors = colors or {}
    for e in g.edges:
        k = _edge_key(e)
        (x1, y1), (x2, y2) = pos[e.u], pos[e.v]
        on = k in hl
        ax.plot([x1, x2], [y1, y2],
                color=colors.get(k, ORANGE if on else GRAY),
                lw=3.2 if on else 1.3,
                ls="--" if k in dashed_keys else "-", zorder=1)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, f"{e.w:g}", fontsize=9, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9), zorder=3)
    for n in g.nodes:
        x, y = pos[n]
        ax.scatter([x], [y], s=900, color="#1f2937", zorder=4)
        ax.text(x, y, n, color="white", ha="center", va="center", fontsize=11, fontweight="bold", zorder=5)
        if node_text and n in node_text:
            ax.text(x, y - 0.22, node_text[n], ha="center", va="top", fontsize=9, color=BLUE, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.9))
    ax.set_title(title, fontsize=10)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.margins(0.18)


def save_mst_comparison(g: Graph, results: list[MSTResult], filename: str) -> None:
    fig, axes = plt.subplots(1, len(results), figsize=(5.2 * len(results), 4.6))
    if len(results) == 1:
        axes = [axes]
    for ax, r in zip(axes, results):
        draw_graph(g, ax, r.edges, title=f"{r.name}: total cost {r.total:g}")
    fig.tight_layout()
    fig.savefig(filename, dpi=130)
    plt.close(fig)


def save_paths(g: Graph, sp: ShortestPaths, filename: str) -> None:
    tree = [Edge(sp.parent[v], v, g.adj[v][sp.parent[v]]) for v in g.nodes if sp.parent[v] is not None]
    text = {n: ("d=inf" if sp.dist[n] == float("inf") else f"d={sp.dist[n]:g}") for n in g.nodes}
    fig, ax = plt.subplots(figsize=(6, 4.6))
    draw_graph(g, ax, tree, title=f"Dijkstra from {sp.source}: shortest-path tree", node_text=text)
    fig.tight_layout()
    fig.savefig(filename, dpi=130)
    plt.close(fig)


def save_kruskal_gif(g: Graph, result: MSTResult, filename: str, fps: float = 1.0) -> None:
    """Animated GIF of Kruskal: green = take, red dashed = skip (cycle)."""
    from matplotlib.animation import FuncAnimation, PillowWriter

    fig, ax = plt.subplots(figsize=(6, 4.6))
    steps = result.steps

    def update(i):
        ax.clear()
        colors, taken, skipped = {}, [], []
        total = 0
        for s in steps[:i]:
            if s.decision == "take":
                colors[_edge_key(s.edge)] = GREEN
                taken.append(s.edge)
                total += s.edge.w
            else:
                colors[_edge_key(s.edge)] = RED
                skipped.append(s.edge)
        if i == 0:
            msg = "Kruskal: cables sorted by cost"
        else:
            s = steps[i - 1]
            msg = f"step {i}: {s.edge} cost {s.edge.w:g} -> {s.decision}   (total {total:g})"
        draw_graph(g, ax, taken + skipped, colors, msg, dashed=skipped)

    anim = FuncAnimation(fig, update, frames=len(steps) + 1, repeat=False)
    anim.save(filename, writer=PillowWriter(fps=fps))
    plt.close(fig)
