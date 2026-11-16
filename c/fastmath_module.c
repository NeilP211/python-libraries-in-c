/*
 * fastmath_module.c: a tiny CPython extension module.
 *
 * Unlike mymath.c, this file includes Python.h and speaks Python's C API
 * directly. After compiling it, Python can simply `import fastmath`, the
 * same way it imports NumPy (NumPy's core is a much bigger module built
 * the same way).
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <string.h>

/* fastmath.add(a, b): unpack two Python ints into C, add, box the result. */
static PyObject *fastmath_add(PyObject *self, PyObject *args) {
    (void) self; /* the module object; these functions do not need it */
    long long a, b;
    if (!PyArg_ParseTuple(args, "LL", &a, &b)) {
        return NULL; /* PyArg_ParseTuple already set a TypeError */
    }
    return PyLong_FromLongLong(a + b);
}

/* True if a buffer's format string describes a native 8-byte signed int. */
static int is_int64_format(const char *fmt, Py_ssize_t itemsize) {
    if (fmt == NULL || itemsize != 8) {
        return 0;
    }
    if (*fmt == '@' || *fmt == '=') {
        fmt++;
    }
    return strcmp(fmt, "q") == 0 || strcmp(fmt, "l") == 0;
}

/*
 * fastmath.sum_squares_buffer(arr): arr is anything that exposes a raw,
 * contiguous block of int64 values through Python's buffer protocol,
 * such as a NumPy int64 array or array.array('q').
 * This is the fast path: one tight C loop over raw integers.
 */
static PyObject *fastmath_sum_squares_buffer(PyObject *self, PyObject *args) {
    (void) self; /* the module object; these functions do not need it */
    PyObject *obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }

    Py_buffer view;
    if (PyObject_GetBuffer(obj, &view, PyBUF_C_CONTIGUOUS | PyBUF_FORMAT) != 0) {
        return NULL;
    }
    if (!is_int64_format(view.format, view.itemsize)) {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_TypeError, "expected a contiguous buffer of int64");
        return NULL;
    }

    const int64_t *values = (const int64_t *) view.buf;
    Py_ssize_t n = view.len / view.itemsize;
    int64_t total = 0;
    for (Py_ssize_t i = 0; i < n; i++) {
        total += values[i] * values[i];
    }

    PyBuffer_Release(&view);
    return PyLong_FromLongLong(total);
}

/*
 * fastmath.sum_squares_list(lst): the same math, but over a Python list.
 * A list does not hold integers. It holds pointers to separate int
 * objects on the heap, so every element costs a pointer chase plus an
 * "unbox" step. This is still C, yet it is much slower than the buffer
 * version above.
 */
static PyObject *fastmath_sum_squares_list(PyObject *self, PyObject *args) {
    (void) self; /* the module object; these functions do not need it */
    PyObject *list;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &list)) {
        return NULL;
    }

    Py_ssize_t n = PyList_GET_SIZE(list);
    int64_t total = 0;
    for (Py_ssize_t i = 0; i < n; i++) {
        PyObject *item = PyList_GET_ITEM(list, i); /* a pointer to a boxed int */
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "list must contain only ints");
            return NULL;
        }
        long long x = PyLong_AsLongLong(item); /* follow the pointer, unbox */
        if (x == -1 && PyErr_Occurred()) {
            return NULL; /* the int did not fit in 64 bits */
        }
        total += x * x;
    }
    return PyLong_FromLongLong(total);
}

static PyMethodDef fastmath_methods[] = {
    {"add", fastmath_add, METH_VARARGS, "add(a, b) -> a + b, computed in C."},
    {"sum_squares_buffer", fastmath_sum_squares_buffer, METH_VARARGS,
     "Sum of squares over a contiguous int64 buffer (NumPy array, array.array)."},
    {"sum_squares_list", fastmath_sum_squares_list, METH_VARARGS,
     "Sum of squares over a Python list of ints, walked from C."},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef fastmath_module = {
    PyModuleDef_HEAD_INIT,
    "fastmath",
    "A tiny C extension module: the same mechanism NumPy is built on.",
    -1,
    fastmath_methods,
    NULL, /* m_slots */
    NULL, /* m_traverse */
    NULL, /* m_clear */
    NULL  /* m_free */
};

/* Python calls this when it runs `import fastmath`. */
PyMODINIT_FUNC PyInit_fastmath(void) {
    return PyModule_Create(&fastmath_module);
}
