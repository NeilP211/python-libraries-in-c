"""Shared helpers: find the build/ folder and load the two C libraries."""
import ctypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
LIB_NAME = "libmymath.dylib" if sys.platform == "darwin" else "libmymath.so"

INT64_PTR = ctypes.POINTER(ctypes.c_int64)


def load_raw():
    """Load libmymath with NO type information (ctypes has to guess)."""
    path = BUILD / LIB_NAME
    if not path.exists():
        raise SystemExit(f"{path} not found. Run `make` in {ROOT} first.")
    return ctypes.CDLL(str(path))


def load_mymath():
    """Load libmymath and tell ctypes each function's real C signature.

    This is the Python version of writing function prototypes in a .h file:
    ctypes cannot read C headers, so we have to declare the types ourselves.
    """
    lib = load_raw()

    lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.add.restype = ctypes.c_int

    lib.average.argtypes = [ctypes.c_double, ctypes.c_double]
    lib.average.restype = ctypes.c_double

    lib.sum_squares.argtypes = [INT64_PTR, ctypes.c_size_t]
    lib.sum_squares.restype = ctypes.c_int64

    lib.double_in_place.argtypes = [INT64_PTR, ctypes.c_size_t]
    lib.double_in_place.restype = None

    return lib


def load_fastmath():
    """Import the compiled extension module from build/."""
    if str(BUILD) not in sys.path:
        sys.path.insert(0, str(BUILD))
    try:
        import fastmath
    except ImportError as exc:
        raise SystemExit(f"fastmath not built ({exc}). Run `make` in {ROOT} first.")
    return fastmath


def as_int64_ptr(arr):
    """Pointer to the first element of a NumPy int64 array (no copy)."""
    if arr.dtype.name != "int64" or not arr.flags["C_CONTIGUOUS"]:
        raise TypeError("need a contiguous int64 array")
    return arr.ctypes.data_as(INT64_PTR)
