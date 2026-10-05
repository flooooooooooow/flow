#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <dlfcn.h>

#ifdef FLOW_PY_EMBED
#include <Python.h>
#endif

#ifndef FLOW_PY_EMBED
typedef void PyObject;
#endif

typedef void (*Py_Initialize_Fn)(void);
typedef int (*Py_FinalizeEx_Fn)(void);
typedef int (*PyRun_SimpleStringFlags_Fn)(const char*, void*);
typedef PyObject* (*PyUnicode_FromString_Fn)(const char*);
typedef PyObject* (*PyImport_Import_Fn)(PyObject*);
typedef PyObject* (*PyObject_GetAttrString_Fn)(PyObject*, const char*);
typedef PyObject* (*PyObject_CallNoArgs_Fn)(PyObject*);
typedef PyObject* (*PyObject_CallFunctionObjArgs_Fn)(PyObject*, ...);
typedef int (*PyList_Append_Fn)(PyObject*, PyObject*);
typedef PyObject* (*PySys_GetObject_Fn)(const char*);
typedef void (*PyErr_Print_Fn)(void);
typedef void (*Py_DecRef_Fn)(PyObject*);
typedef PyObject* (*PyLong_FromLong_Fn)(long);
typedef PyObject* (*PyFloat_FromDouble_Fn)(double);
typedef PyObject* (*PyBool_FromLong_Fn)(long);
typedef double (*PyFloat_AsDouble_Fn)(PyObject*);
typedef void* (*PyGILState_Ensure_Fn)(void);
typedef void (*PyGILState_Release_Fn)(void*);

static void* g_py_lib = NULL;
static int g_py_initialized = 0;
static char g_py_last_error[512];

static Py_Initialize_Fn p_Py_Initialize = NULL;
static Py_FinalizeEx_Fn p_Py_FinalizeEx = NULL;
static PyRun_SimpleStringFlags_Fn p_PyRun_SimpleStringFlags = NULL;
static PyUnicode_FromString_Fn p_PyUnicode_FromString = NULL;
static PyImport_Import_Fn p_PyImport_Import = NULL;
static PyObject_GetAttrString_Fn p_PyObject_GetAttrString = NULL;
static PyObject_CallNoArgs_Fn p_PyObject_CallNoArgs = NULL;
static PyObject_CallFunctionObjArgs_Fn p_PyObject_CallFunctionObjArgs = NULL;
static PyList_Append_Fn p_PyList_Append = NULL;
static PySys_GetObject_Fn p_PySys_GetObject = NULL;
static PyErr_Print_Fn p_PyErr_Print = NULL;
static Py_DecRef_Fn p_Py_DecRef = NULL;
static PyLong_FromLong_Fn p_PyLong_FromLong = NULL;
static PyFloat_FromDouble_Fn p_PyFloat_FromDouble = NULL;
static PyBool_FromLong_Fn p_PyBool_FromLong = NULL;
static PyFloat_AsDouble_Fn p_PyFloat_AsDouble = NULL;
static PyGILState_Ensure_Fn p_PyGILState_Ensure = NULL;
static PyGILState_Release_Fn p_PyGILState_Release = NULL;

static int flow_py_load_symbol(void** slot, const char* name) {
    dlerror();
    *slot = dlsym(g_py_lib, name);
    const char* err = dlerror();
    if (err) {
        strncpy(g_py_last_error, err, sizeof(g_py_last_error) - 1);
        g_py_last_error[sizeof(g_py_last_error) - 1] = '\0';
        return 1;
    }
    return 0;
}

