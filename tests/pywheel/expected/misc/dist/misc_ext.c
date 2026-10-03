/* Auto-generated Python bindings for misc */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyObject* py_identity_i32(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = identity_i32(x);
    return PyLong_FromLong(result);
}


static PyObject* py_abs(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = abs(x);
    return PyLong_FromLong(result);
}


static PyObject* py_exported_abs(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = exported_abs(x);
    return PyLong_FromLong(result);
}


static PyObject* py_inlined(PyObject* self, PyObject* args) {
    int64_t x;
    
    if (!PyArg_ParseTuple(args, "L", &x)) {
        return NULL;
    }
    
    int64_t result = inlined(x);
    return PyLong_FromLongLong(result);
}


static PyMethodDef misc_methods[] = {
    {"identity_i32", py_identity_i32, METH_VARARGS, "identity_i32 function"},
    {"abs", py_abs, METH_VARARGS, "abs function"},
    {"exported_abs", py_exported_abs, METH_VARARGS, "exported_abs function"},
    {"inlined", py_inlined, METH_VARARGS, "inlined function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef misc_module = {
    PyModuleDef_HEAD_INIT,
    "misc",
    "Flow-generated module: misc",
    -1,
    misc_methods
};

PyMODINIT_FUNC PyInit_misc(void) {
    return PyModule_Create(&misc_module);
}
