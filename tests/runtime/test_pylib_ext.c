/* Auto-generated Python bindings for test_pylib */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>


int32_t add_i32_i32(int32_t a, int32_t b);
double multiply_f64_f64(double x, double y);
int32_t square_i32(int32_t n);
void _internal(void);
int32_t main(void);

int32_t add_i32_i32(int32_t a, int32_t b) {
    return (a + b);
}

double multiply_f64_f64(double x, double y) {
    return (x * y);
}

int32_t square_i32(int32_t n) {
    return (n * n);
}

void _internal(void) {
    return;
}

int32_t main(void) {
    int32_t result = add_i32_i32(2, 3);
    return result;
}


/* ===== Python wrappers ===== */

static PyObject* py_add(PyObject* self, PyObject* args) {
    int32_t a;
    int32_t b;
    
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    
    int32_t result = add_i32_i32(a, b);
    return PyLong_FromLong(result);
}


static PyObject* py_multiply(PyObject* self, PyObject* args) {
    double x;
    double y;
    
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) {
        return NULL;
    }
    
    double result = multiply_f64_f64(x, y);
    return PyFloat_FromDouble(result);
}


static PyObject* py_square(PyObject* self, PyObject* args) {
    int32_t n;
    
    if (!PyArg_ParseTuple(args, "i", &n)) {
        return NULL;
    }
    
    int32_t result = square_i32(n);
    return PyLong_FromLong(result);
}


static PyMethodDef test_pylib_methods[] = {
    {"add", py_add, METH_VARARGS, "add function"},
    {"multiply", py_multiply, METH_VARARGS, "multiply function"},
    {"square", py_square, METH_VARARGS, "square function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef test_pylib_module = {
    PyModuleDef_HEAD_INIT,
    "test_pylib",
    "Flow-generated module: test_pylib",
    -1,
    test_pylib_methods
};

PyMODINIT_FUNC PyInit_test_pylib(void) {
    return PyModule_Create(&test_pylib_module);
}
