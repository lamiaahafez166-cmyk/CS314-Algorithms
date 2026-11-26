"""Union-find (disjoint sets) with path compression and union by rank.
Each find/union costs almost constant time, O(alpha(V))."""

from __future__ import annotations


class UnionFind:
    def __init__(self, items) -> None:
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in self.parent}
        self.count = len(self.parent)  # number of sets

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # path compression (iterative)
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b) -> bool:
        """Merge the sets of a and b. Returns False if already in one set."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1
        return True
