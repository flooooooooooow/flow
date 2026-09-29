# MLIR in Flow

The MLIR backend is the largest block of Python between flowc and deleting
`src/flow`. This page inventories it, sorts it into what can move to Flow now
and what cannot, and records the order of the port. Slices 1 to 3 have
landed, with the parts of slice 4 that Python lowers the same way today:
`compiler/src/mlirgen.flow` emits textual MLIR for the core language,
statement forms, programs with imports and module statics, selected with
`FLOWC_EMIT=mlir`, and `flow run --backend=mlir` uses it.

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

## Slice 1

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

## Slices 2 and 3, and part of 4

### Statement forms (slice 2)

* `match` with the arms `_generate_match_with_parity` lowers: int, negative
  int, float, string and bool literals, `_`, a binding name, `default`,
  struct patterns `P(a, b)` (fields extracted positionally; literal and
  nested fields become checks Python ignores), enum variant names, and
  or-patterns and guards over those. The join takes `llvm.unreachable` when
  every arm returns, as `mlir_match_termination.py` adds it.
* Enums lower as the tagged struct Python synthesizes (`tag: i32`, then
  `<Variant>_value` for each variant with a payload), with the variant tag
  globals ahead of every other declaration. The emitter builds the struct
  from synthesized AST nodes, so field access, struct literals and
  parameters reuse the struct path.
* `defer`: block exit runs the block's defers last to first, `break` and
  `continue` run the current block's, and `return` runs every pending defer
  after its value is computed. Python generates those defers before the
  value, which fixes string numbering, so the emitter generates them first
  too and moves their text after the value.
* Address-of on locals (the local moves into an alloca from then on),
  consts, statics, struct fields and array elements, with Python's spill
  fallback.
* `let x = e` with no annotation takes Python's `auto` type, which it lowers
  to `memref<16xi8>`, and `let mut x: T` with no initializer is an
  `llvm.mlir.undef` that assignments rebind.
* A local that is not in an alloca is an SSA binding, and Python merges it
  where control flow joins: `scf.if` results for an if/else, block arguments
  on the join of a cf `if`, `elif` chain or `match`, loop-carried arguments
  on the header, body and exit of `while` and cf `for` loops, `iter_args`
  on `scf.for`, and the carried values on `break` and `continue`. The
  emitter keeps the same lists in the same order (`_assigned_locals`,
  `_filter_ssa_mergeable`, `_detect_loop_carried_vars`).

### Modules (slice 3)

`compiler/src/mlir_bundle.flow` builds the declaration list Python's
`module_resolver.py` builds. It resolves legacy string imports (the
importing file's directory, `lib/stdlib` with and without a `stdlib/`
prefix, `packages/`, the project root), relative dotted imports and absolute
dotted imports (`std`, the `[paths]` of the nearest `flow.toml`, then the
stdlib and the project root, longest module prefix first), and walks them
depth first: a module's imports load, in order, before its own
declarations, and a loaded module is skipped. The expanded modules are
joined in that order and parsed once. The emitter drops imports,
`export a, b` lists and an imported module's `main`, as the resolver does.
Each module is typechecked, dependencies first, with the exports before it
in scope. `FLOWC_EMIT=mlir` takes this path for any program with an
import, and for `FLOWC_BUNDLE=1`. The driver passes `FLOWC_ROOT`, where
`packages/` and the fallback `lib/stdlib` live. A refusal inside an
imported module names it: `... at line 16 of lib/stdlib/font.flow`.

