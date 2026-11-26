"""Maze Solver: BFS vs DFS (and Dijkstra) on a grid treated as an implicit graph."""

from .maze import Maze, parse_maze
from .solvers import SolveResult, bfs, dfs, dijkstra, path_cost, SOLVERS
from .generator import generate_maze

__all__ = [
    "Maze", "parse_maze", "SolveResult", "bfs", "dfs", "dijkstra",
    "path_cost", "SOLVERS", "generate_maze",
]
