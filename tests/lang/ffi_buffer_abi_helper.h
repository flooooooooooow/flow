/* C ABI helper for tests/lang/test_ffi_buffer.flow.
 * Includes the stable header so the structural test exercises the real
 * zero-copy helpers, not a second copy of the rules.
 */
#pragma once
#include "../../runtime/flow_ffi_buffer.h"

static inline int64_t flow_ffi_test_borrow_addr(
    void *data,
    int64_t len,
    int64_t item_size,
    int32_t item_align
) {
    FlowFfiLayout have;
    FlowFfiLayout want;
    FlowFfiBuffer buf;
    int32_t st;

    have.item_size = item_size;
    have.stride = item_size;
    have.item_align = item_align;
    have.reserved = 0;
    want = have;
    st = flow_ffi_buffer_try_borrow(&buf, data, len, &have, &want);
    if (st != FLOW_FFI_OK) {
        return 0;
    }
    return (int64_t)(uintptr_t)buf.data;
}

static inline int32_t flow_ffi_test_borrow_status(
    void *data,
    int64_t len,
    int64_t have_size,
    int64_t have_stride,
    int32_t have_align,
    int64_t want_size,
    int64_t want_stride,
    int32_t want_align
) {
    FlowFfiLayout have;
    FlowFfiLayout want;
    FlowFfiBuffer buf;

    have.item_size = have_size;
    have.stride = have_stride;
    have.item_align = have_align;
    have.reserved = 0;
    want.item_size = want_size;
    want.stride = want_stride;
    want.item_align = want_align;
    want.reserved = 0;
    return flow_ffi_buffer_try_borrow(&buf, data, len, &have, &want);
}
