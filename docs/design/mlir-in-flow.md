# MLIR in Flow

The MLIR backend is the largest block of Python between flowc and deleting
`src/flow`. This page inventories it, sorts it into what can move to Flow now
and what cannot, and records the order of the port. The first slice has
landed: `compiler/src/mlirgen.flow` emits textual MLIR for the core language,
selected with `FLOWC_EMIT=mlir`, and `flow run --backend=mlir` uses it.

## Inventory

### Entry points

| Command or job | What it runs today |
|---|---|
| `flow run <p> --backend=mlir`, `flow compile <p> --backend=mlir`, `FLOW_CPU_BACKEND=mlir` | `compile_program_mlir` in `flow-driver`. Since slice 1: flowc emitter plus `mlir_lower.sh` when the program is in the slice, else `python -m flow.transpiler --mlir --llvm`, then clang with the Flow runtime |
| `flow mlir <p> [--optimize ...]` | `python -m flow.transpiler --mlir`; `--optimize` runs `MLIROptimizer` (mlir-opt pass pipelines) |
| `flow mlir-run <p>` | `flow mlir`, then `mlir_lower_and_link` in bash (mlir-opt, mlir-translate, llc, clang) |
| `flow audio --mlir`, `flow compile-audio --mlir` | transpiler `--mlir --llvm`, linked with the audio runtime |
| `flow jit <p>` | `jit_runner.py`: `flow_to_mlir`, then `MLIRJIT` builds a shared object and calls it through ctypes |
| `flow ml [run\|jit\|bench\|test]`, `flow test-matmul` | the ML and matmul demos through the same MLIR generator, JIT and optimizer |
| `flow test-mlir` | `run_mlir_tests`: generate and lower `tests/mlir` plus three core programs |
| `flow wasm --backend=mlir`, `scripts/wasm_build.sh --backend=mlir` | `wasm_compiler.py`: transpiler `--mlir --llvm --wasm32` as a subprocess, then emcc |
| `python -m flow.bpf_target` | transpiler `--mlir --llvm` as a subprocess, then clang for the BPF target |
| `--mlir-gpu`, `--emit-spirv` | `mlir_gpu_codegen.py` (gpu dialect text) and `mlir_spirv.py` (mlir-opt and mlir-translate to SPIR-V) |
| Metal and CUDA runtimes | `metal_codegen.py` (MSL text), `metal_runtime.py`, `gpu_runtime.py`, `gpu_integration.py` (ctypes, numpy) |

CI: `.github/workflows/ci.yml` installs the MLIR tools for the `flow-tier2`
job, `bpf.yml` compiles `tests/fixtures/bpf/*.flow` through MLIR to BPF ELF,
and `wasm32.yml` compiles `tests/fixtures/wasm/*.flow` through MLIR to
WebAssembly and compares against native MLIR builds. `tests/unit` has 18
`test_mlir_*.py` files that import the generator directly.

The denotational lane described in `AGENTS.md` (a `flow.*` dialect for
evolution blocks, `FLOW_DENOTATIONAL=1`, a `denotational_blocks` argument to
`flow_to_mlir`) is not on `main` at the time of this slice; there is no
`src/flow/denotational_mlir.py` to port yet. Its hook is additive: when it is
set, the dialect module is written ahead of the operational lowering. The
Flow emitter keeps the same shape (see the slice order below).

### Python modules

| Module | Lines | Role | Kind |
|---|---|---|---|
| `mlir_generator.py` | 7746 | AST to textual MLIR (func, arith, scf, cf, llvm, memref, vector, linalg) | text emission |
| `mlir_parity.py`, `mlir_match_termination.py`, `mlir_closure_parity.py`, `mlir_nested_closure_parity.py` | 1004 | patches installed on the generator at import (match, terminators, closures) | text emission |
| `mlir_canonicalize.py` | 457 | AST rewrites before emission: counted-loop rotation, trivial accessors, AoSoA layout | text emission (AST pass) |
| `mlir_gpu_codegen.py` | 494 | gpu dialect module for `@gpu` functions | text emission |
| `metal_codegen.py` | 456 | Metal shading language text | text emission |
| `mlir_optimizer.py` | 482 | mlir-opt pass pipelines, autotuning, reports | process orchestration |
| `mlir_jit.py` (lowering half) | about 150 | mlir-opt and mlir-translate to LLVM IR, clang | process orchestration |
| `mlir_spirv.py` | 268 | mlir-opt and mlir-translate to SPIR-V | process orchestration |
| `mlir_jit.py` (loading half), `jit_runner.py` | about 600 | build a shared object, `ctypes.CDLL`, call entry points | ctypes runtime |
| `metal_runtime.py`, `gpu_runtime.py`, `gpu_integration.py` | 1304 | Metal and CUDA device access, numpy buffers | ctypes runtime |

