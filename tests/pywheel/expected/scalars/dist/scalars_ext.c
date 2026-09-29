/* Auto-generated Python bindings for scalars */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyObject* py_add_i64(PyObject* self, PyObject* args) {
    int64_t a;
    int64_t b;
    
    if (!PyArg_ParseTuple(args, "LL", &a, &b)) {
        return NULL;
    }
    
    int64_t result = add_i64(a, b);
    return PyLong_FromLongLong(result);
}


static PyObject* py_add_u32(PyObject* self, PyObject* args) {
    uint32_t a;
    uint32_t b;
    
    if (!PyArg_ParseTuple(args, "II", &a, &b)) {
        return NULL;
    }
    
    uint32_t result = add_u32(a, b);
    return PyLong_FromUnsignedLong(result);
}


static PyObject* py_add_u64(PyObject* self, PyObject* args) {
    uint64_t a;
    uint64_t b;
    
    if (!PyArg_ParseTuple(args, "KK", &a, &b)) {
        return NULL;
    }
    
    uint64_t result = add_u64(a, b);
    return PyLong_FromUnsignedLongLong(result);
}


static PyObject* py_half(PyObject* self, PyObject* args) {
    float x;
    
    if (!PyArg_ParseTuple(args, "f", &x)) {
        return NULL;
    }
    
    float result = half(x);
    return PyFloat_FromDouble((double)result);
}


static PyObject* py_negate(PyObject* self, PyObject* args) {
    int b;
    
    if (!PyArg_ParseTuple(args, "p", &b)) {
        return NULL;
    }
    
    int result = negate(b);
    return PyBool_FromLong(result);
}


static PyObject* py_greet(PyObject* self, PyObject* args) {
    const char* name;
    
    if (!PyArg_ParseTuple(args, "s", &name)) {
        return NULL;
    }
    
    const char* result = greet(name);
    return PyUnicode_FromString(result);
}


static PyObject* py_mixed(PyObject* self, PyObject* args) {
    int32_t a;
    double b;
    int c;
    const char* d;
    
    if (!PyArg_ParseTuple(args, "idps", &a, &b, &c, &d)) {
        return NULL;
    }
    
    double result = mixed(a, b, c, d);
    return PyFloat_FromDouble(result);
}


static PyObject* py_nothing(PyObject* self, PyObject* args) {

    
    if (!PyArg_ParseTuple(args, "", )) {
        return NULL;
    }
    
    nothing();
    Py_RETURN_NONE;
}


static PyMethodDef scalars_methods[] = {
    {"add_i64", py_add_i64, METH_VARARGS, "add_i64 function"},
    {"add_u32", py_add_u32, METH_VARARGS, "add_u32 function"},
    {"add_u64", py_add_u64, METH_VARARGS, "add_u64 function"},
    {"half", py_half, METH_VARARGS, "half function"},
    {"negate", py_negate, METH_VARARGS, "negate function"},
    {"greet", py_greet, METH_VARARGS, "greet function"},
    {"mixed", py_mixed, METH_VARARGS, "mixed function"},
    {"nothing", py_nothing, METH_VARARGS, "nothing function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef scalars_module = {
    PyModuleDef_HEAD_INIT,
    "scalars",
    "Flow-generated module: scalars",
    -1,
    scalars_methods
};

PyMODINIT_FUNC PyInit_scalars(void) {
    return PyModule_Create(&scalars_module);
}
