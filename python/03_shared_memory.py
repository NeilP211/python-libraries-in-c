"""Experiment 3: a NumPy array is a C array; a Python list is not.

Part A: hand C a pointer into a NumPy array, let C modify it, and watch the
change show up in Python. No copy is made: both sides share the same bytes.

Part B: look at the memory layout. NumPy elements sit next to each other
every 8 bytes. A list only stores pointers to int objects scattered around
the heap.
"""
import sys

import numpy as np

from common import as_int64_ptr, load_mymath

lib = load_mymath()

print("A) C writes into NumPy's memory")
arr = np.arange(1, 6, dtype=np.int64)
print(f"   before: {arr}")
lib.double_in_place(as_int64_ptr(arr), len(arr))
print(f"   after C's double_in_place(): {arr}")

print()
print("B) Where do the elements live?")
base = arr.ctypes.data
print(f"   NumPy int64 array, strides = {arr.strides} (bytes between elements)")
for i in range(len(arr)):
    addr = base + i * arr.strides[0]
    print(f"     arr[{i}] at {hex(addr)}  (+{addr - base} bytes)")

nums = [1000 + i for i in range(5)]  # > 256 so CPython does not reuse cached ints
print("   Python list: the list holds pointers; each int is its own heap object")
first = id(nums[0])
for i, x in enumerate(nums):
    print(f"     nums[{i}] object at {hex(id(x))}  ({id(x) - first:+d} bytes)")
print("   (In CPython, id() is the object's memory address.)")

print()
print("C) How much memory does one million integers take?")
n = 1_000_000
big_list = [1000 + (i % 1000) for i in range(n)]
big_arr = np.array(big_list, dtype=np.int64)
pointer_bytes = sys.getsizeof(big_list)
distinct = {id(x): x for x in big_list}  # each 1000 + k made a new object
object_bytes = sum(sys.getsizeof(x) for x in distinct.values())
print(f"   one Python int object: {sys.getsizeof(1000)} bytes  (header + value)")
print(f"   one NumPy int64:       {big_arr.itemsize} bytes  (just the value)")
print(f"   list: {pointer_bytes / 1e6:.1f} MB of pointers + "
      f"{object_bytes / 1e6:.1f} MB for {len(distinct):,} separate int objects")
print(f"   NumPy array: {big_arr.nbytes / 1e6:.1f} MB total")
