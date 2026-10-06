# FFI boundary audit (C / Python / native)

> **Status:** remaining #737 slice. The [zero-copy buffer ABI](ffi-buffer.md)
> is the C contract. This page is the Python and native-library audit, the
> #728 harness rows, and the break-even rule for real crossings.

A compiled win is wasted if the other side copies, widens, or byte-swaps
the buffer. The rule is the same on every surface: when the layout is
compatible, handoff is `O(1)` (pointer + metadata). When it is not, the
call fails closed. There is no silent `O(n)` conversion of an `O(1)`
handoff.

The executable catalog is `registry/packages/ffi/src/boundary_audit.flow`.
`tests/lang/test_ffi_boundary_audit.flow` checks every row.

## Surfaces

| Surface | Door | What crosses today |
|---|---|---|
| C | `extern`, `@cEmbed`, [`FlowFfiBuffer`](../../runtime/flow_ffi_buffer.h) | Pointer, span, array, borrowed string, struct-by-value, callback, buffer view |
| Native library | Same C ABI (BLAS, libc, a `.so`) | Same as C. Form a `FFIBuffer` / `ptr+len`. Do not pack. |
| Python (ctypes / buffer protocol / NumPy) | Consume the C ABI | Same as C when the array is C-contiguous and the dtype matches |
| `flow python` (pywheel) | Generated CPython module | `i32`/`i64`/`u32`/`u64`/`f32`/`f64`/`bool` by value; `string` as a UTF-8 decode **copy**; pointer, span, array, struct, callback, and `FFIBuffer` are **refused** |

`flow python` is intentionally narrow ([python-target](../python-target.md)).
It does not invent a second buffer ABI. A Python caller that needs a
zero-copy array uses the C header through ctypes, `memoryview`, or NumPy
(`ndarray.__array_interface__` / PEP 3118).

## Representation, ownership, alignment, dtype

| Kind | C / native / ctypes | Ownership | Alignment | Dtype / layout |
|---|---|---|---|---|
| Scalar | Register-sized value (`FFI_X_VALUE`) | Copied | n/a | Exact width. No implicit i32→i64. |
| `ptr<T>` + length | `T*` (`FFI_X_ZERO_COPY`) | Borrowed unless the callee takes `FFI_OWN_OWNED` | `data` must meet `item_align` | `item_size` must match `sizeof(T)` |
| `span<T>` | `{pointer, length}` (`FFI_X_ZERO_COPY`) | Always borrowed | Same as `ptr<T>` | Contiguous only (`stride == item_size`) |
| `array<T, N>` | `&arr[0]`, `N` (`FFI_X_ZERO_COPY`) | Borrowed | Same | Contiguous |
| `string` | `const char*` to the existing bytes (`FFI_X_ZERO_COPY`) | Borrowed. Receiver must not free. | Byte | UTF-8. Pywheel decodes into a `str` (`FFI_X_COPY`). |
| Struct | By value (`FFI_X_VALUE`, `O(sizeof)`) or by pointer | By-value is a copy of the record; by-pointer is a borrow | ABI alignment | Field layout is the C layout. No rename/reorder. |
| Callback | Function pointer (`FFI_X_VALUE`) | Caller keeps the code | n/a | Signature must match. Extra hop vs a direct call. |
| `FFIBuffer` | `FlowFfiBuffer` (`FFI_X_ZERO_COPY`) | Borrowed or owned, explicit | `item_align` | Fail closed on stride, size, or align mismatch |

Incompatible layout (wrong `item_size`, `stride != item_size`,
under-aligned pointer, unknown PEP 3118 format) returns `FFI_X_REFUSED`
and a null view. The named fallback is `ffi_buffer_copy_explicit`.

Python buffer-protocol mapping (`ffi_pep3118_format`,
`ffi_python_buffer_class`):

| Flow / C | PEP 3118 | NumPy dtype |
|---|---|---|
| `i8` / `u8` | `b` / `B` | `int8` / `uint8` |
| `i16` / `u16` | `h` / `H` | `int16` / `uint16` |
| `i32` / `u32` | `i` / `I` | `int32` / `uint32` |
| `i64` / `u64` | `q` / `Q` | `int64` / `uint64` |
| `f32` / `f64` | `f` / `d` | `float32` / `float64` |

A C-contiguous NumPy array whose `itemsize` and format match the want
layout is a zero-copy borrow of `ndarray.ctypes.data`. An F-contiguous
2-D array, a strided view, or a dtype cast (`float32` vs `float64`) is
refused. Do not `np.ascontiguousarray` / `astype` inside the handoff
helper: that is an `O(n)` copy the caller must choose.

## Callback overhead

A function-pointer hop costs `O(1)` extra calls and never copies the `O(n)` payload.
It still shows up on tiny callees. Batch the data, not the callback: one
crossing with a contiguous buffer beats N scalar callbacks.

## #728 harness rows

`./flow tool bench_harness` discovers every directory under
`benchmarks/cross_harness/{runtime,memory}/`. These rows put FFI boundary
overhead in the same schema as the rest of #728 (no new Python twins:
`flow python` cannot export a buffer, and the ratchet forbids new `.py`
files).

| Workload id | What it times |
|---|---|
| `runtime_ffi_scalar` | Many scalar `extern` calls |
| `runtime_ffi_batch` | One pointer+length call over a contiguous buffer |
| `runtime_ffi_buffer` | `ffi_buffer_try_borrow` then a C walk of the same pointer |
| `memory_ffi_handoff` | Borrowed view; instrumentation `copied_bytes=0` |
| `memory_ffi_copy` | Named `O(n)` fallback plus `memcpy` so #740 records copy volume |

## Break-even batching

Crossing into C has a fixed call cost `S`. A batched call costs
`F + W·N` (`F` is the extra handoff, `W` is per-element work). Batching
wins at

```
N >= ceil(F / (S − W))     when S > W
```

`ffi_breakeven_batch(S, F, W)` is that ceiling, or `0` when batching
cannot win. Do not copy a number from an old machine into a comment.

Measure on the current host:

```
./flow run benchmarks/micro/ffi_breakeven.flow
```

The program proves pointer identity (`copied_bytes=0`), times real C
crossings (scalar, batch, zero-copy buffer, explicit copy, borrowed
string, struct-sized value, callback), and prints `breakeven_batch=`.
Guidance: once `N` is at least that value, pass one contiguous view.
Below it, the call dominates. A compatible layout must still not copy.

Related: [FFI buffer ABI](ffi-buffer.md) · [spans](spans.md) ·
[export ABI](export-abi.md) · [Python target](../python-target.md) ·
[memory](../library/memory.md)
