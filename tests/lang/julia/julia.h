// Stub julia.h for CI syntax checking.
// The real header is only available where Julia is installed.
#pragma once
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void jl_init(void);
void* jl_eval_string(const char*);
void jl_atexit_hook(int);

#ifdef __cplusplus
}
#endif
