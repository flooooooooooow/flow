/* Auto-generated Python bindings for mathlib */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyObject* py_square(PyObject* self, PyObject* args) {
    double x;
    
    if (!PyArg_ParseTuple(args, "d", &x)) {
        return NULL;
    }
    
    double result = square(x);
    return PyFloat_FromDouble(result);
}


static PyObject* py_factorial(PyObject* self, PyObject* args) {
    int32_t n;
    
    if (!PyArg_ParseTuple(args, "i", &n)) {
        return NULL;
    }
    
    int32_t result = factorial(n);
    return PyLong_FromLong(result);
}


static PyMethodDef mathlib_methods[] = {
    {"square", py_square, METH_VARARGS, "square function"},
    {"factorial", py_factorial, METH_VARARGS, "factorial function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef mathlib_module = {
    PyModuleDef_HEAD_INIT,
    "mathlib",
    "Flow-generated module: mathlib",
    -1,
    mathlib_methods
};

PyMODINIT_FUNC PyInit_mathlib(void) {
    return PyModule_Create(&mathlib_module);
}
