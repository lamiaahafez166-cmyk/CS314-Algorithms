import os
import unittest

from campusnet import bellman_ford, dijkstra, load_graph, parse_graph, random_graph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = float("inf")


def campus():
    return load_graph(os.path.join(ROOT, "data", "campus.txt"))


class LectureExampleTests(unittest.TestCase):
    def test_distances_from_A(self):
        sp = dijkstra(campus(), "A")
        self.assertEqual(sp.dist, {"A": 0, "B": 4, "C": 3, "D": 8, "E": 10, "F": 13})

    def test_pick_order_matches_slide(self):
        self.assertEqual(dijkstra(campus(), "A").order, ["A", "C", "B", "D", "E", "F"])

    def test_distance_table_matches_slide(self):
        sp = dijkstra(campus(), "A", trace=True)
        rows = [[r[n] for n in "ABCDEF"] for r in sp.table]
        self.assertEqual(rows, [
            [0, 4, 3, INF, INF, INF],
            [0, 4, 3, 8, 11, INF],
            [0, 4, 3, 8, 11, INF],
            [0, 4, 3, 8, 10, 14],
            [0, 4, 3, 8, 10, 13],
            [0, 4, 3, 8, 10, 13],
        ])

    def test_path_to_library(self):
        sp = dijkstra(campus(), "A")
        self.assertEqual(sp.path_to("F"), ["A", "C", "D", "E", "F"])
        self.assertEqual(sp.path_to("A"), ["A"])

    def test_shortest_path_tree_differs_from_mst(self):
        # slide: F is reached through D and E (13), not by the cheapest cable
        sp = dijkstra(campus(), "A")
        self.assertEqual(sp.parent["F"], "E")
        self.assertEqual(sp.parent["B"], "A")   # MST uses B-C (2), shortest path uses A-B (4)


class CorrectnessTests(unittest.TestCase):
    def test_against_bellman_ford(self):
        for seed in range(40):
            g = random_graph(40, 80, seed=seed)
            for source in ("v0", "v17"):
                self.assertEqual(dijkstra(g, source).dist, bellman_ford(g, source), f"seed {seed}")

    def test_path_cost_equals_distance(self):
        g = random_graph(50, 120, seed=9)
        sp = dijkstra(g, "v0")
        for t in g.nodes:
            path = sp.path_to(t)
            cost = sum(g.adj[a][b] for a, b in zip(path, path[1:]))
            self.assertEqual(cost, sp.dist[t])

    def test_zero_cost_edges(self):
        g = parse_graph("edge A B 0\nedge B C 0\nedge A C 5\n")
        self.assertEqual(dijkstra(g, "A").dist["C"], 0)


class EdgeCaseTests(unittest.TestCase):
    def test_unreachable(self):
        g = parse_graph("edge A B 1\nedge C D 1\n")
        sp = dijkstra(g, "A")
        self.assertEqual(sp.dist["C"], INF)
        self.assertIsNone(sp.path_to("C"))

    def test_negative_cost_rejected(self):
        g = parse_graph("edge A B 4\nedge B C -2\n")
        with self.assertRaisesRegex(ValueError, "non-negative"):
            dijkstra(g, "A")

    def test_unknown_source_and_target(self):
        g = campus()
        with self.assertRaises(ValueError):
            dijkstra(g, "Z")
        with self.assertRaises(ValueError):
            dijkstra(g, "A").path_to("Z")

    def test_single_building(self):
        g = parse_graph("node A\n")
        self.assertEqual(dijkstra(g, "A").dist, {"A": 0})


if __name__ == "__main__":
    unittest.main()
