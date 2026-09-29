/* Auto-generated Python bindings for overrides */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyObject* py_py_func_name(PyObject* self, PyObject* args) {

    
    if (!PyArg_ParseTuple(args, "", )) {
        return NULL;
    }
    
    flow_func_name();
    Py_RETURN_NONE;
}


static PyObject* py_sqrt_like(PyObject* self, PyObject* args) {
    double x;
    
    if (!PyArg_ParseTuple(args, "d", &x)) {
        return NULL;
    }
    
    double result = sqrt_like(x);
    return PyFloat_FromDouble(result);
}


static PyObject* py_plain_func(PyObject* self, PyObject* args) {

    
    if (!PyArg_ParseTuple(args, "", )) {
        return NULL;
    }
    
    plain_func();
    Py_RETURN_NONE;
}


static PyMethodDef overrides_methods[] = {
    {"py_func_name", py_py_func_name, METH_VARARGS, "flow_func_name function"},
    {"sqrt_like", py_sqrt_like, METH_VARARGS, "Computes the square root"},
    {"plain_func", py_plain_func, METH_VARARGS, "plain_func function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef overrides_module = {
    PyModuleDef_HEAD_INIT,
    "overrides",
    "Flow-generated module: overrides",
    -1,
    overrides_methods
};

PyMODINIT_FUNC PyInit_overrides(void) {
    return PyModule_Create(&overrides_module);
}
