"""Experiment 2: ctypes trusts you about types, and C types are fixed width.

ctypes cannot see C's function prototypes, so if you do not declare a
function's types it assumes "takes ints, returns int". This script shows
what goes wrong when that assumption is false, and how fixed-width C ints
behave very differently from Python ints.
"""
import ctypes

from common import load_mymath, load_raw

print("A) Calling average() WITHOUT declaring its types")
raw = load_raw()
try:
    raw.average(1.0, 2.0)
except ctypes.ArgumentError as exc:
    print(f"   average(1.0, 2.0) -> ArgumentError: {exc}")

garbage = raw.average(ctypes.c_double(1.0), ctypes.c_double(2.0))
print(f"   average(c_double(1.0), c_double(2.0)) -> {garbage}   (wrong, and no error)")
print("   C put 1.5 in a floating-point register. ctypes assumed the return")
print("   type was int, so it read the integer register instead and got")
print("   whatever happened to be sitting there.")

print()
print("B) Same call WITH argtypes/restype declared")
lib = load_mymath()
print(f"   average(1.0, 2.0) -> {lib.average(1.0, 2.0)}")

print()
print("C) C ints are 32 bits; Python ints are unlimited")
big = 2**31  # one more than INT_MAX
print(f"   Python: (2**31 - 1) + 1     = {(2**31 - 1) + 1}")
print(f"   C:      add(2**31 - 1, 1)  = {lib.add(2**31 - 1, 1)}")
print(f"   ctypes.c_int(2**31).value  = {ctypes.c_int(big).value}")
print("   The bits wrap around (two's complement), just like in COMP 211.")
print("   (In real C, signed overflow is undefined behavior; we got the")
print("   hardware's wraparound here, but the compiler is allowed to do anything.)")