### What the Python emits

One `module { ... }` of textual MLIR:

* `llvm.func @printf(!llvm.ptr, ...) -> i32` when anything prints, then one
  `llvm.mlir.global internal constant @str_N(...)` per interned string, in
  first-use order.
* One `func.func` per function, `func.func private` per extern, a comment
  block per struct, one `llvm.mlir.global` per module const or static.
* Scalars in `arith`; mutable locals and every struct local in one-slot
  `llvm.alloca`s; structs as `!llvm.struct<(...)>` built with
  `llvm.insertvalue`; fixed arrays as `!llvm.array<N x T>` allocas indexed
  with `llvm.getelementptr`; pointers as `!llvm.ptr`.
* Control flow as `cf` blocks, except a counted loop with a positive literal
  step and a simple body, which becomes `scf.for`, and the `if`s inside it,
  which become `scf.if`. `and`, `or` and if-expressions are valued `scf.if`.
* On request: `memref`/`linalg`/`vector` for elementwise loops, the `gpu`
  dialect, debug info, a wasm32 data layout.

### External tools

`mlir-opt` (lowering pass list in `mlir_jit.py`; optimization pipelines in
`mlir_optimizer.py`), `mlir-translate --mlir-to-llvmir`, `llc` (only in
`mlir-run`), clang (link, wasm, BPF), emcc (wasm).

## The split

1. **Text emission moves to Flow.** Everything that turns the AST into MLIR
   text: `mlir_generator.py`, its four patch modules, `mlir_canonicalize.py`,
   `mlir_gpu_codegen.py` and `metal_codegen.py`. This is plain string
   building over the AST, the same kind of work `cgen.flow` does for C.
2. **Process orchestration moves to bash.** Running mlir-opt, mlir-translate,
   llc and clang with fixed flags needs no language at all.
   `compiler/scripts/mlir_lower.sh` now does what `MLIRJIT.compile_mlir_to_llvm`
   does. The optimizer pipelines and SPIR-V lowering follow the same pattern.
3. **The ctypes runtimes stay native.** Loading a shared object and calling
   into Metal or CUDA is C's job. The JIT becomes "emit, lower, link an
   executable, run it" (what `--backend=mlir` already does), and the Metal
   and CUDA device code moves to C next to `runtime/gpu_metal.m`.

## Slice 1 (this change)

`compiler/src/mlirgen.flow`, about 4800 lines, selected with `FLOWC_EMIT=mlir`
(or `FLOWC_BACKEND=mlir`) on the single-file emit path.

Covered: functions and externs, `i8` to `i64`, `u8` to `u64`, `f32`, `f64`,
`bool`, `string`, `ptr<T>`, `array<T, N>`, structs (nested, as parameters and
return values), module consts with literal values, arithmetic, bitwise,
comparison and short-circuit operators, unary `-`, `!`, `not`, `~`, casts,
`if`/`elif`/`else`, if-expressions, `while`, `for` with `to` or `..`, literal,
negative and runtime steps, `break`, `continue`, `print`, `println`,
`printf`, and the `sin`/`cos`/`sqrt`/... intrinsics on floats.

Everything else is refused with a located reason, for example
`flowc mlir: unsupported: match statement at line 8`. Refusal is deliberate:
a program either gets the Python generator's MLIR or it gets none.

The emitter follows the Python lowering one decision at a time, down to its
quirks, because parity is the gate. Known quirks it reproduces rather than
fixes (each is a Python MLIR behaviour that differs from the C backend):

* an `i64` passed to `println` is printed with `%d`;
* `println` of a `string` variable prints no newline;
* float literals are `f32` constants, widened with `arith.extf`;
* integer literals above 2^31-1 wrap to negative `i32` constants;
* a `bool` widened to an integer uses `arith.extsi`, so `true` becomes -1;
* `for i in 5 to 0` counts down (the C backend runs no iterations).

These belong in a later behaviour fix made on both generators at once.

