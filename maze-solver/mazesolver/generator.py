"""Random maze generator (used for tests and experiments)."""

from __future__ import annotations

import random

from .maze import Maze


def generate_maze(rows: int, cols: int, loop_prob: float = 0.0, seed: int | None = None) -> Maze:
    """Generate a solvable maze.

    rows and cols are rounded up to odd numbers. The maze is first made
    *perfect* (exactly one path between any two cells) with an iterative
    randomized depth-first "recursive backtracker". Then each remaining wall
    that separates two corridors is removed with probability `loop_prob`,
    which creates loops, i.e. several possible routes. Loops are what make
    BFS and DFS return different paths.

    Start is the top-left open cell, end is the bottom-right open cell.
    """
    if rows < 3 or cols < 3:
        raise ValueError("rows and cols must be at least 3")
    if not 0.0 <= loop_prob <= 1.0:
        raise ValueError("loop_prob must be between 0 and 1")
    rng = random.Random(seed)
    rows += (rows % 2 == 0)
    cols += (cols % 2 == 0)
    grid = [["#"] * cols for _ in range(rows)]

    grid[1][1] = "."
    stack = [(1, 1)]
    while stack:
        r, c = stack[-1]
        options = []
        for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and grid[nr][nc] == "#":
                options.append((nr, nc))
        if options:
            nr, nc = rng.choice(options)
            grid[(r + nr) // 2][(c + nc) // 2] = "."
            grid[nr][nc] = "."
            stack.append((nr, nc))
        else:
            stack.pop()

    if loop_prob > 0:
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if grid[r][c] != "#":
                    continue
                horizontal = (r % 2 == 1 and c % 2 == 0)
                vertical = (r % 2 == 0 and c % 2 == 1)
                if (horizontal or vertical) and rng.random() < loop_prob:
                    grid[r][c] = "."

    return Maze(grid, (1, 1), (rows - 2, cols - 2))
