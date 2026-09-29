/* Auto-generated Python bindings for private_structs */
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
    
    int32_t result = twice(x);
    return PyLong_FromLong(result);
}


static PyObject* py_square(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = square(x);
    return PyLong_FromLong(result);
}


static PyObject* py_forked(PyObject* self, PyObject* args) {
    int32_t n;
    
    if (!PyArg_ParseTuple(args, "i", &n)) {
        return NULL;
    }
    
    int32_t result = forked(n);
    return PyLong_FromLong(result);
}


/* Struct Marker is exposed as a dictionary */


static PyMethodDef private_structs_methods[] = {
    {"twice", py_twice, METH_VARARGS, "twice function"},
    {"square", py_square, METH_VARARGS, "square function"},
    {"forked", py_forked, METH_VARARGS, "forked function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef private_structs_module = {
    PyModuleDef_HEAD_INIT,
    "private_structs",
    "Flow-generated module: private_structs",
    -1,
    private_structs_methods
};

PyMODINIT_FUNC PyInit_private_structs(void) {
    return PyModule_Create(&private_structs_module);
}
