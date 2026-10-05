#ifndef FLOW_FFI_BUFFER_H
#define FLOW_FFI_BUFFER_H

/*
 * Stable zero-copy FFI buffer ABI (issue #737, version 1).
 *
 * A supported handoff is a pointer plus a compatible contiguous layout.
 * Compatible sources are a raw pointer+length, a Flow span, or a contiguous
 * array. The view stores the caller's pointer; it never copies payload bytes.
 *
 * Ownership:
 *   FLOW_FFI_OWN_BORROWED — sender keeps the storage. The receiver must not
 *     free it or retain it after the call returns.
 *   FLOW_FFI_OWN_OWNED — receiver frees `data` through `dealloc` (or
 *     `dealloc_ctx` if the callback needs a context).
 *
 * Incompatible layout (wrong item size, non-unit stride, or under-aligned
 * pointer) returns a nonzero status and a zeroed buffer. The helpers never
 * fall back to an O(n) copy. An explicit copy is a separate, named call.
 *
 * Layout matches Flow `FFIBuffer` / `FFILayout` in
 * registry/packages/ffi/src/buffer_handoff.flow.
 * Contract: docs/language/ffi-buffer.md
 */

#include <stddef.h>
#include <stdint.h>

#define FLOW_FFI_BUFFER_ABI_VERSION 1

#define FLOW_FFI_OWN_BORROWED 0
#define FLOW_FFI_OWN_OWNED 1

#define FLOW_FFI_OK 0
#define FLOW_FFI_ERR_NULL 1
#define FLOW_FFI_ERR_BAD_LEN 2
#define FLOW_FFI_ERR_BAD_SIZE 3
#define FLOW_FFI_ERR_BAD_ALIGN 4
#define FLOW_FFI_ERR_STRIDE 5
#define FLOW_FFI_ERR_INCOMPATIBLE 6

typedef struct FlowFfiLayout {
    int64_t item_size;
    int64_t stride;
    int32_t item_align;
    int32_t reserved;
} FlowFfiLayout;

typedef struct FlowFfiBuffer {
    void *data;
    int64_t len;
    int64_t item_size;
    int32_t item_align;
    int32_t ownership;
    void *dealloc;
    void *dealloc_ctx;
} FlowFfiBuffer;

static inline int32_t flow_ffi_align_ok(int32_t align) {
    if (align <= 1) {
        return 1;
    }
    return (align & (align - 1)) == 0 ? 1 : 0;
}

static inline int32_t flow_ffi_ptr_aligned(const void *data, int32_t align) {
    if (align <= 1) {
        return 1;
    }
    return (((uintptr_t)data) & (uintptr_t)(align - 1)) == 0 ? 1 : 0;
}

static inline void flow_ffi_buffer_clear(FlowFfiBuffer *out) {
    if (out == NULL) {
        return;
    }
    out->data = NULL;
    out->len = 0;
    out->item_size = 0;
    out->item_align = 0;
    out->ownership = FLOW_FFI_OWN_BORROWED;
    out->dealloc = NULL;
    out->dealloc_ctx = NULL;
}

/* Check only. Never copies. */
static inline int32_t flow_ffi_layout_compatible(
    const void *data,
    int64_t len,
    const FlowFfiLayout *have,
    const FlowFfiLayout *want
) {
    if (have == NULL || want == NULL) {
        return FLOW_FFI_ERR_NULL;
    }
    if (len < 0) {
        return FLOW_FFI_ERR_BAD_LEN;
    }
    if (want->item_size <= 0 || have->item_size <= 0) {
        return FLOW_FFI_ERR_BAD_SIZE;
    }
    if (flow_ffi_align_ok(want->item_align) == 0 || flow_ffi_align_ok(have->item_align) == 0) {
        return FLOW_FFI_ERR_BAD_ALIGN;
    }
    if (want->stride != want->item_size || have->stride != have->item_size) {
        return FLOW_FFI_ERR_STRIDE;
    }
    if (have->item_size != want->item_size) {
        return FLOW_FFI_ERR_INCOMPATIBLE;
    }
    if (len > 0 && data == NULL) {
        return FLOW_FFI_ERR_NULL;
    }
    if (len > 0 && flow_ffi_ptr_aligned(data, want->item_align) == 0) {
        return FLOW_FFI_ERR_BAD_ALIGN;
    }
    return FLOW_FFI_OK;
}

static inline int32_t flow_ffi_buffer_try_borrow(
    FlowFfiBuffer *out,
    void *data,
    int64_t len,
    const FlowFfiLayout *have,
    const FlowFfiLayout *want
) {
    int32_t st;

    if (out == NULL) {
        return FLOW_FFI_ERR_NULL;
    }
    st = flow_ffi_layout_compatible(data, len, have, want);
    if (st != FLOW_FFI_OK) {
        flow_ffi_buffer_clear(out);
        return st;
    }
    out->data = data;
    out->len = len;
    out->item_size = want->item_size;
    out->item_align = want->item_align;
    out->ownership = FLOW_FFI_OWN_BORROWED;
    out->dealloc = NULL;
    out->dealloc_ctx = NULL;
    return FLOW_FFI_OK;
}

static inline int32_t flow_ffi_buffer_try_own(
    FlowFfiBuffer *out,
    void *data,
    int64_t len,
    const FlowFfiLayout *have,
    const FlowFfiLayout *want,
    void *dealloc,
    void *dealloc_ctx
) {
    int32_t st;

    if (out == NULL) {
        return FLOW_FFI_ERR_NULL;
    }
    st = flow_ffi_layout_compatible(data, len, have, want);
    if (st != FLOW_FFI_OK) {
        flow_ffi_buffer_clear(out);
        return st;
    }
    out->data = data;
    out->len = len;
    out->item_size = want->item_size;
    out->item_align = want->item_align;
    out->ownership = FLOW_FFI_OWN_OWNED;
    out->dealloc = dealloc;
    out->dealloc_ctx = dealloc_ctx;
    return FLOW_FFI_OK;
}

#endif /* FLOW_FFI_BUFFER_H */
