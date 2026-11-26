// Heap sort vs quicksort vs merge sort in C++ (CS314 Lecture 3 mini project).
//
// Why C++?  In Python the interpreter overhead hides memory effects.  In compiled code
// the CPU cache dominates for large n, which is exactly the "gap" the project asks us
// to explain: heap sort jumps around memory (a[i] -> a[2i+1] -> a[4i+3] ...), while
// quicksort and merge sort scan the array sequentially.
//
// Build and run (from the project root):
//     g++ -O2 -std=c++17 -o cpp/bench cpp/bench.cpp
//     ./cpp/bench results/cpp_results.csv        # add "--quick" for n <= 1e6
//
// Output CSV columns: algorithm,n,time_ns,reps

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <numeric>
#include <random>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;

// ------------------------------------------------------------------ heap sort
static inline void sift_down(int* a, long i, long n) {
    while (true) {
        long l = 2 * i + 1, r = l + 1, largest = i;
        if (l < n && a[l] > a[largest]) largest = l;
        if (r < n && a[r] > a[largest]) largest = r;
        if (largest == i) return;
        std::swap(a[i], a[largest]);
        i = largest;
    }
}

static void heap_sort(int* a, long n) {
    for (long i = n / 2 - 1; i >= 0; --i) sift_down(a, i, n);   // BUILD-MAX-HEAP
    for (long end = n - 1; end > 0; --end) {
        std::swap(a[0], a[end]);
        sift_down(a, 0, end);
    }
}

// ------------------------------------------------------------------ merge sort
static void merge_rec(int* a, int* tmp, long lo, long hi) {      // sorts a[lo, hi)
    if (hi - lo < 2) return;
    long mid = lo + (hi - lo) / 2;
    merge_rec(a, tmp, lo, mid);
    merge_rec(a, tmp, mid, hi);
    long i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    std::memcpy(a + lo, tmp + lo, (hi - lo) * sizeof(int));
}

static void merge_sort(int* a, long n) {
    std::vector<int> tmp(n);
    merge_rec(a, tmp.data(), 0, n);
}

// ------------------------------------------------------------------ quicksort
// Last-element pivot (Lomuto), as in the lecture; recurse on the smaller part so the
// stack stays O(log n).
static void quick_rec(int* a, long p, long r) {
    while (p < r) {
        int pivot = a[r];
        long i = p - 1;
        for (long j = p; j < r; ++j)
            if (a[j] <= pivot) std::swap(a[++i], a[j]);
        std::swap(a[i + 1], a[r]);
        long q = i + 1;
        if (q - p < r - q) { quick_rec(a, p, q - 1); p = q + 1; }
        else               { quick_rec(a, q + 1, r); r = q - 1; }
    }
}

static void quick_sort(int* a, long n) { quick_rec(a, 0, n - 1); }

static void std_sort(int* a, long n) { std::sort(a, a + n); }

// ------------------------------------------------------------------ harness
struct Algo { const char* name; void (*fn)(int*, long); };

int main(int argc, char** argv) {
    std::string out_path = "results/cpp_results.csv";
    bool quick = false;
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "--quick") quick = true;
        else out_path = argv[i];
    }

    std::vector<long> sizes = {1000, 3000, 10000, 30000, 100000, 300000, 1000000};
    if (!quick) { sizes.push_back(3000000); sizes.push_back(10000000); }

    const Algo algos[] = {{"heap", heap_sort}, {"merge", merge_sort},
                          {"quick", quick_sort}, {"std_sort", std_sort}};

    FILE* out = std::fopen(out_path.c_str(), "w");
    if (!out) { std::perror("cannot open output file"); return 1; }
    std::fprintf(out, "algorithm,n,time_ns,reps\n");

    for (long n : sizes) {
        std::vector<int> base(n);
        std::iota(base.begin(), base.end(), 1);
        std::mt19937 rng(42 + (unsigned)n);
        std::shuffle(base.begin(), base.end(), rng);               // random permutation of 1..n

        int reps = n <= 100000 ? 15 : (n <= 1000000 ? 7 : 3);
        std::vector<int> work(n);

        for (const Algo& algo : algos) {
            std::vector<double> times;
            for (int rep = 0; rep < reps; ++rep) {
                std::copy(base.begin(), base.end(), work.begin()); // fresh copy (not timed)
                auto t0 = Clock::now();
                algo.fn(work.data(), n);
                auto t1 = Clock::now();
                times.push_back(std::chrono::duration<double, std::nano>(t1 - t0).count());
                if (rep == 0 && !std::is_sorted(work.begin(), work.end())) {
                    std::fprintf(stderr, "ERROR: %s produced an unsorted result (n=%ld)\n", algo.name, n);
                    return 2;
                }
            }
            std::sort(times.begin(), times.end());
            double median = times[times.size() / 2];
            std::fprintf(out, "%s,%ld,%.0f,%d\n", algo.name, n, median, reps);
            std::printf("n=%9ld  %-9s %12.3f ms  (%d reps)\n", n, algo.name, median / 1e6, reps);
            std::fflush(stdout);
        }
    }
    std::fclose(out);
    return 0;
}
