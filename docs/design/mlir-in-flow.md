# MLIR in Flow

The MLIR backend was the largest block of Python between flowc and deleting
`src/flow`. This page inventoried it, sorted it into what could move to Flow
and what could not, and recorded the order of the port. The port is
finished: `compiler/src/mlirgen.flow` writes the MLIR (`FLOWC_EMIT=mlir`),
shell scripts run the MLIR tools, and `src/flow` is gone. The first two
sections describe the backend as it is; the rest are the record of how it
got there, with the numbers of their time.

## Correct against the C backend

While the Python generator existed, the emitter copied it text for text,
bugs included, because text parity was the gate. With the Python generator
deleted, the contract is the C backend's: the emitter writes MLIR that
verifies, and the program built from it prints what the C build prints and
exits with the same code.

`compiler/scripts/mlir_vs_c.flow` holds it. It builds every tracked program
with a `main` through `flow compile` and `flow compile --backend=mlir`, runs
both with stdin closed and a timeout, and compares exit code and stdout. A
program the C backend does not build is counted apart; the floor in
`compiler/mlir_vs_c/floor.txt` gates the number that run the same. Output
that changes between two runs of the same build (clocks, addresses) is
not compared.

On macOS (LLVM 22), 2026-09-30:

| | when parity with Python was the contract | now |
|---|---|---|
| programs with `main` | 1465 | 1496 |
| the C backend builds | 1130 | 1156 |
| the MLIR backend builds too | 759 (67.2%) | 1090 (94.3%) |
| same exit code and stdout | 629 (55.7%) | 1018 (88.1%) |

The floor is 5 under the last recorded run, since a few timing programs
flap when the corpus runs in parallel.

`parity_mlir.flow` stays as the regression gate on the text: its goldens are
now recorded from flowc with `--record`, and each change to them comes with
the fix that caused it.

### What changed

