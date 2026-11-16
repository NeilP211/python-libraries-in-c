"""Experiment 7: what is NumPy actually made of?

NumPy's fast parts are compiled C, shipped as shared library files that
end in .so (Linux and macOS) or .pyd (Windows). These are the same kind of
file as build/fastmath*.so in this repo, just much bigger.
"""
import inspect
from pathlib import Path

import numpy as np

pkg = Path(np.__file__).parent
compiled = sorted(
    [p for p in pkg.rglob("*") if p.suffix in (".so", ".pyd")],
    key=lambda p: p.stat().st_size,
    reverse=True,
)
py_files = list(pkg.rglob("*.py"))

print(f"NumPy {np.__version__} installed at {pkg}")
print(f"  {len(py_files)} Python files, {len(compiled)} compiled extension modules")
print("  Biggest compiled modules:")
for p in compiled[:5]:
    print(f"    {p.stat().st_size / 1e6:6.2f} MB  {p.relative_to(pkg)}")

print("\nAsk Python for the source code of np.add:")
try:
    inspect.getsource(np.add)
except TypeError as exc:
    print(f"  TypeError: {exc}")
print(f"  type(np.add) = {type(np.add)}  (a 'universal function' implemented in C)")
print(f"  np.add.types[:6] = {np.add.types[:6]}  (one C loop per input/output type)")

print("\nCompare a function that IS written in Python:")
src = inspect.getsource(np.linspace).splitlines()
print(f"  np.linspace has {len(src)} lines of Python source, starting with:")
print(f"    {next(line for line in src if line.strip().startswith('def'))}")
