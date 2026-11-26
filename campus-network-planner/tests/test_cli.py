import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import main as cli

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPUS = os.path.join(ROOT, "data", "campus.txt")


class CliTests(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_mst_all(self):
        code, out, _ = self.run_cli("mst", CAMPUS)
        self.assertEqual(code, 0)
        self.assertEqual(out.count("= 15"), 3)       # Kruskal, Prim, Prim (dense)

    def test_mst_trace(self):
        code, out, _ = self.run_cli("mst", CAMPUS, "--algo", "kruskal", "--trace")
        self.assertIn("skip: cycle", out)
        self.assertIn("2 + 2 + 3 + 3 + 5 = 15", out)

    def test_paths(self):
        code, out, _ = self.run_cli("paths", CAMPUS, "A", "--to", "F")
        self.assertEqual(code, 0)
        self.assertIn("distance 13", out)
        self.assertIn("A -> C -> D -> E -> F", out)

    def test_cluster(self):
        code, out, _ = self.run_cli("cluster", CAMPUS, "2")
        self.assertIn("A, B, C", out)
        self.assertIn("spacing", out)

    def test_negative_file_error(self):
        code, _, err = self.run_cli("paths", os.path.join(ROOT, "data", "negative.txt"), "A")
        self.assertEqual(code, 1)
        self.assertIn("non-negative", err)

    def test_missing_file(self):
        code, _, err = self.run_cli("mst", "nope.txt")
        self.assertEqual(code, 1)
        self.assertIn("error", err)

    def test_disconnected_warning(self):
        _, out, _ = self.run_cli("mst", os.path.join(ROOT, "data", "disconnected.txt"))
        self.assertIn("FOREST", out)
        self.assertIn("reached only 3 of 5", out)

    def test_generate_then_mst(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "g.txt")
            self.assertEqual(self.run_cli("generate", "30", "50", "--seed", "1", "--out", path)[0], 0)
            code, out, _ = self.run_cli("mst", path)
            self.assertEqual(code, 0)
            self.assertNotIn("ERROR", out)


if __name__ == "__main__":
    unittest.main()
