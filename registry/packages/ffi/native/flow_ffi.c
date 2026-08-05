#include "flow_ffi.h"

#include <stddef.h>

int64_t flow_ffi_sizeof_ptr(void) {
    return (int64_t)sizeof(void *);
}
