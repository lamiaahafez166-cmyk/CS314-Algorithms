"""Weighted undirected graph for the campus network.

Text format (one item per line, '#' starts a comment):
    node A Server Room        a building (the label is optional)
    pos  A 0 1                optional x y position, used only for drawing
    edge A B 4                a possible cable between A and B with cost 4
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Edge:
    u: str
    v: str
    w: float

    def key(self) -> tuple[float, str, str]:
        """Sort key: cost first, then names, so every run is reproducible."""
        a, b = sorted((self.u, self.v))
        return (self.w, a, b)

    def __str__(self) -> str:
        a, b = sorted((self.u, self.v))
        return f"{a}-{b}"


class Graph:
    def __init__(self) -> None:
        self.labels: dict[str, str] = {}
        self.pos: dict[str, tuple[float, float]] = {}
        self.adj: dict[str, dict[str, float]] = {}
        self.edges: list[Edge] = []

    # ----- building ---------------------------------------------------------
    def add_node(self, name: str, label: str | None = None) -> None:
        if name not in self.adj:
            self.adj[name] = {}
        if label:
            self.labels[name] = label

    def add_edge(self, u: str, v: str, w: float) -> None:
        if u == v:
            raise ValueError(f"self-loop on {u} is not allowed")
        if v in self.adj.get(u, {}):
            raise ValueError(f"duplicate edge {u}-{v}")
        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = w
        self.adj[v][u] = w
        self.edges.append(Edge(u, v, w))

    # ----- queries ----------------------------------------------------------
    @property
    def nodes(self) -> list[str]:
        return sorted(self.adj)

    @property
    def V(self) -> int:
        return len(self.adj)

    @property
    def E(self) -> int:
        return len(self.edges)

    def name(self, node: str) -> str:
        """Building name for output, e.g. 'A (Server Room)'."""
        return f"{node} ({self.labels[node]})" if node in self.labels else node

    def components(self) -> list[set[str]]:
        seen: set[str] = set()
        comps: list[set[str]] = []
        for s in self.nodes:
            if s in seen:
                continue
            comp = {s}
            stack = [s]
            while stack:
                x = stack.pop()
                for y in self.adj[x]:
                    if y not in comp:
                        comp.add(y)
                        stack.append(y)
            seen |= comp
            comps.append(comp)
        return comps

    def is_connected(self) -> bool:
        return self.V > 0 and len(self.components()) == 1


def parse_graph(text: str) -> Graph:
    g = Graph()
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        kind = parts[0].lower()
        try:
            if kind == "node":
                if len(parts) < 2:
                    raise ValueError("node needs a name")
                g.add_node(parts[1], " ".join(parts[2:]) or None)
            elif kind == "pos":
                if len(parts) != 4:
                    raise ValueError("pos needs: pos NAME x y")
                g.pos[parts[1]] = (float(parts[2]), float(parts[3]))
            elif kind == "edge":
                if len(parts) != 4:
                    raise ValueError("edge needs: edge U V cost")
                w = float(parts[3])
                g.add_edge(parts[1], parts[2], int(w) if w == int(w) else w)
            else:
                raise ValueError(f"unknown keyword {parts[0]!r}")
        except ValueError as exc:
            raise ValueError(f"line {lineno}: {exc}") from None
    if g.V == 0:
        raise ValueError("graph is empty")
    return g


def load_graph(path: str) -> Graph:
    with open(path, encoding="utf-8") as fh:
        return parse_graph(fh.read())


def graph_to_text(g: Graph) -> str:
    lines = []
    for n in g.nodes:
        lines.append(f"node {n} {g.labels.get(n, '')}".rstrip())
    for e in g.edges:
        lines.append(f"edge {e.u} {e.v} {e.w}")
    return "\n".join(lines) + "\n"
