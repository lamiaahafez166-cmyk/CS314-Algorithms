import unittest

from mazesolver import parse_maze, generate_maze


class ParseTests(unittest.TestCase):
    def test_parse_lecture_example(self):
        m = parse_maze("S..#\n##..\n...E\n")
        self.assertEqual((m.rows, m.cols), (3, 4))
        self.assertEqual(m.start, (0, 0))
        self.assertEqual(m.end, (2, 3))

    def test_neighbors_skip_walls_and_borders(self):
        m = parse_maze("S..#\n##..\n...E\n")
        self.assertEqual(sorted(m.neighbors((0, 0))), [(0, 1)])
        self.assertEqual(sorted(m.neighbors((1, 2))), [(0, 2), (1, 3), (2, 2)])

    def test_graph_size(self):
        m = parse_maze("S..#\n##..\n...E\n")
        self.assertEqual(m.open_cells(), 9)
        self.assertEqual(m.edge_count(), 9)

    def test_missing_start(self):
        with self.assertRaisesRegex(ValueError, "no S"):
            parse_maze("...\n..E\n")

    def test_missing_end(self):
        with self.assertRaisesRegex(ValueError, "no E"):
            parse_maze("S..\n...\n")

    def test_two_starts(self):
        with self.assertRaisesRegex(ValueError, "more than one S"):
            parse_maze("S.S\n..E\n")

    def test_ragged_rows(self):
        with self.assertRaisesRegex(ValueError, "equal length"):
            parse_maze("S..\n.E\n")

    def test_illegal_character(self):
        with self.assertRaisesRegex(ValueError, "illegal"):
            parse_maze("S.x\n..E\n")

    def test_empty(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            parse_maze("   \n")

    def test_roundtrip(self):
        text = "S..#\n##..\n...E"
        self.assertEqual(parse_maze(text).to_text(), text)


class GeneratorTests(unittest.TestCase):
    def test_same_seed_same_maze(self):
        a = generate_maze(21, 21, 0.1, seed=5).to_text()
        b = generate_maze(21, 21, 0.1, seed=5).to_text()
        self.assertEqual(a, b)

    def test_even_sizes_round_up_to_odd(self):
        m = generate_maze(10, 10, seed=1)
        self.assertEqual((m.rows, m.cols), (11, 11))

    def test_perfect_maze_is_a_tree(self):
        # connected + |E| = |V| - 1  <=>  exactly one path between any two cells
        m = generate_maze(31, 31, 0.0, seed=2)
        self.assertEqual(m.edge_count(), m.open_cells() - 1)

    def test_loops_add_edges(self):
        perfect = generate_maze(31, 31, 0.0, seed=3)
        braided = generate_maze(31, 31, 0.3, seed=3)
        self.assertGreater(braided.edge_count(), perfect.edge_count())

    def test_bad_arguments(self):
        with self.assertRaises(ValueError):
            generate_maze(2, 5)
        with self.assertRaises(ValueError):
            generate_maze(5, 5, loop_prob=1.5)


if __name__ == "__main__":
    unittest.main()
