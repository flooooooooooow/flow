# eBPF (bpfel) target

Flow compiles to ELF eBPF objects that the Linux kernel can load. The target
reuses the existing MLIR and LLVM pipeline, then applies the BPF ABI and a set
of verifier-oriented restrictions before LLVM's BPF backend emits the object.

Loading, attaching and live verifier runs are out of scope here; they belong to
`flow-kernel`. What this page covers is producing an object the kernel will
accept.

## Compiling a program

```bash
PYTHONPATH=src python3 -m flow.bpf_target tests/fixtures/bpf/socket_filter.flow \
  --target bpfel \
  --entry socket_filter \
  --section socket \
  --license GPL \
  -O 2 \
  -o socket-filter.bpf.o
```

| Flag | Meaning |
|------|---------|
| `-o`, `--output` | Output `.o` path. Required. |
| `--target` | `bpfel` (little-endian BPF). The only target today. |
| `--entry` | The exported Flow function to expose as a BPF program. |
| `--section` | ELF section for the program, for example `socket` or `xdp`. |
| `--license` | License string written to the `license` section. Defaults to `GPL`. |
| `-O` | `0`, `1`, `2` or `3`. Defaults to `2`. |

The input may be a `.flow` file or LLVM IR (`.ll`), which is useful when
inspecting what the pipeline produced before the BPF stage.

A minimal program is an exported function taking the program context:

```flow ignore="compiled by the bpfel target rather than the host toolchain"
export function socket_filter(context: ptr<void>) -> i32 {
    return 0
}
```

## What the target guarantees

The BPF ABI is fixed:

| Property | Value |
|---|---|
| Triple | `bpfel` |
| Data layout | `e-m:e-p:64:64-i64:64-i128:128-n32:64-S128` |
| Pointer width | 64 bits |
| Stack limit | 512 bytes, the kernel verifier's limit |

The entry function is placed in the section you name, and the license string is
emitted as a separate `license` section, which is what the kernel reads:

```llvm
define i32 @socket_filter(ptr %0) section "socket" {
@_flow_bpf_license = dso_local constant [4 x i8] c"GPL\00", section "license", align 1
```

## What it rejects

A BPF program runs in the kernel with no userspace runtime, so the target fails
the build rather than emitting an object the verifier will reject. Any reference
to an allocator or to C++ exception machinery is refused:

```
bpfel cannot depend on userspace runtime symbol 'malloc'
```

The full list is `malloc`, `calloc`, `realloc`, `free`, `operator new`, `_Znwm`,
`_Znam`, `__cxa_throw`, `__cxa_allocate_exception` and `_Unwind_`. In practice
this means BPF programs work on the stack and on context pointers, within the
512-byte limit.

## Entry point naming

The target lowers with `--llvm`, so the definition in the IR carries the plain
Flow name. It looks for `flow_export_<entry>` first and falls back to `<entry>`.

That order matters. The C backend emits both a mangled definition and a visible
`flow_export_<name>` alias for `--export`, so when both are present the alias is
the one to decorate; the MLIR path emits only the plain name. An earlier version
searched only for the alias, which the MLIR path never produces, so every build
failed with `exported BPF entry not found`.

## Toolchain

The clang on `PATH` needs LLVM's BPF backend. Apple's system clang does not have
it and fails with:

```
error: unable to create target: 'No available targets are compatible with triple "bpfel"'
```

This is the same limitation as the direct wasm32 target. On Linux, an LLVM 18
toolchain works; `.github/workflows/bpf.yml` installs one.

## What CI verifies

`.github/workflows/bpf.yml` compiles both fixtures, then checks the object
rather than trusting the exit code: `llvm-readelf` must report a BPF machine
type, and `llvm-objdump` must show the named program section and the `license`
section.

Unit coverage for the ABI contract, the forbidden-symbol check and the metadata
decoration lives in `tests/unit/test_bpf_target.py`.

## Related

- [WebAssembly](wasm.md) — the other freestanding target, with the same
  toolchain caveat
- [MLIR opt flags](mlir-opt-flags.md) — the optimizer this path runs through
