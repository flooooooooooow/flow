/* Auto-generated Python bindings for overloads */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyObject* py_twice(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = twice_i32(x);
    return PyLong_FromLong(result);
}


static PyObject* py_twice(PyObject* self, PyObject* args) {
    double x;
    
    if (!PyArg_ParseTuple(args, "d", &x)) {
        return NULL;
    }
    
    double result = twice_f64(x);
    return PyFloat_FromDouble(result);
}


static PyMethodDef overloads_methods[] = {
    {"twice", py_twice, METH_VARARGS, "twice function"},
    {"twice", py_twice, METH_VARARGS, "twice function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef overloads_module = {
    PyModuleDef_HEAD_INIT,
    "overloads",
    "Flow-generated module: overloads",
    -1,
    overloads_methods
};

PyMODINIT_FUNC PyInit_overloads(void) {
    return PyModule_Create(&overloads_module);
}
