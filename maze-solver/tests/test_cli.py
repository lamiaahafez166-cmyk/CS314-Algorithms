import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

import main as cli

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CliTests(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_solve_example(self):
        code, out, _ = self.run_cli("solve", os.path.join(ROOT, "mazes", "lecture_example.txt"))
        self.assertEqual(code, 0)
        self.assertIn("BFS", out)
        self.assertIn("moves=5", out)

    def test_missing_file_returns_error_code(self):
        code, _, err = self.run_cli("solve", "does_not_exist.txt")
        self.assertEqual(code, 1)
        self.assertIn("error", err)

    def test_generate_to_file_then_solve(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "m.txt")
            self.assertEqual(self.run_cli("generate", "15", "15", "--seed", "1", "--out", path)[0], 0)
            code, out, _ = self.run_cli("solve", path, "--algos", "bfs", "dfs", "dijkstra")
            self.assertEqual(code, 0)
            self.assertIn("Dijkstra", out)


if __name__ == "__main__":
    unittest.main()
