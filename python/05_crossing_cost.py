"""Experiment 5: crossing from Python into C has a price.

If C is so fast, why not call a C function for every little operation?
Here we add two numbers one million times, a different way each time, and
measure the cost of a single call.

The lesson: the speed comes from doing MANY operations per trip into C,
not from C being involved at all.
"""
import timeit

import numpy as np

from common import load_fastmath, load_mymath

lib = load_mymath()
fastmath = load_fastmath()
N = 1_000_000


def py_add(a, b):
    return a + b


cases = [
    ("a + b (inline Python)", "a + b"),
    ("py_add(a, b) (Python function)", "py_add(a, b)"),
    ("fastmath.add(a, b) (C extension)", "fastmath.add(a, b)"),
    ("lib.add(a, b) (ctypes)", "lib.add(a, b)"),
    ("np.add(a, b) (NumPy on single numbers)", "np.add(a, b)"),
]
env = {"a": 7, "b": 35, "py_add": py_add, "fastmath": fastmath, "lib": lib, "np": np}

print(f"Cost of ONE call, measured over {N:,} calls (best of 5):")
for label, stmt in cases:
    best = min(timeit.repeat(stmt, globals=env, number=N, repeat=5))
    print(f"  {label:<40} {best / N * 1e9:7.1f} ns")

arr_a = np.full(N, 7, dtype=np.int64)
arr_b = np.full(N, 35, dtype=np.int64)
best = min(timeit.repeat(lambda: arr_a + arr_b, number=10, repeat=5)) / 10
print(f"\nOne NumPy call that adds {N:,} pairs at once: {best * 1e3:.2f} ms total, "
      f"{best / N * 1e9:.2f} ns per addition")