static int flow_py_load() {
    if (g_py_lib) return 0;
    g_py_last_error[0] = '\0';

    const char* override = getenv("FLOW_PYTHON_LIB");
    const char* candidates[] = {
        override,
        "libpython3.13.dylib",
        "libpython3.12.dylib",
        "libpython3.11.dylib",
        "libpython3.10.dylib",
        "libpython3.9.dylib",
        "Python3",
        "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Python3",
        "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Python3",
        "/Library/Frameworks/Python.framework/Python",
        "/System/Library/Frameworks/Python.framework/Python",
        NULL
    };

    for (int i = 0; candidates[i]; i++) {
        if (!candidates[i] || !candidates[i][0]) continue;
        g_py_lib = dlopen(candidates[i], RTLD_NOW | RTLD_GLOBAL);
        if (g_py_lib) break;
    }
    if (!g_py_lib) return 1;

    if (flow_py_load_symbol((void**)&p_Py_Initialize, "Py_Initialize")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_Py_FinalizeEx, "Py_FinalizeEx")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyRun_SimpleStringFlags, "PyRun_SimpleStringFlags")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyUnicode_FromString, "PyUnicode_FromString")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyImport_Import, "PyImport_Import")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyObject_GetAttrString, "PyObject_GetAttrString")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyObject_CallNoArgs, "PyObject_CallNoArgs")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyObject_CallFunctionObjArgs, "PyObject_CallFunctionObjArgs")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyList_Append, "PyList_Append")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PySys_GetObject, "PySys_GetObject")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyErr_Print, "PyErr_Print")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_Py_DecRef, "Py_DecRef")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyLong_FromLong, "PyLong_FromLong")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyFloat_FromDouble, "PyFloat_FromDouble")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyBool_FromLong, "PyBool_FromLong")) goto sym_fail;
    if (flow_py_load_symbol((void**)&p_PyFloat_AsDouble, "PyFloat_AsDouble")) goto sym_fail;
    flow_py_load_symbol((void**)&p_PyGILState_Ensure, "PyGILState_Ensure");
    flow_py_load_symbol((void**)&p_PyGILState_Release, "PyGILState_Release");

    if (!p_Py_Initialize || !p_Py_FinalizeEx || !p_PyRun_SimpleStringFlags ||
        !p_PyUnicode_FromString || !p_PyImport_Import || !p_PyObject_GetAttrString ||
        !p_PyObject_CallNoArgs || !p_PyObject_CallFunctionObjArgs || !p_PyList_Append || !p_PySys_GetObject ||
        !p_PyErr_Print || !p_Py_DecRef || !p_PyLong_FromLong || !p_PyFloat_FromDouble || !p_PyBool_FromLong || !p_PyFloat_AsDouble) {
        strncpy(g_py_last_error, "Missing Python symbols", sizeof(g_py_last_error) - 1);
        g_py_last_error[sizeof(g_py_last_error) - 1] = '\0';
        dlclose(g_py_lib);
        g_py_lib = NULL;
        return 2;
    }
    return 0;

sym_fail:
    if (g_py_last_error[0] == '\0') {
        strncpy(g_py_last_error, "Missing Python symbols", sizeof(g_py_last_error) - 1);
        g_py_last_error[sizeof(g_py_last_error) - 1] = '\0';
    }
    dlclose(g_py_lib);
    g_py_lib = NULL;
    return 2;
}

static void* flow_py_gil_enter() {
    if (p_PyGILState_Ensure) {
        return p_PyGILState_Ensure();
    }
    return NULL;
}

static void flow_py_gil_leave(void* state) {
    if (p_PyGILState_Release && state) {
        p_PyGILState_Release(state);
    }
}

int32_t python_init() {
    if (g_py_initialized) return 0;
#ifdef FLOW_PY_EMBED
    Py_Initialize();
    g_py_initialized = 1;
    return 0;
#else
    if (flow_py_load() != 0) {
        const char* err = dlerror();
        if (err) {
            strncpy(g_py_last_error, err, sizeof(g_py_last_error) - 1);
            g_py_last_error[sizeof(g_py_last_error) - 1] = '\0';
        } else {
            strncpy(g_py_last_error, "Unable to load Python library", sizeof(g_py_last_error) - 1);
            g_py_last_error[sizeof(g_py_last_error) - 1] = '\0';
        }
        return 1;
    }
    p_Py_Initialize();
    g_py_initialized = 1;
    return 0;
#endif
}

