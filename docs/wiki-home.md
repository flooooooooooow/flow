# Flow Programming Language

A statically-typed, compiled language with **algebraic effects**, **automatic differentiation**, and **native graphics** — designed for audio, scientific computing, and systems programming at C-level speed.

```flow
function main() -> i32 {
    println("Hello, Flow!")
    return 0
}
```

---

## Why Flow

| Capability | What it means |
|------------|---------------|
| **Algebraic effects** | Swap I/O, logging, and state without rewriting call sites |
| **Built-in autodiff** | Forward and reverse mode for ML and optimization |
| **Dual compilation** | Portable C backend, or MLIR/LLVM for JIT and GPU |
| **flow-verify** | Optional third-party math proof library — not part of core Flow ([docs](third-party/flow-verify.md)) |

Flow compiles to efficient native code. Benchmarks show performance matching hand-written C.

---

## Quick start

```bash
git clone https://github.com/abhishekshivakumar/transpile.git
cd transpile
./flow run examples/basics/hello_world.flow
```

**Requirements:** Python 3.8+, Clang or GCC (LLVM optional for MLIR/JIT)

→ Full guide: [Getting Started](getting-started.md)

---

## Documentation map

### Learn
- [Interactive Tutorials](tutorials/index.html) — compile and run in the browser
- [Beginner Tutorial](tutorials/beginner.md) — variables, functions, control flow
- [Intermediate](tutorials/intermediate.md) — structs, generics, effects
- [Advanced](tutorials/advanced.md) — GPU, autodiff, systems patterns

### Reference
- [Language Spec](LANGUAGE_SPEC.md) — complete syntax and semantics
- [Type System](language/types.md) — primitives, generics, pointers
- [Standard Library](library/stdlib-reference.md) — API reference
- [Comparison](comparison.md) — Flow vs C, Rust, Zig

### Third-party: flow-verify
- [flow-verify](third-party/flow-verify.md) — formal math proof library (not core Flow)
- [Proof catalog](third-party/flow-verify-catalog.md) — browsable index
- [Verification spec](language/verification.md) — `theorem` / `therefore` design (library)

### Tooling
- [CLI & development](DEVELOPMENT.md) — compiler architecture
- [Python target](python-target.md) — generate Python wheels
- [Playground](playground/index.html) — try Flow in the browser

### Documentation project
- [Wiki strategy](wiki-strategy.md) — long-term IA, build pipeline, quality bar
- [Wiki roadmap](wiki-roadmap.md) — phased delivery plan
- [Language roadmap](project/language-roadmap.md) — compiler & language features

---

## Compiler backends

```
Flow source → C generator  → Clang     (portable, default)
            → MLIR generator → LLVM/JIT (optional)
            → Metal codegen  → GPU shaders
```

```bash
./flow run program.flow          # compile via C
./flow mlir program.flow         # emit MLIR
./flow mlir-run program.flow     # compile via MLIR pipeline
./flow jit program.flow          # JIT execution
```

---

## Project

| | |
|---|---|
| Version | 0.7.0 ([changelog](project/CHANGELOG.md) · [all releases](releases.md)) |
| License | MIT |
| Repository | [github.com/abhishekshivakumar/transpile](https://github.com/abhishekshivakumar/transpile) |
| Roadmap | [What's Next](NEXT.md) |