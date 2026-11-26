# Reflection

**What surprised me**

* DFS is not just "BFS with a different data structure": on mazes with loops
  its path was up to 32 times longer than the shortest one, even though it
  explored fewer cells.
* The linear-time fit was weaker for BFS on perfect mazes. At first it looked
  like a bug; the reason is the early exit, so the work depends on where `E`
  is. Plotting time against explored cells made the linear relation clear.
* Marking a cell when it is pushed (BFS) and marking it when it is popped (DFS)
  are different choices. Marking DFS cells on push gives a valid path but not
  the real depth-first order.
* A perfect maze is a tree (|E| = |V| − 1), so BFS and DFS return the same path.
  I needed loops to see any difference, and I turned this into a test.

**What was hard**

Testing the search code itself: I wrote an independent relaxation oracle to
check BFS distances and checked every path step by step, instead of only
comparing path lengths.

**What I would do next**

* A* with the Manhattan distance heuristic and compare cells explored with BFS.
* Allow diagonal moves, and different costs per direction.
* Compare against `networkx` shortest paths as another check.
* Measure memory, not only time, and test bigger mazes (use a faster language
  or `numpy` for the grid).
* An interactive version in HTML + JavaScript where the user draws the walls.
