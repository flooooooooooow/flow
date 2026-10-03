/* Auto-generated Python bindings for imports */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyObject* py_helper_twice(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = helper_twice(x);
    return PyLong_FromLong(result);
}


static PyObject* py_helper_private(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = helper_private(x);
    return PyLong_FromLong(result);
}


static PyObject* py_wrapping_add_i32(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = wrapping_add_i32(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_wrapping_sub_i32(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = wrapping_sub_i32(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_wrapping_mul_i32(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = wrapping_mul_i32(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_saturating_add_i32(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = saturating_add_i32(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_saturating_sub_i32(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = saturating_sub_i32(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_saturating_mul_i32(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = saturating_mul_i32(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_wrapping_add_i64(PyObject* self, PyObject* args) {
    int64_t a;
    int64_t b;
    
    if (!PyArg_ParseTuple(args, "LL", &a, &b)) {
        return NULL;
    }
    
    int64_t result = wrapping_add_i64(a, b);
    return PyLong_FromLongLong(result);
}


static PyObject* py_saturating_add_i64(PyObject* self, PyObject* args) {
    int64_t a;
    int64_t b;
    
    if (!PyArg_ParseTuple(args, "LL", &a, &b)) {
        return NULL;
    }
    
    int64_t result = saturating_add_i64(a, b);
    return PyLong_FromLongLong(result);
}


static PyObject* py_use_helper(PyObject* self, PyObject* args) {
    int32_t x;
    
    if (!PyArg_ParseTuple(args, "i", &x)) {
        return NULL;
    }
    
    int32_t result = use_helper(x);
    return PyLong_FromLong(result);
}


static PyMethodDef imports_methods[] = {
    {"helper_twice", py_helper_twice, METH_VARARGS, "helper_twice function"},
    {"helper_private", py_helper_private, METH_VARARGS, "helper_private function"},
    {"wrapping_add_i32", py_wrapping_add_i32, METH_VARARGS, "wrapping_add_i32 function"},
    {"wrapping_sub_i32", py_wrapping_sub_i32, METH_VARARGS, "wrapping_sub_i32 function"},
    {"wrapping_mul_i32", py_wrapping_mul_i32, METH_VARARGS, "wrapping_mul_i32 function"},
    {"saturating_add_i32", py_saturating_add_i32, METH_VARARGS, "saturating_add_i32 function"},
    {"saturating_sub_i32", py_saturating_sub_i32, METH_VARARGS, "saturating_sub_i32 function"},
    {"saturating_mul_i32", py_saturating_mul_i32, METH_VARARGS, "saturating_mul_i32 function"},
    {"wrapping_add_i64", py_wrapping_add_i64, METH_VARARGS, "wrapping_add_i64 function"},
    {"saturating_add_i64", py_saturating_add_i64, METH_VARARGS, "saturating_add_i64 function"},
    {"use_helper", py_use_helper, METH_VARARGS, "use_helper function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef imports_module = {
    PyModuleDef_HEAD_INIT,
    "imports",
    "Flow-generated module: imports",
    -1,
    imports_methods
};

PyMODINIT_FUNC PyInit_imports(void) {
    return PyModule_Create(&imports_module);
}
