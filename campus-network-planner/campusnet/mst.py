"""Minimum spanning tree: Kruskal and Prim (heap and dense versions).

All three are greedy. Both rules are justified by the cut property: for any
split of the buildings into two groups, the cheapest cable between the groups
belongs to some MST.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from .graph import Edge, Graph
from .unionfind import UnionFind


@dataclass
class Step:
    """One decision, used for the step-by-step trace."""
    edge: Edge
    decision: str                       # "take" or "skip: cycle"
    tree: frozenset[str] | None = None  # Prim only: tree before this step


@dataclass
class MSTResult:
    name: str
    edges: list[Edge]
    total: float
    spanning: bool          # True if the result connects every building
    components: int         # number of trees in the result (Prim always builds 1)
    examined: int           # edges looked at (Kruskal) or heap pops / scans (Prim)
    reached: int = 0        # buildings covered by the result's tree(s)
    steps: list[Step] = field(default_factory=list)


def kruskal(g: Graph, k: int = 1) -> MSTResult:
    """Kruskal: sort cables by cost, take each one that makes no cycle.

    Time O(E log E) = O(E log V) for the sort, plus O(E alpha(V)) for union-find.
    Stops when only k trees are left (k = 1 gives the MST). On a disconnected
    graph it returns a minimum spanning *forest* (spanning = False).
    """
    if k < 1:
        raise ValueError("k must be at least 1")
    uf = UnionFind(g.nodes)
    taken: list[Edge] = []
    steps: list[Step] = []
    examined = 0
    for e in sorted(g.edges, key=Edge.key):
        if uf.count <= k:
            break
        examined += 1
        if uf.union(e.u, e.v):
            taken.append(e)
            steps.append(Step(e, "take"))
        else:
            steps.append(Step(e, "skip: cycle"))
    return MSTResult("Kruskal", taken, sum(e.w for e in taken),
                     uf.count == 1, uf.count, examined, g.V, steps)


def prim(g: Graph, start: str, trace: bool = False) -> MSTResult:
    """Prim with a binary heap (lazy deletion): grow one tree from `start`,
    always adding the cheapest cable that leaves the tree.

    Time O(E log V), memory O(V + E). Only the component of `start` is covered.
    `trace=True` also records the tree before each step (copying it costs O(V)
    per step, so it is off by default to keep the algorithm O(E log V)).
    """
    if start not in g.adj:
        raise ValueError(f"unknown building {start!r}")
    in_tree = {start}
    # heap items: (cost, tree_end, new_end)
    heap = [(w, start, v) for v, w in g.adj[start].items()]
    heapq.heapify(heap)
    taken: list[Edge] = []
    steps: list[Step] = []
    pops = 0
    while heap and len(in_tree) < g.V:
        w, u, v = heapq.heappop(heap)
        pops += 1
        if v in in_tree:
            continue                      # stale entry: v was added meanwhile
        steps.append(Step(Edge(u, v, w), "take", frozenset(in_tree) if trace else None))
        taken.append(Edge(u, v, w))
        in_tree.add(v)
        for x, wx in g.adj[v].items():
            if x not in in_tree:
                heapq.heappush(heap, (wx, v, x))
    return MSTResult("Prim", taken, sum(e.w for e in taken),
                     len(in_tree) == g.V, 1, pops, len(in_tree), steps)


def prim_dense(g: Graph, start: str, trace: bool = False) -> MSTResult:
    """Prim with plain arrays instead of a heap: O(V^2).

    Best on dense graphs (E close to V^2), where it beats O(E log V)."""
    if start not in g.adj:
        raise ValueError(f"unknown building {start!r}")
    INF = float("inf")
    best: dict[str, float] = {v: INF for v in g.adj}   # cheapest cable into the tree
    via: dict[str, str | None] = {v: None for v in g.adj}
    best[start] = 0
    remaining = set(g.adj)
    taken: list[Edge] = []
    steps: list[Step] = []
    in_tree: set[str] = set()
    scans = 0
    while remaining:
        u = min(remaining, key=lambda x: (best[x], x))   # O(V) scan
        scans += 1
        if best[u] == INF:
            break                                         # rest is unreachable
        remaining.discard(u)
        if via[u] is not None:
            e = Edge(via[u], u, best[u])
            taken.append(e)
            steps.append(Step(e, "take", frozenset(in_tree) if trace else None))
        in_tree.add(u)
        for x, wx in g.adj[u].items():
            if x in remaining and wx < best[x]:
                best[x] = wx
                via[x] = u
    return MSTResult("Prim (dense)", taken, sum(e.w for e in taken),
                     len(in_tree) == g.V, 1, scans, len(in_tree), steps)


def clusters(g: Graph, k: int) -> tuple[list[set[str]], float | None]:
    """Cluster buildings into k groups by stopping Kruskal early.

    Returns (groups, spacing) where spacing is the cheapest cable that joins two
    different groups (the larger it is, the better separated the groups)."""
    if k > g.V:
        raise ValueError("k cannot be larger than the number of buildings")
    uf = UnionFind(g.nodes)
    spacing = None
    for e in sorted(g.edges, key=Edge.key):
        if uf.count > k:
            uf.union(e.u, e.v)
        elif uf.find(e.u) != uf.find(e.v):
            spacing = e.w
            break
    groups: dict[str, set[str]] = {}
    for n in g.nodes:
        groups.setdefault(uf.find(n), set()).add(n)
    return sorted(groups.values(), key=lambda s: sorted(s)[0]), spacing
