/*
 * mymath.c: plain C functions, no Python headers at all.
 *
 * This file knows nothing about Python. It gets compiled into a shared
 * library (libmymath.dylib on macOS, libmymath.so on Linux), and Python
 * loads it at runtime with the ctypes module.
 */
#include <stddef.h>
#include <stdint.h>

/* The "hello world" of calling C from Python. */
int add(int a, int b) {
    return a + b;
}

/* Returns a double, which matters: see python/02_types_matter.py. */
double average(double a, double b) {
    return (a + b) / 2.0;
}

/*
 * Sum of squares over a plain C array of 64-bit integers.
 * Python hands us a pointer to the first element plus a length,
 * the same way we pass arrays to functions in COMP 211.
 */
int64_t sum_squares(const int64_t *values, size_t n) {
    int64_t total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i] * values[i];
    }
    return total;
}

/*
 * Doubles every element in place. If Python sees the change afterwards,
 * that proves C and Python were looking at the exact same bytes in memory
 * (no copy was made).
 */
void double_in_place(int64_t *values, size_t n) {
    for (size_t i = 0; i < n; i++) {
        values[i] *= 2;
    }
}