int32_t python_destroy() {
    if (!g_py_initialized) return 0;
#ifdef FLOW_PY_EMBED
    int rc = Py_FinalizeEx();
    g_py_initialized = 0;
    return rc == 0 ? 0 : 1;
#else
    int rc = p_Py_FinalizeEx ? p_Py_FinalizeEx() : 0;
    g_py_initialized = 0;
    return rc == 0 ? 0 : 1;
#endif
}

char* python_last_error() {
    if (g_py_last_error[0] == '\0') {
        return "no error";
    }
    return g_py_last_error;
}

void print_line(const char* msg) {
    if (!msg) msg = "";
    printf("%s\n", msg);
    fflush(stdout);
}

int32_t python_add_to_path(const char* path) {
    if (!g_py_initialized || !path || !path[0]) return 1;
#ifdef FLOW_PY_EMBED
    PyObject* sys_path = PySys_GetObject("path");
    if (!sys_path) return 2;
    PyObject* py_path = PyUnicode_FromString(path);
    if (!py_path) {
        PyErr_Print();
        return 3;
    }
    int rc = PyList_Append(sys_path, py_path);
    Py_DECREF(py_path);
    if (rc != 0) {
        PyErr_Print();
        return 4;
    }
    return 0;
#else
    void* gil = flow_py_gil_enter();
    PyObject* sys_path = p_PySys_GetObject("path");
    if (!sys_path) {
        flow_py_gil_leave(gil);
        return 2;
    }
    PyObject* py_path = p_PyUnicode_FromString(path);
    if (!py_path) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 3;
    }
    int rc = p_PyList_Append(sys_path, py_path);
    p_Py_DecRef(py_path);
    if (rc != 0) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 4;
    }
    flow_py_gil_leave(gil);
    return 0;
#endif
}

void* python_import_module(const char* name) {
    if (!g_py_initialized || !name) return NULL;
#ifdef FLOW_PY_EMBED
    PyObject* py_name = PyUnicode_FromString(name);
    if (!py_name) {
        PyErr_Print();
        return NULL;
    }
    PyObject* module = PyImport_Import(py_name);
    Py_DECREF(py_name);
    if (!module) {
        PyErr_Print();
        return NULL;
    }
    return (void*)module;
#else
    void* gil = flow_py_gil_enter();
    PyObject* py_name = p_PyUnicode_FromString(name);
    if (!py_name) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return NULL;
    }
    PyObject* module = p_PyImport_Import(py_name);
    p_Py_DecRef(py_name);
    if (!module) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return NULL;
    }
    flow_py_gil_leave(gil);
    return (void*)module;
#endif
}

int32_t python_call0(void* module, const char* name) {
    if (!g_py_initialized || !module || !name) return 1;
#ifdef FLOW_PY_EMBED
    PyObject* mod = (PyObject*)module;
    PyObject* func = PyObject_GetAttrString(mod, name);
    if (!func) {
        PyErr_Print();
        return 2;
    }
    PyObject* result = PyObject_CallNoArgs(func);
    Py_DECREF(func);
    if (!result) {
        PyErr_Print();
        return 3;
    }
    Py_DECREF(result);
    return 0;
#else
    void* gil = flow_py_gil_enter();
    PyObject* mod = (PyObject*)module;
    PyObject* func = p_PyObject_GetAttrString(mod, name);
    if (!func) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 2;
    }
    PyObject* result = p_PyObject_CallNoArgs(func);
    p_Py_DecRef(func);
    if (!result) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 3;
    }
    p_Py_DecRef(result);
    flow_py_gil_leave(gil);
    return 0;
#endif
}

