// Stub Python.h for CI syntax checking.
// The real header is only available where CPython dev is installed.
#pragma once
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void Py_Initialize(void);
int PyRun_SimpleString(char*);
void Py_Finalize(void);

#ifdef __cplusplus
}
#endif
