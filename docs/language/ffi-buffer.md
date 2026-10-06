# Zero-copy FFI buffer ABI

> **Status:** C ABI from #1347; Python/native audit, #728 harness rows, and
> live break-even measurements are in [ffi-boundary-audit.md](ffi-boundary-audit.md).

A compiled win is wasted if the FFI copies the buffer. The contract is: when
the layout is compatible, handoff is `O(1)` (pointer + metadata). When it is
not, the call fails closed and the caller chooses whether to copy.

C header: [`runtime/flow_ffi_buffer.h`](../../runtime/flow_ffi_buffer.h)
(`FlowFfiBuffer`, ABI version 1).

Flow types: `registry/packages/ffi/src/buffer_handoff.flow` (`FFIBuffer`).
The field order matches the C struct.

## View

| Field | Meaning |
|---|---|
| `data` | Pointer to the first element. This is the caller's storage. |
| `len` | Element count. |
| `item_size` | Bytes per element. |
| `item_align` | Required alignment of `data` (power of two, or 0/1 = any). |
| `ownership` | `FFI_OWN_BORROWED` (0) or `FFI_OWN_OWNED` (1). |
| `dealloc` / `dealloc_ctx` | Owned-only free function and optional context. |

A layout is the element size, the stride in bytes, and the alignment.

```c
typedef struct FlowFfiLayout {
    int64_t item_size;
    int64_t stride;
    int32_t item_align;
    int32_t reserved;
} FlowFfiLayout;
```

Compatible sources (contiguous, matching `item_size`, pointer meets
`item_align`):

| Source | How to form the view |
|---|---|
| `ptr<T>` + length | `data`, `len`, `item_size = sizeof(T)` |
| `span<T>` / `span<mut T>` | `values.data`, `values.len` — already `{pointer, length}` |
| `array<T, N>` / `array<T>` | `&arr[0]`, `N` or `length(arr)` |

`stride` must equal `item_size`. A strided, padded, or mixed-endian buffer
is not a supported zero-copy handoff.

## Borrowed vs owned

**Borrowed** (`ffi_buffer_try_borrow` / `FLOW_FFI_OWN_BORROWED`). The sender
keeps the storage. The receiver may read or write through `data` only for
the duration of the call. It must not free the pointer or store it past
return.

**Owned** (`ffi_buffer_try_own` / `FLOW_FFI_OWN_OWNED`). The receiver takes
the pointer and frees it with `dealloc` (plus `dealloc_ctx` when the
callback needs a context). The sender must not free it again.

Unchecked `ffi_buffer_borrowed` / `ffi_buffer_owned` exist for a layout the
caller has already proved. They still store the pointer; they do not copy.

## Incompatible layout: fail closed

`ffi_layout_compatible` / `flow_ffi_layout_compatible` return a status and
never touch payload bytes.

| Status | Meaning |
|---|---|
| `FFI_OK` (0) | Contiguous, sizes match, pointer alignment holds. |
| `FFI_ERR_NULL` | Missing layout, or `len > 0` with a null pointer. |
| `FFI_ERR_BAD_LEN` | Negative length. |
| `FFI_ERR_BAD_SIZE` | Non-positive `item_size`. |
| `FFI_ERR_BAD_ALIGN` | Alignment is not 0/1 or a power of two, or `data` is under-aligned. |
| `FFI_ERR_STRIDE` | `stride != item_size` (not contiguous). |
| `FFI_ERR_INCOMPATIBLE` | `item_size` differs (for example i32 vs i64). |

`try_borrow` / `try_own` on a nonzero status return an empty buffer
(`data == null`). They do **not** pack, widen, or byte-swap into a new
allocation. That would turn an `O(1)` handoff into an `O(n)` copy without
the caller seeing it.

The named fallback is `ffi_buffer_copy_explicit`. Call it only after a
failed check, and record the bytes with `ffi_record_copy`. Do not hide that
path inside the handoff helpers.

## Batching

Crossing into C has a fixed call cost. For an `O(1)` buffer handoff that
cost does not grow with `len`. Measure the live break-even with
`./flow run benchmarks/micro/ffi_breakeven.flow` and read
[ffi-boundary-audit.md](ffi-boundary-audit.md). Batch into one contiguous
view when the element type and stride already match.

## Proof

`tests/lang/test_ffi_buffer.flow` checks that a supported i32 handoff keeps
the same pointer on both the Flow and C helpers, that a write through the
view mutates the original storage, and that a strided or size-mismatched
layout returns an error with a null view and no copy instrumentation.
`benchmarks/micro/ffi_boundary_benchmark.flow` prints a pointer-identity
row next to the scalar / batched / large-buffer timings.

Related: [boundary audit](ffi-boundary-audit.md) · [spans](spans.md) · [export ABI](export-abi.md) · [memory](../library/memory.md)
