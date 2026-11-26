# CS314 – Analysis of Algorithms: Mini Projects

**Author:** Lamiaa Mohamed Ahmed Mohamed Hafez · 
**Instructor:** Assoc. Prof. Mohamed Abd Elfattah

This repository contains one mini project for each lecture. Every project is self-contained (code, unit tests,
results, report) and has its own `README.md` with run instructions.

| Lecture | Topic | Project | Folder |
|---|---|---|---|
| 1 | Algorithms basics, Insertion Sort | Empirical analysis of Insertion Sort (compared with Merge Sort) | [lecture-1-insertion-sort](lecture-1-insertion-sort) |
| 2 | Divide and Conquer | Sorting Benchmark Lab (insertion, merge, quick, `sorted()`) | [lecture-2-sorting-benchmark-lab](lecture-2-sorting-benchmark-lab) |
| 3 | Heap Sort | Heap vs Quick vs Merge (Python + C++, cache behaviour) | [lecture-3-heap-vs-quick-vs-merge](lecture-3-heap-vs-quick-vs-merge) |

## Where to find what

* **Report:** `README.md` in lecture 1; `REPORT.md` in lectures 2 and 3.
* **Code:** `src/` (and `cpp/` in lecture 3). **Tests:** `tests/`. **Results and figures:** `results/`.
* **Demo script and reflection:** `docs/` in lectures 2 and 3.

## Quick start

```bash
cd lecture-2-sorting-benchmark-lab          # or any other project folder
pip install -r requirements.txt
python -m unittest discover -s tests -v
```
