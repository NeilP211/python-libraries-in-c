"""Tests: the C code gives the same answers as Python, and every script runs.

Run with `make test` (it builds first).
"""
import array
import ctypes
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

PYTHON_DIR = Path(__file__).resolve().parent.parent / "python"
sys.path.insert(0, str(PYTHON_DIR))

from common import as_int64_ptr, load_fastmath, load_mymath  # noqa: E402

lib = load_mymath()
fastmath = load_fastmath()


def reference_sum_squares(values):
    return sum(int(x) * int(x) for x in values)


# ---------- ctypes library (c/mymath.c) ----------

@pytest.mark.parametrize("a,b", [(2, 3), (0, 0), (-5, 5), (-7, -8), (2**30, 2**30 - 1)])
def test_add_matches_python(a, b):
    assert lib.add(a, b) == a + b


def test_add_wraps_like_32_bit_int():
    assert lib.add(2**31 - 1, 1) == -(2**31)


def test_average_returns_a_double():
    assert lib.average(1.0, 2.0) == 1.5
    assert lib.average(-3.0, 4.0) == 0.5


def test_average_without_restype_is_wrong():
    """Undeclared restype makes ctypes read an int, so we never get 1.5 back."""
    raw = ctypes.CDLL(lib._name)
    result = raw.average(ctypes.c_double(1.0), ctypes.c_double(2.0))
    assert isinstance(result, int)
    assert result != 1.5


def test_average_without_argtypes_rejects_floats():
    raw = ctypes.CDLL(lib._name)
    with pytest.raises(ctypes.ArgumentError):
        raw.average(1.0, 2.0)


@pytest.mark.parametrize("values", [[], [7], [1, 2, 3], [-4, 5, -6], list(range(1000))])
def test_ctypes_sum_squares(values):
    arr = np.array(values, dtype=np.int64)
    assert lib.sum_squares(as_int64_ptr(arr), len(arr)) == reference_sum_squares(values)


def test_double_in_place_shares_memory():
    arr = np.arange(1, 6, dtype=np.int64)
    address_before = arr.ctypes.data
    lib.double_in_place(as_int64_ptr(arr), len(arr))
    assert arr.tolist() == [2, 4, 6, 8, 10]
    assert arr.ctypes.data == address_before


def test_as_int64_ptr_rejects_wrong_dtype_and_views():
    with pytest.raises(TypeError):
        as_int64_ptr(np.arange(5, dtype=np.int32))
    with pytest.raises(TypeError):
        as_int64_ptr(np.arange(10, dtype=np.int64)[::2])  # strided, not contiguous


# ---------- extension module (c/fastmath_module.c) ----------

@pytest.mark.parametrize("a,b", [(2, 3), (-10, 4), (2**40, 2**40)])
def test_extension_add(a, b):
    assert fastmath.add(a, b) == a + b


def test_extension_add_rejects_non_ints():
    with pytest.raises(TypeError):
        fastmath.add("2", 3)


@pytest.mark.parametrize("values", [[], [7], [1, 2, 3], [-4, 5, -6], list(range(1000))])
def test_extension_sum_squares_buffer_and_list(values):
    expected = reference_sum_squares(values)
    assert fastmath.sum_squares_buffer(np.array(values, dtype=np.int64)) == expected
    assert fastmath.sum_squares_buffer(array.array("q", values)) == expected
    assert fastmath.sum_squares_list(list(values)) == expected


def test_extension_buffer_rejects_wrong_types():
    with pytest.raises(TypeError):
        fastmath.sum_squares_buffer(np.arange(5, dtype=np.float64))
    with pytest.raises(TypeError):
        fastmath.sum_squares_buffer(np.arange(5, dtype=np.int32))
    with pytest.raises(TypeError):
        fastmath.sum_squares_buffer([1, 2, 3])  # a list has no raw buffer
    with pytest.raises((TypeError, BufferError, ValueError)):
        fastmath.sum_squares_buffer(np.arange(10, dtype=np.int64)[::2])


def test_extension_list_rejects_bad_items():
    with pytest.raises(TypeError):
        fastmath.sum_squares_list([1, "two", 3])
    with pytest.raises(OverflowError):
        fastmath.sum_squares_list([2**70])
    with pytest.raises(TypeError):
        fastmath.sum_squares_list((1, 2, 3))  # tuple, not list


# ---------- NumPy behavior the talk relies on ----------

def test_numpy_int64_array_wraps():
    arr = np.array([2**63 - 1], dtype=np.int64)
    assert (arr + 1)[0] == -(2**63)


def test_numpy_int8_add_wraps_but_sum_widens():
    pixels = np.full(1000, 100, dtype=np.int8)
    assert (pixels + pixels)[0] == -56
    assert pixels.sum() == 100_000


# ---------- every experiment script runs ----------

SCRIPTS = [
    ["01_hello_ctypes.py"],
    ["02_types_matter.py"],
    ["03_shared_memory.py"],
    ["04_benchmark.py", "--quick"],
    ["05_crossing_cost.py"],
    ["06_overflow.py"],
    ["07_inside_numpy.py"],
    ["08_numpy_temporaries.py", "--quick"],
]


@pytest.mark.parametrize("cmd", SCRIPTS, ids=[c[0] for c in SCRIPTS])
def test_script_runs(cmd):
    result = subprocess.run(
        [sys.executable, cmd[0], *cmd[1:]],
        cwd=PYTHON_DIR, capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()
