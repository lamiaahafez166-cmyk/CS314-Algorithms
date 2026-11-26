import itertools
import os
import unittest

from campusnet import (
    clusters, kruskal, load_graph, parse_graph, prim, prim_dense, random_graph, UnionFind,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def campus():
    return load_graph(os.path.join(ROOT, "data", "campus.txt"))


def brute_force_mst_cost(g):
    """Try every set of V-1 edges; keep the cheapest one that connects all."""
    best = float("inf")
    for combo in itertools.combinations(g.edges, g.V - 1):
        uf = UnionFind(g.nodes)
        for e in combo:
            uf.union(e.u, e.v)
        if uf.count == 1:
            best = min(best, sum(e.w for e in combo))
    return best


def is_spanning_tree(g, edges):
    if len(edges) != g.V - 1:
        return False
    uf = UnionFind(g.nodes)
    return all(uf.union(e.u, e.v) for e in edges) and uf.count == 1


class LectureExampleTests(unittest.TestCase):
    def test_kruskal_total_15(self):
        r = kruskal(campus())
        self.assertEqual(r.total, 15)
        self.assertEqual([str(e) for e in r.edges], ["B-C", "D-E", "A-C", "E-F", "C-D"])

    def test_kruskal_decisions_match_slide(self):
        r = kruskal(campus())
        got = [(str(s.edge), s.edge.w, s.decision) for s in r.steps]
        self.assertEqual(got, [
            ("B-C", 2, "take"), ("D-E", 2, "take"), ("A-C", 3, "take"),
            ("E-F", 3, "take"), ("A-B", 4, "skip: cycle"), ("C-D", 5, "take"),
        ])
        self.assertEqual(r.examined, 6)          # "9 cables sorted, 6 examined"

    def test_prim_total_15_from_any_start(self):
        g = campus()
        for start in g.nodes:
            self.assertEqual(prim(g, start).total, 15, start)
            self.assertEqual(prim_dense(g, start).total, 15, start)

    def test_prim_order_from_A(self):
        r = prim(campus(), "A")
        self.assertEqual([str(e) for e in r.edges], ["A-C", "B-C", "C-D", "D-E", "E-F"])

    def test_clusters(self):
        groups, spacing = clusters(campus(), 2)
        self.assertEqual([sorted(x) for x in groups], [["A", "B", "C"], ["D", "E", "F"]])
        self.assertEqual(spacing, 5)

    def test_cluster_extremes(self):
        g = campus()
        groups, _ = clusters(g, 1)
        self.assertEqual(len(groups), 1)
        groups, spacing = clusters(g, 6)
        self.assertEqual(len(groups), 6)
        self.assertEqual(spacing, 2)             # cheapest cable overall
        with self.assertRaises(ValueError):
            clusters(g, 7)


class CorrectnessTests(unittest.TestCase):
    def test_against_brute_force(self):
        for seed in range(40):
            g = random_graph(6, 4, max_cost=10, seed=seed)   # many ties on purpose
            expected = brute_force_mst_cost(g)
            for result in (kruskal(g), prim(g, "v0"), prim_dense(g, "v3")):
                self.assertEqual(result.total, expected, f"{result.name} seed {seed}")
                self.assertTrue(is_spanning_tree(g, result.edges))

    def test_algorithms_agree_on_larger_graphs(self):
        for seed in range(30):
            g = random_graph(60, 150, seed=seed)
            totals = {kruskal(g).total, prim(g, "v0").total, prim_dense(g, "v7").total}
            self.assertEqual(len(totals), 1, f"seed {seed}: {totals}")

    def test_result_is_spanning_tree_with_v_minus_1_edges(self):
        g = random_graph(100, 300, seed=1)
        for r in (kruskal(g), prim(g, "v0"), prim_dense(g, "v0")):
            self.assertTrue(r.spanning)
            self.assertEqual(len(r.edges), g.V - 1)

    def test_tree_input_returns_all_edges(self):
        g = random_graph(30, 0, seed=2)
        self.assertEqual(kruskal(g).total, sum(e.w for e in g.edges))

    def test_cut_property_every_mst_edge_is_cheapest_across_some_cut(self):
        # Removing an MST edge splits the tree in two; no cheaper cable may join the halves.
        g = random_graph(25, 40, seed=3)
        r = kruskal(g)
        for removed in r.edges:
            uf = UnionFind(g.nodes)
            for e in r.edges:
                if e is not removed:
                    uf.union(e.u, e.v)
            crossing = [e.w for e in g.edges if uf.find(e.u) != uf.find(e.v)]
            self.assertGreaterEqual(min(crossing), removed.w)

    def test_negative_costs_are_fine_for_mst(self):
        g = parse_graph("edge A B -3\nedge B C 2\nedge A C 1\n")
        self.assertEqual(kruskal(g).total, -2)   # -3 and 1
        self.assertEqual(prim(g, "A").total, -2)


class EdgeCaseTests(unittest.TestCase):
    def test_disconnected_gives_forest(self):
        g = parse_graph("edge A B 2\nedge B C 4\nedge A C 5\nedge D E 1\n")
        k = kruskal(g)
        self.assertFalse(k.spanning)
        self.assertEqual(k.components, 2)
        self.assertEqual(k.total, 7)
        p = prim(g, "A")
        self.assertFalse(p.spanning)
        self.assertEqual(p.reached, 3)
        self.assertEqual(p.total, 6)
        pd = prim_dense(g, "D")
        self.assertEqual(pd.reached, 2)

    def test_single_building(self):
        g = parse_graph("node A\n")
        self.assertEqual(kruskal(g).total, 0)
        self.assertEqual(prim(g, "A").edges, [])
        self.assertTrue(prim(g, "A").spanning)

    def test_two_buildings(self):
        g = parse_graph("edge A B 9\n")
        self.assertEqual(prim_dense(g, "B").total, 9)

    def test_unknown_start(self):
        g = campus()
        with self.assertRaises(ValueError):
            prim(g, "Z")
        with self.assertRaises(ValueError):
            prim_dense(g, "Z")

    def test_bad_k(self):
        with self.assertRaises(ValueError):
            kruskal(campus(), 0)

    def test_equal_costs_everywhere(self):
        g = random_graph(20, 30, max_cost=1, seed=5)
        self.assertEqual(kruskal(g).total, 19)
        self.assertEqual(prim(g, "v0").total, 19)

    def test_float_costs(self):
        g = parse_graph("edge A B 1.5\nedge B C 2.25\nedge A C 4\n")
        self.assertAlmostEqual(kruskal(g).total, 3.75)


if __name__ == "__main__":
    unittest.main()
