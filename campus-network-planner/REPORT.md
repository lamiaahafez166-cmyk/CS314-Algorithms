# Campus Network Planner: Greedy Graph Algorithms

**Course:** Analysis of Algorithms (CS314), Lecture 5: Greedy Algorithms

## 1. Problem

A campus has 6 buildings and 9 possible cables, each with a price (lecture example).
Two questions: (1) wire all buildings as cheaply as possible, and (2) find the
cheapest route from the Server Room (A) to every other building. Both are solved
with greedy algorithms, and compared experimentally.

## 2. Graph model

An **undirected weighted graph**. Vertices are buildings; an edge is a possible
cable with its cost as weight. Example: V = 6, E = 9. The graph is stored as
adjacency dictionaries plus an edge list (Kruskal needs the list, Prim and
Dijkstra need adjacency). Input is a small text file (`node`, `edge`, `pos` lines).

## 3. Algorithms, complexity and correctness

| Algorithm | Greedy rule | Time | Memory |
|---|---|---|---|
| Kruskal | Cheapest cable that makes no cycle (union-find) | O(E log V) | O(V + E) |
| Prim (heap) | Cheapest cable leaving the tree | O(E log V) | O(V + E) |
| Prim (dense) | Same rule, array instead of heap | O(V²) | O(V) |
| Dijkstra (heap) | Settle the closest unsettled building | O((V + E) log V) | O(V) |

* **Kruskal:** the sort costs O(E log E) = O(E log V) since E ≤ V². Union-find with
  path compression and union by rank costs almost constant time per call, so the
  loop is O(E α(V)). It stops after V − 1 cables.
* **Prim:** every building enters the tree once and every cable is pushed at most
  twice, so the heap has O(E) entries and total cost is O(E log V). The dense version
  scans an array V times: O(V²), better when E is close to V².
* **Why MST is correct:** the **cut property**. For any split of the buildings into two
  groups, the cheapest cable between the groups is in some MST. Both Kruskal and Prim
  only add such cables. (A test checks it directly: removing any MST edge, no
  cheaper cable reconnects the two halves.)
* **Dijkstra:** with non-negative costs, the closest unsettled building cannot be
  improved through any other unsettled building, so its distance is final. A negative
  cost breaks this, so the program **rejects** it.
* **Clustering (extension):** stopping Kruskal when *k* trees remain gives *k* groups.
  On the campus, k = 2 gives {A, B, C} and {D, E, F}, with spacing 5 (cable C-D).

### Check against the lecture

| Item | Lecture | Program |
|---|---|---|
| Kruskal decisions | take B-C, D-E, A-C, E-F; skip A-B; take C-D | same (test) |
| MST cost | 15 | 15 for Kruskal, Prim and dense Prim from every start |
| Dijkstra pick order from A | A, C, B, D, E, F | same |
| Distance to F | 13, through A, C, D, E | same |

The MST and the shortest-path tree are different trees: the MST uses B-C (2),
but the shortest path to B is the direct cable A-B (4). The MST minimises the *total*
cost; Dijkstra minimises the cost *to each building*.

## 4. Experiments

Random connected graphs (a random spanning tree plus extra cables, integer costs
1-10,000), 3 graphs per size, time = best of 3 runs, pure Python. Every graph was
solved by all MST algorithms and the totals were compared: **they always agreed.**

### 4.1 Sparse graphs (E ≈ 3V, V from 200 to 6,400)

![sparse](results/sparse_time.png)

| Algorithm | Fitted against | R² |
|---|---|---|
| Prim (heap) | E log₂ V | 0.984 |
| Dijkstra | (V + E) log₂ V | 0.987 |
| Kruskal | E log₂ V | 0.882 |

Prim and Dijkstra follow their predicted growth closely. Kruskal fits less well.
A likely reason: Python's built-in sort runs in C, so the E log E term is small
compared with the Python loop and union-find work, which are close to linear in E.
I did not test this explanation separately.

### 4.2 Dense graphs (E ≈ V²/4), mean time in ms

| V | E | Kruskal | Prim (heap) | Prim (dense) |
|---:|---:|---:|---:|---:|
| 80 | 1,580 | 0.8 | 0.5 | 0.6 |
| 160 | 6,360 | 3.5 | 2.0 | 2.2 |
| 320 | 25,520 | 16.6 | 8.2 | 8.9 |
| 640 | 102,240 | 84.9 | 35.5 | 35.8 |

![dense](results/dense_vs_sparse.png)

* Kruskal is the slowest on dense graphs: it sorts all 102,240 cables, and the sort
  key is a Python function called once per cable.
* The dense O(V²) Prim did **not** beat the heap version at these sizes
  (35.8 vs 35.5 ms). Theory says it should win as E approaches V², but in
  pure Python at V ≤ 640 the two are equal, so I cannot claim an advantage.

### 4.3 How early Kruskal stops

Kruskal stops after V − 1 cables, so it may not look at the whole sorted list.
It examined **99%** of the cables on sparse graphs (V = 6,400) but only **2%** on
dense graphs (V = 640), because many cheap cables connect everything quickly.

## 5. Conclusion

Kruskal, Prim and Dijkstra all use a priority order and a safe greedy choice, and
all were verified against the lecture numbers, a brute-force oracle and Bellman-Ford.
In practice: **Prim** or **Kruskal** both give the optimal MST; Kruskal is natural
when cables come as a price list and for clustering, Prim is faster on dense graphs
in my measurements. Use **Dijkstra** for routes from one building, only with
non-negative costs.

**Limits:** undirected graphs only; Python timings on one machine; 3 graphs per
size; random costs, not real campus data; not tested above V = 6,400.

*Reproduce:* `python experiments/run_experiments.py` (raw data in `results/experiments.csv`).
