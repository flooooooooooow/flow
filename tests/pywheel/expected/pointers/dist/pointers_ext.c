/* Auto-generated Python bindings for pointers */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */


/* ===== Flow compiled code ===== */
@FLOWC_C@


/* ===== Python wrappers ===== */

static PyMethodDef pointers_methods[] = {

    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef pointers_module = {
    PyModuleDef_HEAD_INIT,
    "pointers",
    "Flow-generated module: pointers",
    -1,
    pointers_methods
};

PyMODINIT_FUNC PyInit_pointers(void) {
    return PyModule_Create(&pointers_module);
}