* Issues: forward declarations emit nothing and overloads get the C
  backend's mangled names (#1059); `len` of spans, arrays and strings, and
  sized span parameters (#1060); `@gpu` negation, `!` and `elif` (#1061);
  lambda captures and untyped lambda bindings (#1062); non-literal consts,
  record update, unknown and capability types (#1063).
* Values: integer literals past the i32 range are i64, float literals f64;
  bools widen unsigned; conditions of any scalar type test `!= 0`; returned
  values are cast to the return type; `let x = e` takes the type of `e`.
* Printing and strings: `print`/`println` use the C backend's conversions
  and separators; string `+` (numbers formatted as C does), `==` and match
  patterns compare contents; C escapes in string literals are decoded.
* Floating point: `a * b + c` and its mirror images are one
  `llvm.intr.fmuladd`, the intrinsic clang emits when it contracts them
  within an expression, so LLVM fuses or splits them as it does for the
  C build and results agree to the bit. Float `!=` is unordered, so NaN
  != NaN, as in C. Unsigned integers convert to and from floats as
  unsigned.
* Control: `defer` runs on `break` and `continue` out of nested blocks;
  `elif` conditions see the locals as they were before the `if`; struct
  patterns check nested and literal fields; a match ends in
  `llvm.unreachable` only when every arm returns.
* Statements: `expect c` writes `expect failed (line N)` and exits 1 when
  `c` is false; `a = b = v` is an expression; `ui_*` layout blocks call
  their `_begin` and `_end` functions around the body.
* Runtime checks (`FLOWC_CHECKS=1`, the default of `flow_to_mlir.sh`):
  integer division by zero, shift range, and reads of sized arrays and
  spans abort with `flow: <what>` as the C backend's checks do.
* Data: statics fold negative and constant initializers; `[v; N]` takes a
  constant `N` and fills in a loop; a short array literal zeroes the rest;
  arrays over 64 KiB live on the heap, since an alloca in a loop is not
  released; arguments are evaluated left to right; an array returned by
  value is copied to the heap, and assigning to a sized array copies;
  `array<T>(n)` zeroes its elements.
* Intrinsics the C backend provides: `sizeof<T>()`, `flow_panic`,
  `i32_to_f32`, `str` as the string type.
* C interop: libc and `<math.h>` functions without a declaration are
  declared with their C signatures, and a Flow declaration of one (the
  `@libm` stubs of `stdlib/math.flow`) yields to libc, as the C header
  does. `@cInclude` and `@cImport` are accepted; `@cEmbed` C is written
  beside the MLIR and linked by `flow compile --backend=mlir`.
* Operators: `+ - * /` and unary minus on `Dual` call the overloads the C
  backend calls, and the `Tensor` operators call `tensor_add` and its
  siblings; `v in arr` scans a sized array; pointer minus pointer counts
  elements.
* Declarative ordering: `xs |> sort` (keys, `descending`, `unique`) is a
  stable merge sort and `xs |> find(t)` a search, both with the C
  backend's three-way compare (strcmp, IEEE 754 totalOrder, signed or
  unsigned order). Every C plan is stable, so the order agrees.
* More control and data: `@max_iterations(N)` aborts past its bound; a
  value function whose end is reachable returns zero; a field read
  through a mutable pointer uses its current value; rows of a nested
  array literal are copies, so a returned nested array keeps its rows;
  the proof layer is erased as for C, so proof-only files emit an empty
  module.
* Removed: string interpolation (the C backend prints the literal), the
  linalg rewrite of pointer loops (its casts do not lower), the
  module-wide array name cache.

### Known gaps

What the gate still reports, largest first:

* Types that only a C header defines. `stdlib/concurrent.flow` holds
  `pthread_mutex_t` and its kin by value from `<pthread.h>` (16
  programs); `c64` complex numbers, `stdlib/rf.flow` and a few fixtures
  name types the emitter has no layout for (12); `extern type` handles
  and helpers defined in an included header (3).
* Forms the emitter refuses: `impl Trait for Type` methods, which the
  parser skips; fields of a generic struct inferred at the call; two
  lowered forms of `test_lowered_forms.flow`; SIMD vector ops that
  mlir-opt does not know.
* A C-side reference that is itself undefined. Signed overflow in the
  LCGs of `stdlib/tensor.flow`, `examples/ml` and `hash_table.flow`
  (clang assumes it cannot happen, the MLIR build wraps); the GA history
  buffer the dynamics DSL sizes at 32 for 40 generations
  (`spring_mass_control`); reads past an array in `ok_namespaced`,
  `matmul_benchmark` and `livecode_demo`; type-error fixtures whose C
  build crashes.
* Floating point that still parts in the last bits and then grows:
  `double_pendulum` (chaotic) and `policy_pong`.
* Build-mode guards: `test_only_guard` expects the C build's modes, and
  the MLIR build runs under `mlir`.
* Concurrency and network examples whose C build waits past the timeout
  or whose output depends on scheduling.

## Finished: the Python MLIR stack is deleted

Every slice has landed and `src/flow` is gone. The MLIR backend is
`compiler/src/mlirgen.flow` for text, bash for process orchestration, and C
or Objective-C for the GPU runtimes. No MLIR command runs Python.

### Emitter coverage

Against the Python generator at `bb23f19f`, run with `--lenient` over every
`.flow` file in the repository:

| Mode | Python emits MLIR | flowc text-equal after normalization |
|---|---|---|
| 64-bit | 1270 | 1270 |
| `--mlir-gpu` (`FLOWC_MLIR_GPU=1`, programs with `@gpu`) | 14 | 14 |
| `--wasm32` (`FLOWC_MLIR_SIZE_T=32`) | 1270 | 1270 |

flowc also accepts 3 programs the Python generator fails on
(`tests/lang/test_prefix_deref.flow`, `tests/tools/lsp/fixtures/attr.flow`
and a fuzz crash reproducer). `parity_mlir.flow` holds this as goldens: 21
fixtures (text, and run output where mlir-opt is installed), the GPU and
wasm32 fixtures, and 1252 corpus digests. `--python <rev>` still compares
live against any revision that has the Python generator, taken with `git
archive`, so the gate outlives the deletion.

Added for the last slices: generic monomorphization, `fork`/`choose`
desugaring, range sums, test blocks, vectors,
tensors (struct fields, arguments, `tensor_add`, `tensor_matmul`), the AoSoA
rewrite, counted-loop rotation of `while true`, dual numbers through
operator structs, unsized arrays, 128-bit and wide integer literals, and the
wasm32 32-bit `size_t` ABI.

`FLOWC_LENIENT=1` makes non-fatal type errors warnings, as Python's
`--lenient` did. `flow_to_mlir.sh --lenient` sets it; the MLIR commands of
the driver and `--jit` use it.

### Orchestration

| Was | Now |
|---|---|
| `mlir_optimizer.py` pipelines | `compiler/scripts/mlir_optimize.sh`, pipeline text from `scripts/tools/mlir_pipeline` |
| `mlir_jit.py` lowering | `compiler/scripts/mlir_lower.sh` |
| `mlir_jit.py` loading, `jit_runner.py` (ctypes) | `flow jit`: emit, lower, link an executable, run it |
| `mlir_spirv.py` | `compiler/scripts/mlir_spirv.sh` |
| transpiler `--mlir` entry | `compiler/scripts/flow_to_mlir.sh`, `flow_to_llvm.sh` |
| `gpu_integration.py`, `gpu_runtime.py`, `metal_runtime.py` | `benchmarks/gpu/gpu_microbenchmark.c`, `runtime/gpu_metal.m` |

`./flow tool tests/mlir_commands/run.flow` checks 72 command cases (`flow mlir`,
`mlir-run`, `jit`, `ml`, `test-mlir`, `test-matmul`, `compile-audio --mlir`,
`--mlir-gpu`, `--emit-spirv` and the pass pipelines) against goldens
recorded from the Python stack at `bb23f19f`, with `python` and `python3`
stubbed to exit 127.

### What the deletion took with it

The Python parser, type checker, monomorphizer and module resolver had one
caller left, the MLIR generator, so they went with it: 30 files and 25,782
lines under `src/flow`, and 111 pytest files that imported them.

What those tests checked is covered as follows:

* MLIR text and runs: `parity_mlir.flow` and `./flow tool tests/mlir_commands/run.flow`.
* Lowering, DSLs and flow blocks: `tests/cgen`, `tests/lang`,
  `parity_flow_blocks.flow`, `parity_dynamics_dsl.flow`, `parity_field_dsl.flow`,
  `parity_shader_dsl.flow`, `parity_lowering.flow`, `parity_effects.flow`.
* Front-end crashes: `./flow tool tests/fuzz/run.flow` replaces the Python fuzz harness.
  It replays `tests/fuzz/crashes`, generates nesting 20000 levels deep, and
  runs seeded mutations of the corpus through flowc, failing on a signal or
  a hang. It found that flowc overflowed its stack on deep nesting;
  `FLOWC_PARSE_MAX_DEPTH` in `compiler/src/parser.flow` now makes that a
  parse error.
* The Stable conformance corpus: `./flow tool tests/conformance/run.flow`, through flowc.
* Type-checker rules flowc has: `tests/cgen/tc_reject_*` pin arity,
  unbound calls and a value returned from a void function.

### What the deletion left open

Some diagnostics existed only in the Python type checker. The port of that
checker to flowc (`compiler/src/sem_check.flow`, #1071) closed most of them:

* `./flow tool tests/conformance/run.flow` passes, including the Stable negatives
  `01_type_mismatch` and `02_immutable_assignment`.
* `scripts/check_doc_examples.sh --check-ledger` finds every
  `expect-error` example rejected, and the ledger is empty.
* `compiler/scripts/typecheck_rules.sh` holds one negative program per
  ported rule, and `compiler/scripts/parity_typecheck.sh --check` holds
  flowc to the Python checker's recorded diagnostics.

The last items on the old list are closed too, each with a negative program
in `compiler/fixtures/typecheck_rules/`:

* An invalid escape in a string (`"\x1b"`) is `Invalid escape sequence: \x`,
  the Python lexer's error, fatal in both modes (`escape_invalid`).
* `import "../x.flow"`, an absolute path or a `~` path is `Unsafe import
  path: ../x.flow`, the Python module resolver's error (`import_traversal`).
  The tracked imports that climbed out of their directory now name the
  sibling file (`scripts/tools/lattice_allpass`, `discord_welcome`) or drop
  a duplicate of `stdlib/vulkan_abi_renderer.flow` (`demos/vulkan_*_flow`).
* A literal `step 0` in a `for` range is `for range step must not be zero`
  (`for_step_zero`). This one is new: the Python checker had no rule and the
  loop spun at run time. The words follow range_sums.py, which rejected
  `sum(a..b step 0)`; flowc's closed form gives that sum 0 instead.
* Flow-stage parameters `x |> Stage { k: v }` outside a flow `output` get
  fork_records.py's error: they "are only valid for a flow used as a
  pipeline stage inside a flow output" (`flow_stage_outside_output`).
* Literal division by zero and shifts, the `FLOW_PROFILE` safety rules,
  `@rt_safe`, and the span and lifetime-domain checks were ported in #1071
  (`divide_by_zero`, `shift_*`, `safety_*`, `rt_safe_*`, `span_*`,
  `domain_*`).
* Match exhaustiveness and the checker's other warnings print as
  `FILE:LINE:COL: warning: ...` (#678), which the Python host never did.
  `flowc_emit.flow --no-warnings` (`FLOWC_WARNINGS=0`) silences them and
  `--Werror` (`FLOWC_WERROR=1`) makes them errors. Warnings inside
  `lib/stdlib` and `lib/runtime` are shown only with `FLOWC_WARNINGS=all`.
  `parity_typecheck.sh --check` holds them to the Python checker's list in
  `compiler/fixtures/typecheck_parity/warnings.txt` (`warn_*`,
  `werror_match`).

## Inventory

### Entry points

| Command or job | What it runs today |
|---|---|
| `flow run <p> --backend=mlir`, `flow compile <p> --backend=mlir`, `FLOW_CPU_BACKEND=mlir` | `compile_program_mlir` in the driver (now [`tools/flow_cli/toolchain.flow`](../../tools/flow_cli/toolchain.flow)). Since slice 1: flowc emitter plus `mlir_lower.sh` when the program is in the slice, else `python -m flow.transpiler --mlir --llvm`, then clang with the Flow runtime |
| `flow mlir <p> [--optimize ...]` | `python -m flow.transpiler --mlir`; `--optimize` runs `MLIROptimizer` (mlir-opt pass pipelines) |
| `flow mlir-run <p>` | `flow mlir`, then `mlir_lower_and_link` (mlir-opt, mlir-translate, llc, clang), now in [`tools/flow_cli/build.flow`](../../tools/flow_cli/build.flow) |
| `flow audio --mlir`, `flow compile-audio --mlir` | transpiler `--mlir --llvm`, linked with the audio runtime |
| `flow jit <p>` | `jit_runner.py`: `flow_to_mlir`, then `MLIRJIT` builds a shared object and calls it through ctypes |
| `flow ml [run\|jit\|bench\|test]`, `flow test-matmul` | the ML and matmul demos through the same MLIR generator, JIT and optimizer |
| `flow test-mlir` | `run_mlir_tests`: generate and lower `tests/mlir` plus three core programs |
| `flow wasm --backend=mlir`, `./flow tool wasm_build build --backend=mlir` | `scripts/tools/wasm_build`: transpiler `--mlir --llvm --wasm32` as a subprocess, then emcc |
| `flow bpf`, `flow wasm32` | `scripts/tools/llvm_target` through `compiler/scripts/flow_to_llvm.sh`: the flowc emitter plus `mlir_lower.sh` when the program is in the slice (for wasm32, also when it declares no external functions), else transpiler `--llvm`; then clang for the BPF or wasm32 target |
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

The emitter followed the Python lowering one decision at a time, down to its
quirks, because parity was the gate. Those quirks are fixed now; see
[Correct against the C backend](#correct-against-the-c-backend).

### `--backend=mlir` on the flowc host

`compile_program_mlir` in the driver (now [`tools/flow_cli/toolchain.flow`](../../tools/flow_cli/toolchain.flow)) tries flowc first: `FLOWC_EMIT=mlir`, then `compiler/scripts/mlir_lower.sh`,
then clang on the `.ll`. No Python runs. When flowc refuses the program the
driver prints

    flowc MLIR emitter does not cover this program yet (flowc mlir: unsupported: ...); using the Python MLIR generator

and takes the old path. `FLOW_HOST=python` is retired and no longer selects it.

### Parity gate

`compiler/scripts/parity_mlir.flow`, modelled on `parity_field_dsl.flow`:

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

Normalization (`gl_mlir_normalize` in `compiler/scripts/gate_lib.flow`) renames `%N` values and
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

### Python behaviour copied, then fixed

The Python MLIR behaviours this slice reproduced (untyped `let` as
`memref<16xi8>`, elif conditions reading the then-arm's locals, string `+`
as a comment, negative static initializers at zero, the module-wide array
name cache, `linalg.generic` through casts mlir-translate cannot lower) are
fixed; see [Correct against the C backend](#correct-against-the-c-backend).

### Refused on purpose

Proof-layer programs (the typecheck erases theorems into `AST_ERROR`
nodes, and Python rejects `TheoremDecl`), structs that hold a
Tensor-shaped field and Tensor arguments to struct-returning calls (Python's
`_is_tensor_struct` copies those its own way), the sprintf, snprintf,
fprintf and scanf externs (always `llvm.func` varargs in Python), list
patterns, spans, and everything in slices 5 to 11. The next section lifts
most of these. The proof layer is now erased as the C backend erases it.

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

## The rest of slice 4, slices 5 and 6, and attributes

### Data (rest of slice 4)

* Spans are Python's `!llvm.struct<(!llvm.ptr, i64)>`, handled as a
  struct: parameters are copied into an alloca, locals live in one, and a
  span returned from a call is stabilized. `s.len` is `extractvalue [1]`,
  `s[i]` reads and writes through `extractvalue [0]` and a GEP, and
  `base[a..b]` slices a pointer, a memref or a span. An argument bound to a
  span parameter is borrowed as `_generate_span_borrow` does: a slice, a
  span as it is, or a memref with its static size or `memref.dim`. `&[T]`
  is `span<T>`, and `[T; N]` is `array<T, N>`.
* `[v; N]` is written out N times, as Python's parser expands it.
* An array literal used as a value is a stack `memref<NxT>` typed by its
  first element (an `!llvm.array` alloca for struct and pointer elements);
  a memref local takes the declared element type. `array<T>(n)` is
  `memref.alloc` and `array<T>(a, b, ...)` a stored `memref.alloca`. A
  memref argument of another shape goes through `memref.cast`.
* The single-statement loop `out[i] = e` over local f32 or i32 memrefs takes
  `_try_vectorize_elementwise_for`: a `vector<4xT>` `scf.for` over the
  bulk and a scalar remainder loop.
* List patterns `[1, c, d]` compare literal elements and bind the others.
* Record update `Name { ..base, f: v }` (new in the Stage-A parser, marked
  by the parse-only `AST_RECORD_UPDATE`, which jsgen refuses; cgen lowers it
  too, as `({ Name t = base; t.f = v; t; })`, since #996) copies
  the base and inserts the listed fields.
* Consts take `generate_const`'s second path: cast-wrapped and negated
  literals, integer expressions folded as `_fold_const_binary` folds them,
  and zero for any other value. Statics fold the same way.
* A call to a name nobody declares (`len`, `abs` on an integer) is
  `func.call @name` typed from its arguments and returning i32, as
  `generate_function_call` writes it.

### Functions as values (slice 5)

A function type `(A) -> R` is the fat closure
`!llvm.struct<(!llvm.ptr, !llvm.ptr)>` of `mlir_closure_parity.py`. A
lambda is lifted to `func.func private @lambda_N(%env, ...)`, written ahead
of the declarations. Its captures are its free names, sorted, copied into a
malloc'd environment (calloc or a declared malloc when the program has one;
otherwise Python's own `llvm.func @malloc`), and loaded back through `%env`
in the body; a closure capture stays a closure
(`mlir_nested_closure_parity.py`). Calls through a closure local or
parameter extract the code and env pointers and `llvm.call` the code. A
named function passed to a closure parameter goes through a
`__flow_callback_<name>` adapter, and a function name used as a value is
`func.constant` cast to `!llvm.ptr`.

### Effects (slice 6)

`generate_effect`, `generate_capability`, `_generate_effects_init` and
`generate_handle`: a `_current_E_handler` global and a NULL-checked
dispatch function per operation, capability methods as `<Cap>_<method>`,
one zeroed vtable per handled effect filled by `@_flow_effects_init` (which
main calls first), and handle blocks that install the vtables and restore
them unless the body returned. An effect call inside a matching handle
calls the capability method directly; elsewhere it calls the dispatch
function. Any other method call is a call with the receiver first, as
Python desugars it.

Along with effects: variadic externs and the printf and scanf families are
`llvm.func` declarations called through `llvm.call ... vararg(...)`,
every overload is emitted with calls resolving to the last, and calls pass
the arguments they have against the parameter types.

### Forward declarations and imports

A forward declaration is emitted as Python emits it, a function with an
empty body beside the definition. An absolute import whose first part is a
`[dependencies]` key resolves under `flow_packages/<key>/src`, then
`flow_packages/<key>`. The imports that still do not resolve are programs
Python cannot build either: 17 name modules or packages missing from the
checkout, and 18 are proof-layer claim imports whose programs Python rejects as
`TheoremDecl`.

### Attributes and the GPU dialect

An `@gpu` function leaves the host module, as `generate_module` splits
kernels off. Mode guards follow `transpiler._function_allowed` with the
modes the MLIR backend runs under (`compile`, `mlir`). With
`FLOWC_MLIR_GPU=1`, the counterpart of `--mlir-gpu`, the kernels become
`gpu.module @flow_kernels` as `mlir_gpu_codegen.py` writes it. That
generator numbers each kernel's values from `%1`, so the normalizer starts
names over at each `gpu.func`; `parity_mlir.flow` checks `gpu_*` fixtures in
GPU mode and, with `--python`, every accepted program that has a kernel.
`@cInclude`, `@cEmbed` and `@cImport` were refused while parity with
Python held (Python rejected the first two); they are accepted now, see
[Correct against the C backend](#correct-against-the-c-backend).

Type aliases lower as their base type and units as f64
(`_resolve_type_alias`).

### More Python behaviour copied, then fixed

Filed as #1059 to #1063 while parity was the gate, and fixed since (see
[Correct against the C backend](#correct-against-the-c-backend)): forward
declarations and overloads, `len` of a span and sized span parameters, the
`@gpu` negation, `!` and `elif`, lambda captures, non-literal consts,
record update on an untyped base, unknown types as `memref<16xi8>`, `[v;
N]` with a literal N only, the vectorized loop's `i32` bounds, the void
lambda and callback adapter. Arithmetic on dual numbers through operators
calls the `add`, `sub`, `mul`, `div` and `neg` overloads, as in C.

### Numbers

Same corpus and Python reference (`84806b0d`) as above. `tests/lang` now
holds 183 programs.

| After | Accepted | Text equal | Run same | Timing/address output | Builds on neither path | `tests/lang` |
|---|---|---|---|---|---|---|
| Slice 4 part (#1041), run again | 794 | 794 | 353 | 21 | 420 | 81 |
| Spans, list patterns, array literals and constructors, folded consts | 829 | 828 | 367 | 21 | 440 | 91 |
| Lambdas and closures | 844 | 843 | 372 | 21 | 450 | 93 |
| Effects, C varargs, overloads, method calls | 920 | 919 | 397 | 21 | 501 | 106 |
| Forward declarations, package imports | 947 | 946 | 398 | 21 | 527 | 125 |
| `@gpu` kernels and mode guards | 955 | 953 | 404 | 21 | 528 | 125 |
| Record update | 956 | 954 | 405 | 21 | 528 | 125 |
| GPU dialect (`FLOWC_MLIR_GPU=1`) | 957 | 955 | 406 | 21 | 528 | 125 |
| Type aliases and units | 968 | 966 | 413 | 21 | 532 | 126 |

Text and run failures are 0 in every row; so are programs that build on
one path only. Accepted programs beyond the text-equal ones are programs
Python itself fails on: a parser crash, and an `@gpu` kernel with a `vec`
type Python cannot parse. The run columns come from one run of the final
text-equal set through both MLIR paths, counted over each commit's
recorded corpus and fixtures, so the first row differs slightly from the
figures above (a few large programs time out in clang under load). In GPU
mode, 5 of 5 corpus programs with a kernel Python lowers are text-equal;
Python fails on the other 3, and flowc refuses them.

`parity_mlir.flow` golden mode: 18 fixtures (text and run, and `gpu_kernels`
in GPU mode) and 948 recorded corpus programs.

## Slice order

Each slice ends the same way: the parity gate grows, the refusal list
shrinks, and Python code is deleted only where nothing calls it any more.

1. **Core language** (done).
2. **Remaining statement forms** (done except `expect` and `dbg`): `match`
   and enums (`mlir_parity.py`, `mlir_match_termination.py`), `defer`,
   address-of, `let` without an annotation, uninitialized locals and the SSA
   merges they need (scf.if yields, loop-carried block arguments).
3. **Modules** (done): bundle mode for programs with imports, module
   statics, consts Python folds.
4. **Data** (done): memref arrays and arrays of structs, spans and slices,
   list patterns, the `array<T>(n)` constructors, record update.
5. **Functions as values** (done): lambdas, closures, callbacks
   (`mlir_closure_parity.py`, `mlir_nested_closure_parity.py`).
6. **Effects and capabilities** (done).
7. **AST rewrites** (done): counted-loop rotation, AoSoA layout and the
   linalg/vector rewrites of elementwise loops (`mlir_canonicalize.py` and
   the `_try_*_elementwise_for` paths). The linalg rewrite over pointers is
   done, and so is the vector rewrite of single-store memref loops.
8. **Orchestration** (done): the `mlir_optimizer.py` pipelines and `mlir_spirv.py`
   as bash beside `mlir_lower.sh`; `flow mlir`, `mlir-run`, wasm and BPF
   switched to flowc.
9. **Denotational dialect**: once the lane lands, a second pass over flow
   blocks writes the `flow.*` module ahead of the operational one, under the
   same `FLOW_DENOTATIONAL=1` switch.
10. **GPU** (done): `mlir_gpu_codegen.py` (`FLOWC_MLIR_GPU=1`) and
    `metal_codegen.py` as Flow text emitters; Metal and CUDA runtimes in C.
11. **JIT** (done): `flow jit` as emit, lower, link and run; `mlir_jit.py`,
    `jit_runner.py` and the ctypes runtimes deleted.
