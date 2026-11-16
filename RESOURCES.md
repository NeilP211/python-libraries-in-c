# Resources

References I used while exploring this topic.

## Official documentation

- [ctypes: a foreign function library for Python](https://docs.python.org/3/library/ctypes.html): loading shared libraries, `argtypes` / `restype`, passing pointers.
- [Extending Python with C or C++](https://docs.python.org/3/extending/extending.html): how a C extension module like `fastmath` is structured (`PyMethodDef`, `PyModuleDef`, `PyInit_...`).
- [Parsing arguments and building values](https://docs.python.org/3/c-api/arg.html): the `PyArg_ParseTuple` format codes (`"LL"`, `"O!"`).
- [Buffer protocol](https://docs.python.org/3/c-api/buffer.html): how C code gets a raw pointer into a NumPy array or `array.array` without copying.
- [timeit: measure execution time of small code snippets](https://docs.python.org/3/library/timeit.html): `autorange()` and `repeat()`, used by the benchmarks.
- [NumPy: What is NumPy?](https://numpy.org/doc/stable/user/whatisnumpy.html): why fixed-type, contiguous arrays let NumPy push loops into compiled code.
- [NumPy: Internal organization of NumPy arrays](https://numpy.org/doc/stable/dev/internals.html): data buffer plus metadata (dtype, shape, strides).
- [NumPy: Universal functions (ufunc)](https://numpy.org/doc/stable/reference/ufuncs.html): what `np.add` really is, and its per-type loops (`np.add.types`).
- [NumPy: Data types, overflow errors](https://numpy.org/doc/stable/user/basics.types.html#overflow-errors): fixed-width integers wrap around.

## Source code

- [numpy/numpy on GitHub](https://github.com/numpy/numpy): the C sources live under `numpy/_core/src/` (for example `multiarray/` and `umath/`).
- [CPython `Objects/longobject.c`](https://github.com/python/cpython/blob/main/Objects/longobject.c): how a Python `int` is stored, which explains the 28 bytes per int.

## Articles

- Jake VanderPlas, [Why Python is Slow: Looking Under the Hood](https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/) (2014): dynamic typing, boxed objects, and why NumPy arrays avoid that overhead.
