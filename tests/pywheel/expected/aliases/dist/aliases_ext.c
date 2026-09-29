/* Auto-generated Python bindings for aliases */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyObject* py_scale(PyObject* self, PyObject* args) {
    PyObject* m_obj;
    
    if (!PyArg_ParseTuple(args, "O", &m_obj)) {
        return NULL;
    }
    
    scale(m);
    Py_RETURN_NONE;
}


static PyObject* py_plain(PyObject* self, PyObject* args) {
    double x;
    
    if (!PyArg_ParseTuple(args, "d", &x)) {
        return NULL;
    }
    
    double result = plain(x);
    return PyFloat_FromDouble(result);
}


static PyMethodDef aliases_methods[] = {
    {"scale", py_scale, METH_VARARGS, "scale function"},
    {"plain", py_plain, METH_VARARGS, "plain function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef aliases_module = {
    PyModuleDef_HEAD_INIT,
    "aliases",
    "Flow-generated module: aliases",
    -1,
    aliases_methods
};

PyMODINIT_FUNC PyInit_aliases(void) {
    return PyModule_Create(&aliases_module);
}
