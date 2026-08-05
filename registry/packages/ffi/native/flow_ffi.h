#ifndef FLOW_FFI_H
#define FLOW_FFI_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Bindgen seed: pointer width on this platform (no dlopen). */
int64_t flow_ffi_sizeof_ptr(void);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_FFI_H */
