"""Dijkstra (shortest paths from one building) and a Bellman-Ford checker."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from .graph import Graph

INF = float("inf")


@dataclass
class ShortestPaths:
    source: str
    dist: dict[str, float]
    parent: dict[str, str | None]
    order: list[str]                                  # buildings in the order they were settled
    table: list[dict[str, float]] = field(default_factory=list)  # dist after each pick
    relaxed: int = 0                                  # edge relaxations that improved a distance

    def path_to(self, target: str) -> list[str] | None:
        """Path source -> target rebuilt from parent pointers, or None."""
        if target not in self.dist:
            raise ValueError(f"unknown building {target!r}")
        if self.dist[target] == INF:
            return None
        path, node = [], target
        while node is not None:
            path.append(node)
            node = self.parent[node]
        return path[::-1]


def dijkstra(g: Graph, source: str, trace: bool = False) -> ShortestPaths:
    """Dijkstra with a binary heap. Greedy rule: settle the closest unsettled
    building, then try to improve its neighbors.

    Time O((V + E) log V), memory O(V). Needs non-negative cable costs: a
    negative edge breaks the proof, so we reject it instead of returning
    wrong answers. Uses lazy deletion (stale heap entries are skipped), which
    is the usual replacement for decrease-key. `trace=True` records the distance
    table after every pick (a copy of dist per pick is O(V), so it is off by
    default to keep the algorithm O((V + E) log V)).
    """
    if source not in g.adj:
        raise ValueError(f"unknown building {source!r}")
    for e in g.edges:
        if e.w < 0:
            raise ValueError(
                f"Dijkstra needs non-negative costs, but {e} has cost {e.w}; use Bellman-Ford"
            )
    dist = {v: INF for v in g.adj}
    parent: dict[str, str | None] = {v: None for v in g.adj}
    dist[source] = 0
    heap = [(0, source)]
    settled: set[str] = set()
    order: list[str] = []
    table: list[dict[str, float]] = []
    relaxed = 0
    while heap:
        d, u = heapq.heappop(heap)
        if u in settled:
            continue                      # stale entry
        settled.add(u)
        order.append(u)
        for v, w in g.adj[u].items():
            if v not in settled and d + w < dist[v]:
                dist[v] = d + w
                parent[v] = u
                relaxed += 1
                heapq.heappush(heap, (dist[v], v))
        if trace:
            table.append(dict(dist))
    return ShortestPaths(source, dist, parent, order, table, relaxed)


def bellman_ford(g: Graph, source: str) -> dict[str, float]:
    """Slow but simple O(V*E) reference used only to check Dijkstra in tests."""
    dist = {v: INF for v in g.adj}
    dist[source] = 0
    for _ in range(g.V - 1):
        changed = False
        for e in g.edges:
            for a, b in ((e.u, e.v), (e.v, e.u)):
                if dist[a] + e.w < dist[b]:
                    dist[b] = dist[a] + e.w
                    changed = True
        if not changed:
            break
    return dist