Top-level `let mut` statics lower as Python's `generate_static` does:
scalar globals (a literal, or a const that resolves to one, is the initial
value; anything else starts at zero), string, pointer and struct globals
with LLVM-dialect initializer regions, and fixed arrays as `!llvm.array`
globals built element by element. Reads load through `llvm.mlir.addressof`,
writes store, and an array static indexes through its address.
Parameterless accessors that return a static, a const or its address are
inlined at their calls (#474).

### Data (part of slice 4)

Uninitialized fixed arrays are `memref.alloca`s (spelled with the element's
own type name, `memref<16xu8>`, as Python writes it), memref elements load
and store through `memref.load`/`memref.store`, `array<T>` with no size is
`memref<?xT>` for parameters and results, and a memref passed as a pointer
decays through `memref.extract_aligned_pointer_as_index`. Arrays of structs
and array fields initialized from a literal inside a struct literal
(`_generate_llvm_array_aggregate`) are covered. The single-statement loop
`out[i] = a[i] op b[i]` over `0 to N` on f32 or i32 pointers becomes
Python's `linalg.generic` (`_try_linalg_elementwise_for`); every other
pointer loop lowers normally. Spans and slices are not covered: Python
only borrows spans from memref arrays, so the programs that use them mostly
fail on the Python side.

### Python behaviour copied, not fixed

These are Python MLIR behaviours the emitter now reproduces. Each one gives
MLIR that does not verify or does not do what the program says, on both
paths:

* `let x = e` with no annotation types `x` as `memref<16xi8>`, so any
  arithmetic on it is typed `memref<16xi8>` too.
* The `elif` conditions of a cf `if` read the locals the then-arm assigned
  (the entry bindings are restored only before each arm's body), which
  fails dominance when the then-arm assigned one.
* String `+` becomes a `# String concatenation: ...` comment and a value
  with no definition.
* A static initialized with a negative literal (`let mut x: i32 = -1`)
  starts at zero; only a bare literal is kept.
* The `!llvm.array` tag Python records for a local is also cached under the
  local's name for the rest of the module, so a later `ptr` local of the same
  name, in any function, is indexed as that array.
* `linalg.generic` loops go through `builtin.unrealized_conversion_cast`,
  which mlir-translate cannot lower.

### Refused on purpose

Proof-layer programs (the typecheck erases theorems into `AST_ERROR`
nodes, and Python rejects `TheoremDecl`), structs that hold a
Tensor-shaped field and Tensor arguments to struct-returning calls (Python's
`_is_tensor_struct` copies those its own way), the sprintf, snprintf,
fprintf and scanf externs (always `llvm.func` varargs in Python), list
patterns, spans, and everything in slices 5 to 11.

### Numbers

Against the Python generator at `84806b0d` (origin/main; its MLIR generator
is unchanged since `eec7463f`), over every `.flow` under `examples/`,
`tests/`, `lib/`, `benchmarks/` and `compiler/fixtures/`, on macOS with
Homebrew LLVM 22. A program counts as accepted when flowc emits MLIR for it.
"Run" builds it through both MLIR paths and compares stdout and exit code.

| After | Accepted | Text equal | Run same | Timing/address output | Builds on neither path | `tests/lang` |
|---|---|---|---|---|---|---|
| Slice 1 (#1020, at `eec7463f`) | 291 | 290 | 184 | 16 | 90 | 16 of 166 |
| Slice 2 | 364 | 364 | 225 | 16 | 123 | 23 of 168 |
| Slice 3 | 645 | 640 | 302 | 18 | 320 | 79 of 168 |
| Slice 4, part | 794 | 794 | 356 | 21 | 417 | 81 of 168 |

Text and run failures are 0 in the final row. The slice 3 commit had four
text mismatches, fixed in the next commit: a memref passed as a pointer
(Python decays it) and the sprintf family. One more program crashes the
Python parser and is not counted. Programs that build on neither path are
mostly the `memref<16xi8>` locals above, or need the Flow runtime or a C
header.

`flow run --backend=mlir` with `python` and `python3` replaced by failing
stubs builds and runs the fixtures, including `imports_statics.flow`.

## Slice order

Each slice ends the same way: the parity gate grows, the refusal list
shrinks, and Python code is deleted only where nothing calls it any more.

1. **Core language** (done).
2. **Remaining statement forms** (done except `expect` and `dbg`): `match`
   and enums (`mlir_parity.py`, `mlir_match_termination.py`), `defer`,
   address-of, `let` without an annotation, uninitialized locals and the SSA
   merges they need (scf.if yields, loop-carried block arguments).
3. **Modules** (done except string and cast-wrapped consts): bundle mode
   for programs with imports, module statics.
4. **Data** (memref arrays and arrays of structs done): spans and slices,
   list patterns, the `array<T>(n)` constructors, record update.
5. **Functions as values**: lambdas, closures, callbacks
   (`mlir_closure_parity.py`, `mlir_nested_closure_parity.py`).
6. **Effects and capabilities**.
7. **AST rewrites**: counted-loop rotation, AoSoA layout and the
   linalg/vector rewrites of elementwise loops (`mlir_canonicalize.py` and
   the `_try_*_elementwise_for` paths). The linalg rewrite over pointers is
   done; the vector rewrite only fires on memref arrays.
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
