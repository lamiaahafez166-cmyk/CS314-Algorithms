"""Drawing helpers (matplotlib) for mazes, paths and explored cells."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from .maze import Maze
from .solvers import SolveResult

# 0 wall, 1 open, 2 explored, 3 path, 4 start, 5 end, 6 mud
_COLORS = ["#1f2937", "#f9fafb", "#bfdbfe", "#f59e0b", "#16a34a", "#dc2626", "#a16207"]
_CMAP = ListedColormap(_COLORS)


def _image(maze: Maze, result: SolveResult | None, upto: int | None = None) -> np.ndarray:
    img = np.ones((maze.rows, maze.cols), dtype=int)
    for r in range(maze.rows):
        for c in range(maze.cols):
            ch = maze.grid[r][c]
            if ch == "#":
                img[r, c] = 0
            elif ch.isdigit():
                img[r, c] = 6
    if result is not None:
        cells = result.explored if upto is None else result.explored[:upto]
        for r, c in cells:
            img[r, c] = 2
        if result.path and (upto is None or upto >= len(result.explored)):
            for r, c in result.path:
                img[r, c] = 3
    img[maze.start] = 4
    img[maze.end] = 5
    return img


def draw_maze(maze: Maze, result: SolveResult | None = None, ax=None, title: str | None = None):
    own = ax is None
    if own:
        _, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(_image(maze, result), cmap=_CMAP, vmin=0, vmax=6, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=10)
    return ax


def save_comparison(maze: Maze, results: list[SolveResult], filename: str) -> None:
    """Side-by-side picture of several solvers on the same maze."""
    fig, axes = plt.subplots(1, len(results), figsize=(5 * len(results), 5.3))
    if len(results) == 1:
        axes = [axes]
    for ax, res in zip(axes, results):
        moves = "no path" if res.path is None else f"{res.path_moves} moves"
        draw_maze(maze, res, ax, f"{res.name}: {moves}, {res.explored_count} cells explored")
    fig.tight_layout()
    fig.savefig(filename, dpi=130)
    plt.close(fig)


def save_animation(maze: Maze, result: SolveResult, filename: str, frames: int = 60, fps: int = 12) -> None:
    """Animated GIF of how a solver explores the maze (needs Pillow)."""
    from matplotlib.animation import FuncAnimation, PillowWriter

    total = len(result.explored)
    step = max(1, total // frames)
    marks = list(range(0, total, step)) + [total]
    fig, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(_image(maze, result, 0), cmap=_CMAP, vmin=0, vmax=6, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])

    def update(i):
        n = marks[i]
        im.set_data(_image(maze, result, n))
        ax.set_title(f"{result.name}: {n}/{total} cells explored", fontsize=10)
        return [im]

    anim = FuncAnimation(fig, update, frames=len(marks), blit=False)
    anim.save(filename, writer=PillowWriter(fps=fps))
    plt.close(fig)
