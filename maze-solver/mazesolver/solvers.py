"""BFS, DFS and Dijkstra on a Maze.

Every solver returns a SolveResult with:
    path      list of cells from start to end, or None if unreachable
    explored  cells in the order they were *expanded* (popped and processed)
    name      algorithm name

Design notes
------------
* We never store whole paths in the queue/stack. Each solver keeps a `parent`
  dictionary (the pi[v] of the lecture) and rebuilds the path at the end.
* Everything is iterative, so large mazes cannot hit Python's recursion limit.
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass

from .maze import Cell, Maze


@dataclass
class SolveResult:
    name: str
    path: list[Cell] | None
    explored: list[Cell]

    @property
    def found(self) -> bool:
        return self.path is not None

    @property
    def path_moves(self) -> int | None:
        """Number of moves (edges) on the path."""
        return None if self.path is None else len(self.path) - 1

    @property
    def explored_count(self) -> int:
        return len(self.explored)


def _rebuild(parent: dict[Cell, Cell | None], end: Cell) -> list[Cell]:
    path = []
    node: Cell | None = end
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def bfs(maze: Maze) -> SolveResult:
    """Breadth-first search with a queue. Fewest moves. O(V + E)."""
    start, end = maze.start, maze.end
    parent: dict[Cell, Cell | None] = {start: None}  # doubles as the visited set
    queue: deque[Cell] = deque([start])
    explored: list[Cell] = []
    while queue:
        cell = queue.popleft()
        explored.append(cell)
        if cell == end:
            return SolveResult("BFS", _rebuild(parent, end), explored)
        for nxt in maze.neighbors(cell):
            if nxt not in parent:  # mark visited when pushed, never pushed twice
                parent[nxt] = cell
                queue.append(nxt)
    return SolveResult("BFS", None, explored)


def dfs(maze: Maze) -> SolveResult:
    """Depth-first search with an explicit stack. Any path, not always shortest.
    O(V + E).

    A cell is marked visited when it is popped (not when pushed), together with
    the cell it was reached from. This gives a true "go deep first" order, the
    same order as the recursive DFS of the lecture.
    """
    start, end = maze.start, maze.end
    parent: dict[Cell, Cell | None] = {}
    stack: list[tuple[Cell, Cell | None]] = [(start, None)]
    explored: list[Cell] = []
    while stack:
        cell, came_from = stack.pop()
        if cell in parent:
            continue
        parent[cell] = came_from
        explored.append(cell)
        if cell == end:
            return SolveResult("DFS", _rebuild(parent, end), explored)
        # reversed() so that the first neighbor in DIRECTIONS is explored first
        for nxt in reversed(list(maze.neighbors(cell))):
            if nxt not in parent:
                stack.append((nxt, cell))
    return SolveResult("DFS", None, explored)


def dijkstra(maze: Maze) -> SolveResult:
    """Dijkstra with a binary heap (extension). Cheapest path when cells have
    weights 2-9 (mud). O((V + E) log V). With all weights 1 it equals BFS in
    path cost."""
    start, end = maze.start, maze.end
    dist: dict[Cell, int] = {start: 0}
    parent: dict[Cell, Cell | None] = {start: None}
    done: set[Cell] = set()
    heap: list[tuple[int, Cell]] = [(0, start)]
    explored: list[Cell] = []
    while heap:
        d, cell = heapq.heappop(heap)
        if cell in done:
            continue
        done.add(cell)
        explored.append(cell)
        if cell == end:
            return SolveResult("Dijkstra", _rebuild(parent, end), explored)
        for nxt in maze.neighbors(cell):
            nd = d + maze.cost(nxt)
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                parent[nxt] = cell
                heapq.heappush(heap, (nd, nxt))
    return SolveResult("Dijkstra", None, explored)


def path_cost(maze: Maze, path: list[Cell]) -> int:
    """Total cost of entering every cell of the path after the start."""
    return sum(maze.cost(c) for c in path[1:])


SOLVERS = {"bfs": bfs, "dfs": dfs, "dijkstra": dijkstra}
