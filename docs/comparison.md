# Flow vs C · Rust · Zig · Mojo

Where Flow sits relative to systems and AI/ML languages. For the dynamics / control-engineering story, see [Flow vs MATLAB/Simulink](#flow-vs-labviewsimulink--matlabsimulink) below and [VISION.md](../VISION.md) at the repo root.

## At a glance

| Dimension | Flow | C | Rust | Zig | Mojo |
|-----------|------|---|------|-----|------|
| **Memory model** | Manual + helpers; no GC | Manual | Ownership / borrow checker | Manual + allocators | Ownership (Rust-like) |
| **Effects / side effects** | Algebraic effects (first-class) | Conventions / errno | `Result` + traits | Error unions | Python-style + extras |
| **Autodiff** | Built into the language | Libraries | Libraries (e.g. burn) | Libraries | Core ML feature |
| **Audio / DSP** | First-class stdlib paths | External libs | Ecosystem crates | DIY / C interop | Not a focus |
| **Compile target** | Portable C (+ MLIR/LLVM) | Native object code | LLVM | LLVM / C ABI | Machine code + Python interop |
| **Syntax feel** | Explicit types, Rust/Go-ish | Low-level | Strict / expressive | Explicit / C-like | Python-like |
| **Package story** | Early (`flow.toml`) | Headers / build systems | crates.io | zig fetch | Modular / evolving |
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
| Threads | POSIX wrappers in stdlib | pthreads / OS | `std::thread` + async | std.Thread | Runtime / Python model |
| Side-effect control | Effect handlers | Informal | Types + `unsafe` | Explicit errors | Framework-dependent |
| Async | Modeled via effects (no `async` keyword) | Callbacks / libs | `async`/`await` | Manual / event loops | Interactive notebooks |

### Differentiation & numerics

| | Flow | C | Rust | Zig | Mojo |
|-|------|---|------|-----|------|
| Forward / reverse AD | Language-level | Manual / libs | Ecosystem | Ecosystem | Native focus |
| SIMD | `vec4` / stdlib | Intrinsics | `std::simd` | `@Vector` | Hardware accel for ML |
| GPU | Experimental `@gpu` / Metal path | CUDA/OpenCL by hand | Growing | Via C | Strong ML path |

## When to choose what

**Choose Flow** when you want algebraic effects, built-in autodiff, and audio/dynamics-oriented systems code that still emits portable C.

**Choose C** when you need maximum ABI control, tiny runtimes, or to meet an existing C-only interface.

**Choose Rust** when memory safety at scale and a mature package ecosystem matter more than effects/AD as language features.

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

On microbenchmarks (Apple Silicon, clang `-O3`), Flow matches C within noise and is typically 50–100× faster than CPython for the same algorithms. Full tables: [Benchmark results](project/benchmark-results.md).

## See also

- [Quick Start](getting-started.md)
- [Effects showcase](effects-showcase.md)
- [Autodiff library](library/autodiff.md)
- [Language roadmap](project/language-roadmap.md)
