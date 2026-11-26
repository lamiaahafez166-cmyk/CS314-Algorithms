import os
import unittest

from campusnet import UnionFind, load_graph, parse_graph, graph_to_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GraphTests(unittest.TestCase):
    def test_load_campus(self):
        g = load_graph(os.path.join(ROOT, "data", "campus.txt"))
        self.assertEqual((g.V, g.E), (6, 9))
        self.assertEqual(g.adj["B"]["D"], 7)
        self.assertEqual(g.labels["F"], "Library")
        self.assertTrue(g.is_connected())

    def test_components(self):
        g = parse_graph("edge A B 1\nedge C D 2\nnode E\n")
        self.assertEqual(sorted(sorted(c) for c in g.components()), [["A", "B"], ["C", "D"], ["E"]])
        self.assertFalse(g.is_connected())

    def test_roundtrip(self):
        g = parse_graph("node A Lab\nedge A B 4\nedge B C 2.5\n")
        g2 = parse_graph(graph_to_text(g))
        self.assertEqual((g2.V, g2.E), (3, 2))
        self.assertEqual(g2.adj["B"]["C"], 2.5)

    def test_comments_and_blank_lines(self):
        g = parse_graph("# hi\n\nedge A B 1  # trailing\n")
        self.assertEqual(g.E, 1)

    def test_errors(self):
        for text, msg in [
            ("edge A A 1", "self-loop"),
            ("edge A B 1\nedge B A 2", "duplicate"),
            ("edge A B", "edge needs"),
            ("edge A B x", "could not convert"),
            ("road A B 1", "unknown keyword"),
            ("pos A 1", "pos needs"),
            ("# nothing", "empty"),
        ]:
            with self.assertRaisesRegex(ValueError, msg):
                parse_graph(text)

    def test_error_mentions_line_number(self):
        with self.assertRaisesRegex(ValueError, "line 2"):
            parse_graph("edge A B 1\nedge B")


class UnionFindTests(unittest.TestCase):
    def test_union_find(self):
        uf = UnionFind("abcde")
        self.assertEqual(uf.count, 5)
        self.assertTrue(uf.union("a", "b"))
        self.assertTrue(uf.union("c", "d"))
        self.assertFalse(uf.union("b", "a"))
        self.assertNotEqual(uf.find("a"), uf.find("c"))
        self.assertTrue(uf.union("b", "d"))
        self.assertEqual(uf.find("a"), uf.find("c"))
        self.assertEqual(uf.count, 2)

    def test_long_chain_no_recursion_error(self):
        n = 50000
        uf = UnionFind(range(n))
        for i in range(n - 1):
            uf.union(i, i + 1)
        self.assertEqual(uf.count, 1)
        self.assertEqual(uf.find(0), uf.find(n - 1))


if __name__ == "__main__":
    unittest.main()
