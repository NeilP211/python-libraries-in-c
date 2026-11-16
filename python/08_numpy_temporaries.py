"""Experiment 8: why did my plain C loop beat NumPy?

In the benchmark, `(arr * arr).sum()` was about 3x slower than the C loop
in c/mymath.c. The reason: NumPy runs ONE C loop per operation.

  arr * arr   loop 1: read arr, write every square into a brand new
              temporary array (80 MB for 10 million int64 values)
  .sum()      loop 2: read that temporary array again and add it up

The hand-written C loop squares and adds in a single pass and never
allocates anything. np.dot(arr, arr) is also a single pass, so it
catches up.
"""
import statistics
import sys
import timeit

import numpy as np

from common import as_int64_ptr, load_mymath

n = 100_000 if "--quick" in sys.argv else 10_000_000
lib = load_mymath()
arr = np.array([i % 1000 for i in range(n)], dtype=np.int64)
squares = arr * arr

cases = [
    ("(arr * arr).sum()   two loops + temp", lambda: (arr * arr).sum()),
    ("arr * arr           loop 1 alone", lambda: arr * arr),
    ("squares.sum()       loop 2 alone", lambda: squares.sum()),
    ("np.dot(arr, arr)    one loop, no temp", lambda: np.dot(arr, arr)),
    ("C sum_squares       one loop, no temp", lambda: lib.sum_squares(as_int64_ptr(arr), n)),
]

answers = {
    int((arr * arr).sum()),
    int(squares.sum()),
    int(np.dot(arr, arr)),
    lib.sum_squares(as_int64_ptr(arr), n),
}
assert len(answers) == 1, f"methods disagree: {answers}"

print(f"n = {n:,}, temporary array size = {squares.nbytes / 1e6:.0f} MB")
for label, fn in cases:
    ms = statistics.median(timeit.repeat(fn, number=3, repeat=5)) / 3 * 1e3
    print(f"  {label:<40} {ms:7.2f} ms")
