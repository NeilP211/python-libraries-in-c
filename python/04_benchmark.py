"""Experiment 4: benchmark the same computation six ways.

Task: sum of squares, total = x0*x0 + x1*x1 + ... over n integers.

  python loop      a plain `for` loop in Python
  python sum()     built-in sum() over a generator expression
  C over list      C extension that walks a Python list (still boxed ints)
  C via ctypes     plain C loop over NumPy's raw buffer, called with ctypes
  C extension      same C loop, called through the extension module
  numpy            (arr * arr).sum(), which runs NumPy's own C loops

Fairness rules:
  * Every method gets the same data, and we check they all return the same
    answer before timing anything.
  * Building the list / array is NOT timed (we time only the computation),
    but we report the list -> NumPy conversion cost separately, because in
    real code your data might start as a list.
  * Each measurement repeats until it runs for at least 0.2 s, and we take
    the median of 5 such measurements to smooth out noise from other
    programs, CPU frequency changes, and caches.

Usage:
  python3 04_benchmark.py            full run (n up to 10 million, about a minute)
  python3 04_benchmark.py --quick    tiny sizes, used by the tests
"""
import argparse
import csv
import platform
import statistics
import sys
import timeit
from pathlib import Path

import numpy as np

from common import ROOT, as_int64_ptr, load_fastmath, load_mymath

lib = load_mymath()
fastmath = load_fastmath()


def python_loop(data):
    total = 0
    for x in data:
        total += x * x
    return total


def python_sum(data):
    return sum(x * x for x in data)


def c_over_list(data):
    return fastmath.sum_squares_list(data)


def c_ctypes(arr):
    return lib.sum_squares(as_int64_ptr(arr), len(arr))


def c_extension(arr):
    return fastmath.sum_squares_buffer(arr)


def numpy_way(arr):
    return int((arr * arr).sum())


# (label, function, uses_list)
METHODS = [
    ("python loop", python_loop, True),
    ("python sum()", python_sum, True),
    ("C over list", c_over_list, True),
    ("C via ctypes", c_ctypes, False),
    ("C extension", c_extension, False),
    ("numpy", numpy_way, False),
]


def measure(fn, arg, repeats):
    """Median seconds per call, using timeit's autorange to pick a loop count."""
    timer = timeit.Timer(lambda: fn(arg))
    loops, _ = timer.autorange()  # enough loops for >= 0.2 s
    runs = timer.repeat(repeat=repeats, number=loops)
    return statistics.median(runs) / loops


def fmt(seconds):
    if seconds >= 1:
        return f"{seconds:.2f} s"
    if seconds >= 1e-3:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds * 1e6:.1f} us"


def make_data(n):
    data = [i % 1000 for i in range(n)]  # small values: no overflow anywhere
    arr = np.array(data, dtype=np.int64)
    return data, arr


def run(sizes, repeats, out_csv=None, plot_path=None):
    rows = []
    for n in sizes:
        data, arr = make_data(n)
        expected = python_loop(data)
        for label, fn, uses_list in METHODS:
            got = fn(data if uses_list else arr)
            if got != expected:
                raise AssertionError(f"{label} returned {got}, expected {expected}")

        convert = measure(lambda d: np.array(d, dtype=np.int64), data, repeats)
        times = {}
        for label, fn, uses_list in METHODS:
            times[label] = measure(fn, data if uses_list else arr, repeats)

        base = times["python loop"]
        print(f"\nn = {n:,}   (all methods agree: {expected:,})")
        for label, _, _ in METHODS:
            t = times[label]
            print(f"  {label:<14} {fmt(t):>10}   {base / t:7.1f}x vs python loop")
        print(f"  {'(list->numpy)':<14} {fmt(convert):>10}   one-time conversion cost")
        for label in times:
            rows.append({"n": n, "method": label, "seconds": times[label]})
        rows.append({"n": n, "method": "list->numpy conversion", "seconds": convert})

    if out_csv:
        with open(out_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["n", "method", "seconds"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote {out_csv}")
    if plot_path:
        plot(rows, plot_path)
    return rows


def plot(rows, path):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping the plot")
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, _, _ in METHODS:
        pts = [(r["n"], r["seconds"]) for r in rows if r["method"] == label]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", label=label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n (number of integers)")
    ax.set_ylabel("seconds per run (median, log scale)")
    ax.set_title("Sum of squares: Python vs C vs NumPy")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Wrote {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="tiny sizes for tests")
    args = parser.parse_args()

    print(f"Python {platform.python_version()}, NumPy {np.__version__}, "
          f"{platform.machine()} {platform.system()}")
    if args.quick:
        run([1_000, 10_000], repeats=3)
    else:
        results = ROOT / "results"
        results.mkdir(exist_ok=True)
        tag = f"{platform.system().lower()}-{platform.machine()}"
        run([1_000, 10_000, 100_000, 1_000_000, 10_000_000], repeats=5,
            out_csv=results / f"benchmark-{tag}.csv",
            plot_path=results / f"benchmark-{tag}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
