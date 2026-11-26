"""Command line interface.

Examples
--------
  python main.py solve mazes/lecture_example.txt
  python main.py solve mazes/mud.txt --algos bfs dijkstra --png results/mud.png
  python main.py generate 41 41 --loops 0.05 --seed 1 --out mazes/m41.txt
  python main.py solve mazes/m41.txt --png results/m41.png --gif results/m41_bfs.gif
"""

from __future__ import annotations

import argparse
import sys

from mazesolver import SOLVERS, generate_maze, parse_maze, path_cost


def cmd_solve(args: argparse.Namespace) -> int:
    with open(args.file, encoding="utf-8") as fh:
        maze = parse_maze(fh.read())
    print(f"Maze {maze.rows}x{maze.cols}, |V|={maze.open_cells()}, |E|={maze.edge_count()}")
    results = []
    for name in args.algos:
        res = SOLVERS[name](maze)
        results.append(res)
        if res.path is None:
            print(f"{res.name:9s} no path, explored {res.explored_count} cells")
        else:
            print(
                f"{res.name:9s} moves={res.path_moves:<5d} cost={path_cost(maze, res.path):<5d} "
                f"explored={res.explored_count}"
            )
    if args.show:
        for res in results:
            print(f"\n{res.name}:")
            on_path = set(res.path or [])
            for r in range(maze.rows):
                line = []
                for c in range(maze.cols):
                    cell = (r, c)
                    if cell == maze.start:
                        line.append("S")
                    elif cell == maze.end:
                        line.append("E")
                    elif cell in on_path:
                        line.append("*")
                    else:
                        line.append(maze.grid[r][c])
                print("".join(line))
    if args.png:
        from mazesolver.visualize import save_comparison
        save_comparison(maze, results, args.png)
        print(f"saved {args.png}")
    if args.gif:
        from mazesolver.visualize import save_animation
        save_animation(maze, results[0], args.gif)
        print(f"saved {args.gif} (animation of {results[0].name})")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    maze = generate_maze(args.rows, args.cols, args.loops, args.seed)
    text = maze.to_text()
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"saved {args.out} ({maze.rows}x{maze.cols})")
    else:
        print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Solve mazes with BFS, DFS and Dijkstra.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("solve", help="solve a maze file")
    s.add_argument("file")
    s.add_argument("--algos", nargs="+", choices=list(SOLVERS), default=["bfs", "dfs"])
    s.add_argument("--show", action="store_true", help="print the maze with the path in the terminal")
    s.add_argument("--png", help="save a side-by-side picture")
    s.add_argument("--gif", help="save an animation of the first algorithm")
    s.set_defaults(func=cmd_solve)

    g = sub.add_parser("generate", help="generate a random maze")
    g.add_argument("rows", type=int)
    g.add_argument("cols", type=int)
    g.add_argument("--loops", type=float, default=0.0, help="probability of removing an extra wall (0-1)")
    g.add_argument("--seed", type=int)
    g.add_argument("--out")
    g.set_defaults(func=cmd_generate)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