int32_t python_call1_str(void* module, const char* name, const char* arg) {
    if (!g_py_initialized || !module || !name) return 1;
#ifdef FLOW_PY_EMBED
    PyObject* mod = (PyObject*)module;
    PyObject* func = PyObject_GetAttrString(mod, name);
    if (!func) {
        PyErr_Print();
        return 2;
    }
    PyObject* py_arg = PyUnicode_FromString(arg ? arg : "");
    if (!py_arg) {
        PyErr_Print();
        Py_DECREF(func);
        return 3;
    }
    PyObject* result = PyObject_CallFunctionObjArgs(func, py_arg, NULL);
    Py_DECREF(py_arg);
    Py_DECREF(func);
    if (!result) {
        PyErr_Print();
        return 4;
    }
    Py_DECREF(result);
    return 0;
#else
    void* gil = flow_py_gil_enter();
    PyObject* mod = (PyObject*)module;
    PyObject* func = p_PyObject_GetAttrString(mod, name);
    if (!func) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 2;
    }
    PyObject* py_arg = p_PyUnicode_FromString(arg ? arg : "");
    if (!py_arg) {
        p_PyErr_Print();
        p_Py_DecRef(func);
        flow_py_gil_leave(gil);
        return 3;
    }
    PyObject* result = p_PyObject_CallFunctionObjArgs(func, py_arg, NULL);
    p_Py_DecRef(py_arg);
    p_Py_DecRef(func);
    if (!result) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 4;
    }
    p_Py_DecRef(result);
    flow_py_gil_leave(gil);
    return 0;
#endif
}

int32_t python_call1_i32(void* module, const char* name, int32_t arg) {
    if (!g_py_initialized || !module || !name) return 1;
#ifdef FLOW_PY_EMBED
    PyObject* mod = (PyObject*)module;
    PyObject* func = PyObject_GetAttrString(mod, name);
    if (!func) {
        PyErr_Print();
        return 2;
    }
    PyObject* py_arg = PyLong_FromLong((long)arg);
    if (!py_arg) {
        PyErr_Print();
        Py_DECREF(func);
        return 3;
    }
    PyObject* result = PyObject_CallFunctionObjArgs(func, py_arg, NULL);
    Py_DECREF(py_arg);
    Py_DECREF(func);
    if (!result) {
        PyErr_Print();
        return 4;
    }
    Py_DECREF(result);
    return 0;
#else
    void* gil = flow_py_gil_enter();
    PyObject* mod = (PyObject*)module;
    PyObject* func = p_PyObject_GetAttrString(mod, name);
    if (!func) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 2;
    }
    PyObject* py_arg = p_PyLong_FromLong((long)arg);
    if (!py_arg) {
        p_PyErr_Print();
        p_Py_DecRef(func);
        flow_py_gil_leave(gil);
        return 3;
    }
    PyObject* result = p_PyObject_CallFunctionObjArgs(func, py_arg, NULL);
    p_Py_DecRef(py_arg);
    p_Py_DecRef(func);
    if (!result) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 4;
    }
    p_Py_DecRef(result);
    flow_py_gil_leave(gil);
    return 0;
#endif
}

int32_t python_call1_f32(void* module, const char* name, float arg) {
    if (!g_py_initialized || !module || !name) return 1;
#ifdef FLOW_PY_EMBED
    PyObject* mod = (PyObject*)module;
    PyObject* func = PyObject_GetAttrString(mod, name);
    if (!func) {
        PyErr_Print();
        return 2;
    }
    PyObject* py_arg = PyFloat_FromDouble((double)arg);
    if (!py_arg) {
        PyErr_Print();
        Py_DECREF(func);
        return 3;
    }
    PyObject* result = PyObject_CallFunctionObjArgs(func, py_arg, NULL);
    Py_DECREF(py_arg);
    Py_DECREF(func);
    if (!result) {
        PyErr_Print();
        return 4;
    }
    Py_DECREF(result);
    return 0;
#else
    void* gil = flow_py_gil_enter();
    PyObject* mod = (PyObject*)module;
    PyObject* func = p_PyObject_GetAttrString(mod, name);
    if (!func) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 2;
    }
    PyObject* py_arg = p_PyFloat_FromDouble((double)arg);
    if (!py_arg) {
        p_PyErr_Print();
        p_Py_DecRef(func);
        flow_py_gil_leave(gil);
        return 3;
    }
    PyObject* result = p_PyObject_CallFunctionObjArgs(func, py_arg, NULL);
    p_Py_DecRef(py_arg);
    p_Py_DecRef(func);
    if (!result) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 4;
    }
    p_Py_DecRef(result);
    flow_py_gil_leave(gil);
    return 0;
#endif
}

