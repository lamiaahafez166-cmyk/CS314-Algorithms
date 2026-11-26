"""Random connected graphs for tests and experiments."""

from __future__ import annotations

import random

from .graph import Graph


def random_graph(n: int, extra_edges: int, max_cost: int = 100, seed: int | None = None) -> Graph:
    """A connected graph with n buildings and (n - 1 + extra_edges) cables.

    A random spanning tree guarantees connectivity; then extra cables are added
    between random pairs that are not connected yet. Costs are integers in
    1..max_cost (ties are possible on purpose: they test tie handling)."""
    if n < 2:
        raise ValueError("n must be at least 2")
    if extra_edges < 0:
        raise ValueError("extra_edges must be >= 0")
    max_edges = n * (n - 1) // 2
    if n - 1 + extra_edges > max_edges:
        raise ValueError(f"too many edges: at most {max_edges} for n={n}")
    rng = random.Random(seed)
    g = Graph()
    names = [f"v{i}" for i in range(n)]
    for name in names:
        g.add_node(name)
    for i in range(1, n):                       # random tree
        g.add_edge(names[rng.randrange(i)], names[i], rng.randint(1, max_cost))
    added = 0
    while added < extra_edges:
        a, b = rng.sample(names, 2)
        if b not in g.adj[a]:
            g.add_edge(a, b, rng.randint(1, max_cost))
            added += 1
    return g
