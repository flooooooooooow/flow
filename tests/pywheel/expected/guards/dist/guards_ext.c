/* Auto-generated Python bindings for guards */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyObject* py_pick_i32(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = pick_i32(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_pick_i64(PyObject* self, PyObject* args) {
    int64_t a;
    int64_t b;
    
    if (!PyArg_ParseTuple(args, "LL", &a, &b)) {
        return NULL;
    }
    
    int64_t result = pick_i64(a, b);
    return PyLong_FromLongLong(result);
}


static PyObject* py_pick_f64(PyObject* self, PyObject* args) {
    double a;
    double b;
    
    if (!PyArg_ParseTuple(args, "dd", &a, &b)) {
        return NULL;
    }
    
    double result = pick_f64(a, b);
    return PyFloat_FromDouble(result);
}


static PyObject* py_compiled_only(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = compiled_only(x);
    return PyLong_FromLong(result);
}


static PyObject* py_plus(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = add(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_single_quoted(PyObject* self, PyObject* args) {
    double x;
    
    if (!PyArg_ParseTuple(args, "d", &x)) {
        return NULL;
    }
    
    double result = sq(x);
    return PyFloat_FromDouble(result);
}


static PyObject* py_use_generics(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = use_generics(x);
    return PyLong_FromLong(result);
}


static PyMethodDef guards_methods[] = {
    {"pick_i32", py_pick_i32, METH_VARARGS, "pick_i32 function"},
    {"pick_i64", py_pick_i64, METH_VARARGS, "pick_i64 function"},
    {"pick_f64", py_pick_f64, METH_VARARGS, "pick_f64 function"},
    {"compiled_only", py_compiled_only, METH_VARARGS, "compiled_only function"},
    {"plus", py_plus, METH_VARARGS, "Adds a"},
    {"single_quoted", py_single_quoted, METH_VARARGS, "sq function"},
    {"use_generics", py_use_generics, METH_VARARGS, "use_generics function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef guards_module = {
    PyModuleDef_HEAD_INIT,
    "guards",
    "Flow-generated module: guards",
    -1,
    guards_methods
};

PyMODINIT_FUNC PyInit_guards(void) {
    return PyModule_Create(&guards_module);
}