int32_t python_call1_bool(void* module, const char* name, int32_t arg) {
    if (!g_py_initialized || !module || !name) return 1;
#ifdef FLOW_PY_EMBED
    PyObject* mod = (PyObject*)module;
    PyObject* func = PyObject_GetAttrString(mod, name);
    if (!func) {
        PyErr_Print();
        return 2;
    }
    PyObject* py_arg = PyBool_FromLong(arg ? 1 : 0);
    if (!py_arg) {
        PyErr_Print();
        Py_DECREF(func);
        return 3;
    }
    PyObject* result = PyObject_CallFunctionObjArgs(func, py_arg, NULL);
    Py_DECREF(py_arg);
    Py_DECREF(func);
    if (!result) {
        PyErr_Print();
        return 4;
    }
    Py_DECREF(result);
    return 0;
#else
    void* gil = flow_py_gil_enter();
    PyObject* mod = (PyObject*)module;
    PyObject* func = p_PyObject_GetAttrString(mod, name);
    if (!func) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 2;
    }
    PyObject* py_arg = p_PyBool_FromLong(arg ? 1 : 0);
    if (!py_arg) {
        p_PyErr_Print();
        p_Py_DecRef(func);
        flow_py_gil_leave(gil);
        return 3;
    }
    PyObject* result = p_PyObject_CallFunctionObjArgs(func, py_arg, NULL);
    p_Py_DecRef(py_arg);
    p_Py_DecRef(func);
    if (!result) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 4;
    }
    p_Py_DecRef(result);
    flow_py_gil_leave(gil);
    return 0;
#endif
}

double python_call3_i32_f64(void* module, const char* name, int32_t a, int32_t b, int32_t c) {
    if (!g_py_initialized || !module || !name) return 0.0;
#ifdef FLOW_PY_EMBED
    PyObject* mod = (PyObject*)module;
    PyObject* func = PyObject_GetAttrString(mod, name);
    if (!func) {
        PyErr_Print();
        return 0.0;
    }
    PyObject* a0 = PyLong_FromLong((long)a);
    PyObject* a1 = PyLong_FromLong((long)b);
    PyObject* a2 = PyLong_FromLong((long)c);
    if (!a0 || !a1 || !a2) {
        PyErr_Print();
        Py_XDECREF(a0);
        Py_XDECREF(a1);
        Py_XDECREF(a2);
        Py_DECREF(func);
        return 0.0;
    }
    PyObject* result = PyObject_CallFunctionObjArgs(func, a0, a1, a2, NULL);
    Py_DECREF(a0);
    Py_DECREF(a1);
    Py_DECREF(a2);
    Py_DECREF(func);
    if (!result) {
        PyErr_Print();
        return 0.0;
    }
    double out = PyFloat_AsDouble(result);
    Py_DECREF(result);
    return out;
#else
    void* gil = flow_py_gil_enter();
    PyObject* mod = (PyObject*)module;
    PyObject* func = p_PyObject_GetAttrString(mod, name);
    if (!func) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 0.0;
    }
    PyObject* a0 = p_PyLong_FromLong((long)a);
    PyObject* a1 = p_PyLong_FromLong((long)b);
    PyObject* a2 = p_PyLong_FromLong((long)c);
    if (!a0 || !a1 || !a2) {
        p_PyErr_Print();
        if (a0) p_Py_DecRef(a0);
        if (a1) p_Py_DecRef(a1);
        if (a2) p_Py_DecRef(a2);
        p_Py_DecRef(func);
        flow_py_gil_leave(gil);
        return 0.0;
    }
    PyObject* result = p_PyObject_CallFunctionObjArgs(func, a0, a1, a2, NULL);
    p_Py_DecRef(a0);
    p_Py_DecRef(a1);
    p_Py_DecRef(a2);
    p_Py_DecRef(func);
    if (!result) {
        p_PyErr_Print();
        flow_py_gil_leave(gil);
        return 0.0;
    }
    double out = p_PyFloat_AsDouble(result);
    p_Py_DecRef(result);
    flow_py_gil_leave(gil);
    return out;
#endif
}
