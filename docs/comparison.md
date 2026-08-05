# Flow vs C · Rust · Zig · Mojo

Where Flow sits relative to systems and AI/ML languages. For the dynamics / control-engineering story, see [Flow vs MATLAB/Simulink](#flow-vs-labviewsimulink--matlabsimulink) below and [VISION.md](../VISION.md) at the repo root.

## At a glance

| Dimension | Flow | C | Rust | Zig | Mojo |
|-----------|------|---|------|-----|------|
| **Memory model** | Manual + helpers; no GC | Manual | Ownership / borrow checker | Manual + allocators | Ownership (Rust-like) |
| **Effects / side effects** | Algebraic effects (first-class) | Conventions / errno | `Result` + traits | Error unions | Python-style + extras |
| **Autodiff** | Stdlib + tools (not a compiler AD pass) | Libraries | Libraries (e.g. burn) | Libraries | Core ML feature |
| **Audio / DSP** | First-class stdlib paths | External libs | Ecosystem crates | DIY / C interop | Not a focus |
| **Compile target** | Portable C (+ MLIR/LLVM) | Native object code | LLVM | LLVM / C ABI | Machine code + Python interop |
| **Syntax feel** | Explicit types, Rust/Go-ish | Low-level | Strict / expressive | Explicit / C-like | Python-like |
| **Package story** | Local registry index + git/path (`flow.toml`) | Headers / build systems | crates.io | zig fetch | Modular / evolving |
| **Learning curve** | Moderate | Steep for safety | Steep | Moderate–steep | Easy if you know Python |
| **Best fit today** | Audio, dynamics seed, systems demos | Embedded, OS, ABI glue | Safe systems at scale | Tooling, interop, freestanding | AI/ML productivity |

## Feature deep dive

### Memory & safety

| | Flow | C | Rust | Zig | Mojo |
|-|------|---|------|-----|------|
| Buffer overflows | Programmer discipline | Same | Prevented by types | Discipline + optional checks | Ownership helps |
| Null | `null` + pointers | Ubiquitous | `Option` | Optional pointers | Safer defaults |
| GC pause | None | None | None | None | None (ownership) |

### Concurrency & effects

| | Flow | C | Rust | Zig | Mojo |
|-|------|---|------|-----|------|
| Threads | POSIX + `runtime/flow_concurrency.c` | pthreads / OS | `std::thread` + async | std.Thread | Runtime / Python model |
| Channels / WaitGroup | Real buffered channels in `concurrent.flow` | DIY | channels crate / sync | DIY | Framework-dependent |
| Data-parallel | `parallel for` → OpenMP when available | OpenMP / TBB | rayon | DIY | Hardware accel |
| Side-effect control | Effect handlers (`_Thread_local`) | Informal | Types + `unsafe` | Explicit errors | Framework-dependent |
| Async | Effects (`SimulatedAsync` / `ThreadedAsync` / `FiberAsync` / `NetpollAsyncIO`; no `async` keyword) | Callbacks / libs | `async`/`await` | Manual / event loops | Interactive notebooks |

Vs **Go** specifically: see [concurrency-vs-go.md](language/concurrency-vs-go.md) and [replace-go.md](language/replace-go.md) — effects + no-GC + data-parallel is the wedge. Flow ships `NetpollAsyncIO` + 2-way `select2`; Go still leads on mature netpoller integration / N-way `select`.

### Differentiation & numerics

| | Flow | C | Rust | Zig | Mojo |
|-|------|---|------|-----|------|
| Forward / reverse AD | Stdlib dual numbers + grad tools | Manual / libs | Ecosystem | Ecosystem | Native focus |
| SIMD | `vec4` / stdlib | Intrinsics | `std::simd` | `@Vector` | Hardware accel for ML |
| GPU | Experimental `@gpu` / Metal path | CUDA/OpenCL by hand | Growing | Via C | Strong ML path |

## When to choose what

**Choose Flow** when you want algebraic effects, library autodiff, and audio/dynamics-oriented systems code that still emits portable C.

**Choose C** when you need maximum ABI control, tiny runtimes, or to meet an existing C-only interface.

**Choose Rust** when memory safety at scale and a mature package ecosystem matter more than effects + stdlib AD.

**Choose Zig** when you want explicit allocators, superb C interop, and a modern “better C” toolchain.

**Choose Mojo** when the workload is AI/ML and Python interop / notebook speed dominate.

## Flow vs LabVIEW/Simulink · MATLAB/Simulink

The workflow Flow ultimately targets is the fragmented control-engineering toolchain: analyze in MATLAB, diagram in Simulink, model physics in Modelica, then hand-write or code-generate C for deployment. Every hand-off loses information. Flow's answer: **the model is the program.**

| Feature | Flow | MATLAB/Simulink |
|---------|------|-----------------|
| **Model → deployment** | One source file → C | Model in one tool, code in another |
| **System declaration** | `dsys` in the program | Block diagrams / `ss()` elsewhere |
| **Analysis** | `sense` blocks bound to program variables | Rich toolboxes outside the deployable artifact |
| **Controller synthesis** | GA gain search (`ga evolve`), `closed` blocks | PID/LQR/MPC toolboxes |
| **Runtime artifact** | Native binary; no runtime license | Toolchain hand-off; licenses |
| **Breadth today** | LTI seed (honest scope) | Decades of numerical breadth |

> [!note] Honest scoping
> What ships today is discrete/continuous *linear* `dsys` plants, `sense` analysis, Gramians, and GA-based gain search — see the [dynamics DSL](language/dynamics-dsl.md). MATLAB remains far ahead numerically. The end-state is [VISION.md](../VISION.md).

## Performance

Measured on 2026-07-29 on an Apple M4 Max, comparing Flow binaries against
hand-written C compiled by the same clang with the same flags
(`-O3 -march=native`). Median of 5 runs, workload time only.

- Dense 300x300 matrix multiply: Flow 0.0167 s, C 0.0167 s (1.00x).
- Mandelbrot count, 400x400 grid: Flow 0.0069 s, C 0.0069 s (1.00x).
- N-body, 1,000,000 steps: Flow 0.0320 s, C 0.0257 s (1.24x). The gap
  comes from clang specializing the static hand-written functions for a
  constant body count, which Flow's externally visible functions block.
- The same n-body run in plain CPython took 5.4521 s.

Full tables, methodology, and reproduce instructions:
[benchmarks/RESULTS.md](../benchmarks/RESULTS.md). Regenerate with
`./benchmarks/run_publish.sh`.

## See also

- [Quick Start](getting-started.md)
- [Effects showcase](effects-showcase.md)
- [Autodiff library](library/autodiff.md)
- [Language roadmap](project/language-roadmap.md)
