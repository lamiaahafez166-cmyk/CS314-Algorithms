import unittest

from mazesolver import bfs, dfs, dijkstra, generate_maze, parse_maze, path_cost


def valid_path(maze, path):
    """Path starts at S, ends at E, every step is to an open neighbor."""
    if path[0] != maze.start or path[-1] != maze.end:
        return False
    return all(b in set(maze.neighbors(a)) for a, b in zip(path, path[1:]))


LECTURE = "S..#\n##..\n...E\n"
LOOPS = """#########
#S......#
#.#####.#
#.#...#.#
#.#.#.#.#
#...#..E#
#########
"""
MUD = """##########
#S...#...#
#.##.#.#.#
#.#..#.#.#
#.#.####.#
#.#......#
#.######.#
#...9999E#
##########
"""


class SolverTests(unittest.TestCase):
    def test_lecture_example_shortest_is_5_moves(self):
        m = parse_maze(LECTURE)
        res = bfs(m)
        self.assertEqual(res.path_moves, 5)
        self.assertTrue(valid_path(m, res.path))

    def test_dfs_finds_a_valid_path(self):
        m = parse_maze(LECTURE)
        res = dfs(m)
        self.assertTrue(res.found)
        self.assertTrue(valid_path(m, res.path))

    def test_dfs_can_be_longer_than_bfs(self):
        m = parse_maze(LOOPS)
        self.assertEqual(bfs(m).path_moves, 10)
        self.assertEqual(dfs(m).path_moves, 14)

    def test_no_path(self):
        m = parse_maze("S.#.E\n")
        for solver in (bfs, dfs, dijkstra):
            res = solver(m)
            self.assertFalse(res.found)
            self.assertIsNone(res.path)
            self.assertIsNone(res.path_moves)

    def test_start_equals_neighbor_end(self):
        m = parse_maze("SE\n")
        for solver in (bfs, dfs, dijkstra):
            self.assertEqual(solver(m).path, [(0, 0), (0, 1)])

    def test_explored_has_no_duplicates_and_starts_at_start(self):
        m = generate_maze(41, 41, 0.1, seed=7)
        for solver in (bfs, dfs, dijkstra):
            res = solver(m)
            self.assertEqual(len(res.explored), len(set(res.explored)))
            self.assertEqual(res.explored[0], m.start)

    def test_dijkstra_beats_bfs_on_mud(self):
        m = parse_maze(MUD)
        b, d = bfs(m), dijkstra(m)
        self.assertLess(path_cost(m, d.path), path_cost(m, b.path))
        self.assertEqual(path_cost(m, d.path), 15)

    def test_dijkstra_equals_bfs_without_mud(self):
        m = generate_maze(41, 41, 0.1, seed=11)
        self.assertEqual(dijkstra(m).path_moves, bfs(m).path_moves)

    def test_perfect_maze_has_unique_path(self):
        m = generate_maze(41, 41, 0.0, seed=4)
        self.assertEqual(bfs(m).path, dfs(m).path)

    def test_bfs_is_shortest_on_many_random_mazes(self):
        # Oracle: a plain Bellman-style relaxation that does not use BFS.
        for seed in range(15):
            m = generate_maze(21, 21, 0.15, seed=seed)
            dist = {m.start: 0}
            changed = True
            while changed:
                changed = False
                for cell in list(dist):
                    for nxt in m.neighbors(cell):
                        if dist.get(nxt, 10**9) > dist[cell] + 1:
                            dist[nxt] = dist[cell] + 1
                            changed = True
            self.assertEqual(bfs(m).path_moves, dist[m.end], f"seed {seed}")
            self.assertTrue(valid_path(m, dfs(m).path))
            self.assertGreaterEqual(dfs(m).path_moves, dist[m.end])

    def test_large_maze_no_recursion_error(self):
        m = generate_maze(401, 401, 0.02, seed=1)
        self.assertTrue(dfs(m).found)
        self.assertTrue(bfs(m).found)


if __name__ == "__main__":
    unittest.main()
