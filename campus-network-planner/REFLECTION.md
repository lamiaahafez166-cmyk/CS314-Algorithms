# Reflection

**What surprised me**

* My first experiment showed Prim and Dijkstra growing like V², not like
  E log V. The cause was my own tracing code: it copied the tree or the distance
  table at every step, which costs O(V) per step. After making tracing opt-in
  (`--trace`), both algorithms scaled as predicted (R² of 0.98+). The lesson is
  that a harmless-looking convenience can change the complexity class.
* The MST and the shortest-path tree are really different. Same graph, same
  greedy style, different answers: the MST uses B-C (2) while Dijkstra
  reaches B directly with A-B (4).
* The "faster" dense Prim was not faster in my tests. I expected it to win and
  I report the real result instead.
* Kruskal examined 99% of the cables on sparse graphs but only 2% on dense ones.

**What was hard**

Making the tests strong. For the MST I used a brute-force search over every set
of V − 1 cables as the oracle, and Bellman-Ford for Dijkstra. One of my own
test expectations was wrong (the MST with a negative cable); the program
was right, so I corrected the test, not the code.

**What I would do next**

* Test with a real campus or road dataset instead of random costs.
* Compare against `networkx` as a second check, and use a Fibonacci-heap-style
  decrease-key to see if it matters in practice.
* Add A* for one target and compare explored buildings with Dijkstra.
* Add Huffman coding from the same lecture as a second tool.
* An interactive page where the user draws the campus and watches Kruskal.
