# FFI Package

The FFI package provides little-endian buffer packing helpers and the Flow
side of the zero-copy buffer ABI (`ffi_buffer_handoff`).

The stable C contract is [`runtime/flow_ffi_buffer.h`](../../../runtime/flow_ffi_buffer.h).
The prose contract is [docs/language/ffi-buffer.md](../../../docs/language/ffi-buffer.md).

## Zero-Copy Buffer ABI

Compatible contiguous pointer, span, and array data cross the boundary as a
view (`data`, `len`, `item_size`, `item_align`). The view stores the
caller's pointer. It does not copy payload bytes.

- **Borrowed** (`ffi_buffer_try_borrow` / `ffi_buffer_borrowed`): sender
  keeps the storage. The receiver must not free it or retain it after the
  call returns.
- **Owned** (`ffi_buffer_try_own` / `ffi_buffer_owned`): receiver frees
  `data` through `dealloc`.

`try_borrow` / `try_own` check the layout (size, stride, alignment). A
strided, under-aligned, or item-size-mismatched buffer returns a nonzero
status and an empty view. The helpers never silently `O(n)`-copy an `O(1)`
handoff. The named fallback is `ffi_buffer_copy_explicit`.

Calling across the FFI has a baseline overhead. For an `O(1)` buffer
handoff the overhead is fixed regardless of buffer size. Operations on
small batches (for example fewer than 1000 elements) may see FFI overhead
dominate. Batching over one contiguous view amortizes that cost.

## Instrumentation

Use `ffi_instrumentation_new`, `ffi_record_copy` and `ffi_record_zero_copy`
to track copies vs zero-copy handoffs. Record a copy only when the caller
opts into `ffi_buffer_copy_explicit`.