### `--backend=mlir` on the flowc host

`compile_program_mlir` in `flow-driver` now tries flowc first (the default
`FLOW_HOST=flowc`): `FLOWC_EMIT=mlir`, then `compiler/scripts/mlir_lower.sh`,
then clang on the `.ll`. No Python runs. When flowc refuses the program the
driver prints

    flowc MLIR emitter does not cover this program yet (flowc mlir: unsupported: ...); using the Python MLIR generator

and takes the old path. `FLOW_HOST=python` always takes the old path.

### Parity gate

`compiler/scripts/parity_mlir.sh`, modelled on `parity_field_dsl.sh`:

* golden mode (no Python): the fixtures in `compiler/fixtures/mlir/` against
  their `.mlir` goldens (normalized Python output) and, with mlir-opt
  installed, their `.out` goldens (stdout and exit code of the program built
  through the Python MLIR path); plus every program in
  `compiler/fixtures/mlir/corpus.txt` must still be accepted with the same
  normalized MLIR (a digest per program).
* `--python <rev>`: the Python generator from git revision `<rev>` over the
  fixtures and every `.flow` under `examples/`, `tests/`, `lib/`,
  `benchmarks/` and `compiler/fixtures/`. Every program flowc accepts must
  give the same normalized MLIR; with mlir-opt installed, each is built
  through both MLIR paths and run, and the runs must agree.
* `--write-golden <rev>` rewrites the goldens.

Normalization (`compiler/scripts/mlir_normalize.awk`) renames `%N` values and
`^bbN` labels in order of first appearance and drops indentation. Python
numbers a value before it emits the value's operands, so its numbers are not
in text order; the renaming makes that irrelevant. Nothing else is
normalized.

Numbers against the Python generator at `eec7463f` (origin/main when the
slice landed), on macOS with Homebrew LLVM 22:

| Check | Result |
|---|---|
| Fixtures, MLIR text | 7 of 7 equal |
| Fixtures, run output | 7 of 7 equal |
| Repository programs flowc accepts (of 2,400 `.flow` files) | 291 |
| Of those, MLIR text equal to Python after normalization | 290; the other one crashes the Python parser |
| Built through both MLIR paths and run | 184 same output, 16 print timings or addresses (differ from run to run on either path), 90 build on neither path (they need the Flow runtime or a C header) |
| `tests/lang` programs covered | 16 of 166 |

The refusals are led by imports (455 programs), `@gpu`/mode/C-interop
attributes, elementwise pointer loops that Python vectorizes, `match`,
`defer` and address-of.

## Slice order

Each slice ends the same way: the parity gate grows, the refusal list
shrinks, and Python code is deleted only where nothing calls it any more.

1. **Core language** (this slice).
2. **Remaining statement forms**: `match` and enums (`mlir_parity.py`,
   `mlir_match_termination.py`), `defer`, `expect`, `dbg`, address-of, `let`
   without an annotation, uninitialized locals and the SSA merges they need
   (scf.if yields, loop-carried block arguments).
3. **Modules**: bundle mode for programs with imports, module statics,
   string and cast-wrapped consts. This is where most of the corpus is: 455
   of the refused programs stop at an import.
4. **Data**: arrays of structs, spans and slices, memref arrays, the
   `array<T>(n)` constructors, record update.
5. **Functions as values**: lambdas, closures, callbacks
   (`mlir_closure_parity.py`, `mlir_nested_closure_parity.py`).
6. **Effects and capabilities**.
7. **AST rewrites**: counted-loop rotation, AoSoA layout and the
   linalg/vector rewrites of elementwise loops (`mlir_canonicalize.py` and
   the `_try_*_elementwise_for` paths).
8. **Orchestration**: the `mlir_optimizer.py` pipelines and `mlir_spirv.py`
   as bash beside `mlir_lower.sh`; `flow mlir`, `mlir-run`, wasm and BPF
   switched to flowc.
9. **Denotational dialect**: once the lane lands, a second pass over flow
   blocks writes the `flow.*` module ahead of the operational one, under the
   same `FLOW_DENOTATIONAL=1` switch.
10. **GPU**: `mlir_gpu_codegen.py` and `metal_codegen.py` as Flow text
    emitters; Metal and CUDA runtimes in C.
11. **JIT**: `flow jit` as emit, lower, link and run; `mlir_jit.py`,
    `jit_runner.py` and the ctypes runtimes deleted.
