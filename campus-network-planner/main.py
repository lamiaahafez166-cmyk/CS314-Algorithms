"""Campus Network Planner: command line interface.

  python main.py mst      data/campus.txt --trace
  python main.py mst      data/campus.txt --algo prim --start A --png results/mst.png
  python main.py paths    data/campus.txt A --trace --to F
  python main.py cluster  data/campus.txt 2
  python main.py generate 50 100 --seed 1 --out data/random50.txt
"""

from __future__ import annotations

import argparse
import sys

from campusnet import (
    clusters, dijkstra, graph_to_text, kruskal, load_graph, prim, prim_dense, random_graph,
)
from campusnet.shortest import INF


# ----- text output ------------------------------------------------------------
def _fmt(x: float) -> str:
    return "inf" if x == INF else f"{x:g}"


def print_kruskal_trace(res) -> None:
    print(f"  {'Cable':<8}{'Cost':<6}Decision")
    for s in res.steps:
        print(f"  {str(s.edge):<8}{s.edge.w:<6g}{s.decision}")


def print_prim_trace(g, res) -> None:
    for s in res.steps:
        tree = s.tree
        leaving = sorted(
            (e for e in g.edges if (e.u in tree) != (e.v in tree)), key=lambda e: e.key()
        )
        cands = ", ".join(f"{e} {e.w:g}" for e in leaving)
        print(f"  Tree = {{{','.join(sorted(tree))}}}. Leaving: {cands}  ->  take {s.edge} ({s.edge.w:g})")


def print_mst(g, res, trace: bool) -> None:
    print(f"{res.name}:")
    if trace:
        if res.name == "Kruskal":
            print_kruskal_trace(res)
        else:
            print_prim_trace(g, res)
    cables = ", ".join(f"{e}({e.w:g})" for e in res.edges)
    total = " + ".join(f"{e.w:g}" for e in res.edges) or "0"
    print(f"  cables : {cables}")
    print(f"  total  : {total} = {res.total:g}")
    if res.spanning:
        print(f"  check  : {len(res.edges)} cables = V - 1 = {g.V - 1}, no cycle")
    else:
        if res.name == "Kruskal":
            print(f"  WARNING: graph is not connected: this is a minimum spanning FOREST "
                  f"with {res.components} trees, not a single tree")
        else:
            print(f"  WARNING: graph is not connected: Prim reached only {res.reached} of "
                  f"{g.V} buildings (the component of the start building)")


def cmd_mst(args) -> int:
    g = load_graph(args.file)
    start = args.start or g.nodes[0]
    print(f"Graph: V={g.V}, E={g.E}, connected={g.is_connected()}")
    if not g.is_connected():
        comps = [sorted(c) for c in g.components()]
        print(f"Components: {comps}")
    results = []
    if args.algo in ("kruskal", "all"):
        results.append(kruskal(g))
    if args.algo in ("prim", "all"):
        results.append(prim(g, start, trace=args.trace))
    if args.algo in ("prim-dense", "all"):
        results.append(prim_dense(g, start, trace=args.trace))
    for r in results:
        print_mst(g, r, args.trace)
    if len({round(r.total, 9) for r in results}) > 1 and all(r.spanning for r in results):
        print("ERROR: algorithms disagree on the total cost")
        return 2
    if args.png:
        from campusnet.visualize import save_mst_comparison
        save_mst_comparison(g, results, args.png)
        print(f"saved {args.png}")
    if args.gif:
        from campusnet.visualize import save_kruskal_gif
        save_kruskal_gif(g, kruskal(g), args.gif)
        print(f"saved {args.gif}")
    return 0


def cmd_paths(args) -> int:
    g = load_graph(args.file)
    sp = dijkstra(g, args.source, trace=args.trace)
    print(f"Dijkstra from {g.name(args.source)}  (V={g.V}, E={g.E})")
    if args.trace:
        nodes = g.nodes
        print("  " + f"{'Pick':<6}" + "".join(f"{n:<6}" for n in nodes))
        print("  " + f"{'start':<6}" + "".join(f"{('0' if n == args.source else 'inf'):<6}" for n in nodes))
        for pick, row in zip(sp.order, sp.table):
            print("  " + f"{pick:<6}" + "".join(f"{_fmt(row[n]):<6}" for n in nodes))
    targets = [args.to] if args.to else [n for n in g.nodes if n != args.source]
    for t in targets:
        path = sp.path_to(t)
        if path is None:
            print(f"  {g.name(t)}: unreachable")
        else:
            print(f"  {g.name(t)}: distance {_fmt(sp.dist[t])}   path {' -> '.join(path)}")
    if args.png:
        from campusnet.visualize import save_paths
        save_paths(g, sp, args.png)
        print(f"saved {args.png}")
    return 0


def cmd_cluster(args) -> int:
    g = load_graph(args.file)
    groups, spacing = clusters(g, args.k)
    print(f"{args.k} clusters (Kruskal stopped early):")
    for i, grp in enumerate(groups, 1):
        print(f"  cluster {i}: {', '.join(sorted(grp))}")
    if spacing is not None:
        print(f"  spacing (cheapest cable between clusters): {spacing:g}")
    return 0


def cmd_generate(args) -> int:
    g = random_graph(args.n, args.extra, args.max_cost, args.seed)
    text = graph_to_text(g)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"saved {args.out}: V={g.V}, E={g.E}")
    else:
        print(text, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Greedy algorithms on a campus network.")
    sub = p.add_subparsers(dest="command", required=True)

    m = sub.add_parser("mst", help="minimum spanning tree (Kruskal / Prim)")
    m.add_argument("file")
    m.add_argument("--algo", choices=["kruskal", "prim", "prim-dense", "all"], default="all")
    m.add_argument("--start", help="start building for Prim (default: first)")
    m.add_argument("--trace", action="store_true", help="print every decision")
    m.add_argument("--png")
    m.add_argument("--gif", help="animated Kruskal")
    m.set_defaults(func=cmd_mst)

    s = sub.add_parser("paths", help="shortest paths with Dijkstra")
    s.add_argument("file")
    s.add_argument("source")
    s.add_argument("--to", help="only this target")
    s.add_argument("--trace", action="store_true", help="print the distance table")
    s.add_argument("--png")
    s.set_defaults(func=cmd_paths)

    c = sub.add_parser("cluster", help="k clusters by stopping Kruskal early")
    c.add_argument("file")
    c.add_argument("k", type=int)
    c.set_defaults(func=cmd_cluster)

    g = sub.add_parser("generate", help="random connected graph")
    g.add_argument("n", type=int, help="number of buildings")
    g.add_argument("extra", type=int, help="cables beyond the n-1 of a tree")
    g.add_argument("--max-cost", type=int, default=100)
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
