# 16. Compilation targets and distribution

A Flow program can be compiled in several ways. The C and MLIR backends both
support the executable core, but their feature sets differ. Choose the target
before using closures, units, spans, effects, statics, SIMD, or a domain DSL.

## 16.1 C backend

```bash
./flow run program.flow
./flow compile program.flow
./flow transpile program.flow --c -o build/program.c
```

The default build emits C11, invokes the platform compiler, and links an
executable. The generated translation unit is inspectable and works with
native debuggers, sanitizers, static scanners, and existing libraries.

Use `FLOW_HOST=flowc` for the self-hosted Stage-A compiler,
`FLOW_HOST=python` for the full language, and `FLOW_HOST=auto` for a
self-hosted attempt followed by a Python-host fallback.

## 16.2 MLIR backend

```bash
./flow mlir program.flow
./flow mlir program.flow --optimize --opt-level 3
./flow mlir-run program.flow
./flow run program.flow --backend=mlir
```

The pipeline is:

```text
Flow AST -> MLIR dialects -> optimisation passes -> LLVM IR -> native code
```

MLIR supports the executable core, arrays, structs, ordinary control flow, and
many numeric operations. Important gaps include capturing closures, units,
spans, module statics, declarative sort pipelines, flows, fields, graphics, and
several effect details. A parallel loop currently executes serially after
lowering.

## 16.3 JIT execution

```bash
./flow jit program.flow
```

The JIT uses the MLIR/LLVM toolchain and runs generated machine code without a
separate persistent executable. JIT execution suits iterative numeric work but
inherits the MLIR feature matrix and requires installed LLVM tools.

Build guards can select JIT-specific implementations:

```flow
@only(jit)
function development_probe() -> void {
    println("JIT mode")
}
```

## 16.4 WebAssembly

```bash
./flow wasm program.flow --out build/wasm
./flow wasm program.flow --backend=mlir --out build/wasm-mlir
```

The usual build runs Flow through C and then Emscripten. The output directory contains a
module and runnable page. Stable `flow_export_...` aliases expose selected
functions to JavaScript.

Preload files and choose a filesystem:

```bash
./flow wasm program.flow \
    --preload assets@/assets \
    --fs idbfs \
    --out build/web
```

`memfs` is in-memory and session-local. `idbfs` persists through IndexedDB and
requires explicit synchronisation. A preload packages files into the module.

## 16.5 WebAssembly crossings

Browser execution changes system boundaries:

| Native facility | Browser crossing |
|---|---|
| OS threads | Emscripten pthreads, cross-origin isolation, shared memory |
| GPU | WebGPU and WGSL |
| TCP sockets | WebSocket relay or browser networking API |
| filesystem | MEMFS, IDBFS, preload, or browser file handles |
| embedded CPython | separately packaged interpreter/runtime assets |

Enable threads with `--threads`. A deployment must send the required COOP and
COEP headers for shared memory. Browser background scheduling, first-run JIT,
and transfer overhead can distort measurements.

The complete constraints and measured examples are documented in
[WASM crossings](../language/wasm-crossings.md).

## 16.6 Python packages

```bash
./flow python library.flow --name library --version 0.1.0
```

The command produces a CPython extension wheel through the C backend. It does
not interpret Flow as Python. Export analysis reports
which functions and structs have compatible signatures.

## 16.7 Native libraries and ABI

For a C or JavaScript consumer, generate named exports:

```bash
./flow transpile library.flow --c --library \
    --export add process \
    --module-name signal \
    -o build/signal.c
```

External consumers call versioned `flow_export_` aliases. `@flow_api` keeps a
specific plain symbol when source-level ABI control is appropriate. Pointers,
struct layout, ownership, alignment, calling convention, and error reporting
must be documented at every boundary.

## 16.8 GPU and shader targets

```bash
./flow gpu kernels.flow
./flow shader scene.flow
```

The two commands accept restricted device code and generate Metal or shader
sources. They do not produce a general host executable. The platform runtime
still allocates buffers, dispatches work, and presents frames.

## 16.9 Graphics and audio executables

```bash
./flow gfx application.flow
./flow window application.flow
./flow audio processor.flow
./flow compile-audio processor.flow
```

Each wrapper chooses runtime sources and linker flags for its domain. Audio can
request MLIR with `--mlir` where supported.

## 16.10 JavaScript/browser tutorial backend

The interactive documentation uses a small JavaScript compiler for core
examples. It supports less than native Flow. Effects, pointers, system calls,
native runtimes, and many DSLs do not run there. A browser example therefore
does not test parity with the native backends.

## 16.11 Target selection table

| Requirement | Preferred target |
|---|---|
| broadest language coverage | Python-hosted C backend |
| bootstrap/core build | self-hosted Stage A to C |
| inspectable portable native output | C backend |
| MLIR optimisation or in-memory execution | MLIR/JIT |
| browser delivery | WebAssembly |
| Python installation | CPython wheel |
| Metal compute | `flow gpu` |
| fill shader | `flow shader` |
| native interactive media | `gfx`, `window`, or `audio` |

## Exercises

1. Compile one core program through C and MLIR and compare exit status.
2. Inspect the generated C for a struct and one overloaded function.
3. Export a two-argument function to WebAssembly with a stable alias.
4. List every feature used by a proposed application and select a compatible
   backend before implementation.

Next: [Engineering, diagnostics, safety, and verification](17-engineering-and-verification.md).
