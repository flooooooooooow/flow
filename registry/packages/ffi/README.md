# FFI Package

The FFI package provides little-endian buffer packing helpers and tools for managing the FFI boundary, including zero-copy ABI definitions for contiguous buffers (`ffi_buffer_handoff`).

## Zero-Copy Buffer ABI

The FFI boundary rules for buffer handoffs:
- **Owned Buffer**: The receiver takes responsibility for freeing the buffer using the provided deallocator. Use `ffi_buffer_owned`.
- **Borrowed Buffer**: The sender retains ownership. The receiver must not use the buffer after the function returns. No copies are made. Use `ffi_buffer_borrowed`.

Calling across the FFI has a baseline overhead. For $O(1)$ buffer handoffs (i.e. passing a pointer), the overhead is fixed regardless of buffer size. Operations on small batches (e.g. < 1000 elements) may see FFI overhead dominate. Batching operations on large buffers amortizes this cost to effectively zero.

## Instrumentation
Use `ffi_instrumentation_new`, `ffi_record_copy` and `ffi_record_zero_copy` to track how many copies vs zero-copy handoffs are occurring across your FFI boundaries.
