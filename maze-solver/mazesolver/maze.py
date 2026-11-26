"""Maze model.

The maze is an *implicit graph*: we never build an adjacency list.
A vertex is an open cell (row, col); the neighbors of a vertex are the open
cells directly up, down, left and right of it.

File format (plain text, one row per line):
    #    wall
    .    open cell (cost 1)
    S    start
    E    end
    2-9  open "mud" cell with that movement cost (used by Dijkstra only)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

Cell = tuple[int, int]

# Fixed neighbor order (up, down, left, right). It affects which path DFS finds
# and which of several equally short paths BFS returns, so it is documented
# and kept constant to make every run reproducible.
DIRECTIONS: tuple[Cell, ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))


@dataclass
class Maze:
    grid: list[list[str]]
    start: Cell
    end: Cell
    rows: int = field(init=False)
    cols: int = field(init=False)

    def __post_init__(self) -> None:
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.grid else 0

    # ----- basic queries -------------------------------------------------
    def in_bounds(self, cell: Cell) -> bool:
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_open(self, cell: Cell) -> bool:
        return self.in_bounds(cell) and self.grid[cell[0]][cell[1]] != "#"

    def cost(self, cell: Cell) -> int:
        """Cost of *entering* a cell: 1 for normal cells, 2-9 for mud."""
        ch = self.grid[cell[0]][cell[1]]
        return int(ch) if ch.isdigit() else 1

    def neighbors(self, cell: Cell) -> Iterator[Cell]:
        r, c = cell
        for dr, dc in DIRECTIONS:
            nxt = (r + dr, c + dc)
            if self.is_open(nxt):
                yield nxt

    # ----- graph size (used by the experiments) --------------------------
    def open_cells(self) -> int:
        """|V|: number of open cells."""
        return sum(1 for row in self.grid for ch in row if ch != "#")

    def edge_count(self) -> int:
        """|E|: number of undirected edges (each adjacent open pair once)."""
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == "#":
                    continue
                if r + 1 < self.rows and self.grid[r + 1][c] != "#":
                    count += 1
                if c + 1 < self.cols and self.grid[r][c + 1] != "#":
                    count += 1
        return count

    # ----- text conversion -----------------------------------------------
    def to_text(self) -> str:
        rows = []
        for r, row in enumerate(self.grid):
            line = []
            for c, ch in enumerate(row):
                if (r, c) == self.start:
                    line.append("S")
                elif (r, c) == self.end:
                    line.append("E")
                else:
                    line.append(ch)
            rows.append("".join(line))
        return "\n".join(rows)


def parse_maze(text: str) -> Maze:
    """Parse maze text. Raises ValueError with a clear message on bad input."""
    lines = [ln.rstrip("\r") for ln in text.splitlines() if ln.strip() != ""]
    if not lines:
        raise ValueError("maze is empty")
    width = len(lines[0])
    start = end = None
    grid: list[list[str]] = []
    for r, line in enumerate(lines):
        if len(line) != width:
            raise ValueError(
                f"row {r} has length {len(line)}, expected {width} (rows must be equal length)"
            )
        row = []
        for c, ch in enumerate(line):
            if ch == "S":
                if start is not None:
                    raise ValueError("maze has more than one S")
                start = (r, c)
                row.append(".")
            elif ch == "E":
                if end is not None:
                    raise ValueError("maze has more than one E")
                end = (r, c)
                row.append(".")
            elif ch in "#." or ch in "23456789":
                row.append(ch)
            else:
                raise ValueError(f"illegal character {ch!r} at row {r}, col {c}")
        grid.append(row)
    if start is None:
        raise ValueError("maze has no S (start)")
    if end is None:
        raise ValueError("maze has no E (end)")
    return Maze(grid, start, end)
