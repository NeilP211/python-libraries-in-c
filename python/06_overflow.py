"""Experiment 6: NumPy integers are C integers, so they can overflow.

Python's int grows to any size. NumPy stores fixed-width C integers, so it
inherits C's two's complement wraparound, and for whole arrays it does it
silently.
"""
import warnings

import numpy as np

INT64_MAX = 2**63 - 1

print("Python int:")
print(f"  {INT64_MAX} + 1 = {INT64_MAX + 1}")

print("\nNumPy int64 array (silent):")
arr = np.array([INT64_MAX], dtype=np.int64)
wrapped = arr + 1
print(f"  {arr} + 1 = {wrapped}")
print(f"  bits before: {int(arr[0]) & 0xFFFFFFFFFFFFFFFF:064b}")
print(f"  bits after:  {int(wrapped[0]) & 0xFFFFFFFFFFFFFFFF:064b}")
print("  0111...1 + 1 = 1000...0, and a leading 1 means negative in two's complement.")

print("\nNumPy int64 scalar (warns, still wraps):")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    result = np.int64(INT64_MAX) + np.int64(1)
print(f"  np.int64({INT64_MAX}) + 1 = {result}")
for w in caught:
    print(f"  warning: {w.message}")

print("\nA realistic way to hit it: summing a big int8 image")
pixels = np.full(1000, 100, dtype=np.int8)  # 1000 pixels, each value 100
print(f"  pixels.dtype = {pixels.dtype}, pixels[:3] = {pixels[:3]}")
print(f"  (pixels + pixels)[:3] = {(pixels + pixels)[:3]}   (100 + 100 does not fit in int8)")
print(f"  pixels.sum() = {pixels.sum()}   (NumPy widens for sum(), so this one is fine)")
