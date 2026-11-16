"""Experiment 1: call a C function from Python with ctypes.

Steps:
  1. c/mymath.c is ordinary C (no Python headers).
  2. `make` compiles it into a shared library: build/libmymath.dylib (or .so).
  3. ctypes opens that library at runtime and calls functions inside it.
"""
from common import BUILD, LIB_NAME, load_mymath

lib = load_mymath()

print(f"Loaded {BUILD / LIB_NAME}")
print(f"add(2, 3)          = {lib.add(2, 3)}")
print(f"average(1.0, 2.0)  = {lib.average(1.0, 2.0)}")
print(f"type of lib.add    = {type(lib.add).__name__} (a wrapper around a C function pointer)")
