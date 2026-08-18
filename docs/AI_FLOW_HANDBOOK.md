# Working with AI on Flow

## A formal operating handbook for building, testing, and extending Flow programs

**Edition:** 1.0  
**Repository baseline:** Flow 0.11.1, August 2026  
**Language:** simplified technical English

---

## Preface

This book explains how to direct an AI coding agent to use the Flow programming
language and to work safely in the Flow repository. It is an operating manual.
Its main content is instructions, process, reference data, and practical know-how.

The book is based on the present construction of Flow:

- a small, statically typed language;
- a self-hosted Stage-A compiler, called `flowc`, for the stable core;
- a Python compiler host for the full language surface;
- C as the default portable CPU target;
- optional MLIR, Metal, WGSL, SPIR-V, WebAssembly, graphics, audio, and native
  runtime paths;
- examples and tests as executable evidence;
- human direction for design and AI assistance for implementation.

Flow changes quickly. This book shows how to check the current repository. The
repository is the final source for current behavior.

### Intended reader

Use this book to ask an AI to:

- write a Flow program;
- explain a Flow program;
- find and reuse a Flow feature;
- repair a compiler or runtime defect;
- add a language feature;
- improve an example, test, library, backend, or document;
- evaluate whether a Flow claim is supported by working code.

You do not need to be a compiler engineer. You should be able to state the
result you want and review evidence that the result works.

### Meaning of key words

The formal terms have these meanings:

- **MUST** means the rule is required for a reliable result.
- **SHOULD** means the rule is normally correct, but a stated reason may justify
  another action.
- **MAY** means the action is optional.
- **Evidence** means a file, command result, test, measurement, generated
  artifact, or other item that another person can inspect.
- **AI** means a coding agent that can read files, edit files, and run commands.
- **Human** means the person who owns the goal and has final design authority.

### Contents

1. [The operating model](#part-i-the-operating-model)
2. [Directing the AI](#part-ii-directing-the-ai)
3. [Producing Flow programs](#part-iii-producing-flow-programs)
4. [Verification and diagnosis](#part-iv-verification-and-diagnosis)
5. [Extending the language and implementation](#part-v-extending-the-language-and-implementation)
6. [Methods that have worked](#part-vi-methods-that-have-worked)
7. [Common failure patterns](#part-vii-common-failure-patterns)
8. [Reusable operating procedures](#part-viii-reusable-operating-procedures)
9. [Prompt library](#part-ix-prompt-library)
10. [Reference](#part-x-reference)
11. [Coverage audit](#part-xi-coverage-audit)
12. [Flow as a language for vibe coding](#part-xii-flow-as-a-language-for-vibe-coding)

---

# Part I: The operating model

## 1. Give the AI a work contract

An AI works best when the request states the outcome, the reason, the limits,
and the proof of completion. A request such as “add support for X” is incomplete.
It does not say which compiler host, which backend, which syntax limits, or which
tests define success.

Use this contract:

```text
Goal:
Why it matters:
In scope:
Out of scope:
Required compatibility:
Required evidence:
Files or areas to preserve:
```

Example:

```text
Goal: Add a fixed-size moving average example in Flow.
Why it matters: It will be the first audio tutorial example.
In scope: One example, one runtime test, and a short tutorial section.
Out of scope: New syntax, heap allocation, and MLIR-specific optimization.
Required compatibility: C backend on the Python host; real-time-safe style.
Required evidence: The example compiles, runs, returns 0, and the runtime test
passes.
Files or areas to preserve: Do not change unrelated compiler code.
```

The human MUST decide the product intent. The AI MAY decide ordinary
implementation details when the repository already establishes a pattern.
The AI MUST return a real design choice to the human when the choice changes
language meaning, syntax, public API, architecture, or project scope.

### 1.1 A useful division of work

| Area | Human responsibility | AI responsibility |
|---|---|---|
| Goal and value | Decide what matters | Restate the goal precisely |
| Language syntax | Give final approval | Find precedents and propose options |
| Architecture | Give final approval | Trace dependencies and identify risks |
| Implementation | Review important choices | Edit in small, complete slices |
| Verification | Decide acceptable risk | Run checks and report exact results |
| Documentation | Judge clarity and truth | Draft, link, and keep examples runnable |
| Scope | Approve expansion | Prevent accidental expansion |

### 1.2 Define “done” before code changes

A Flow task is done only when all required layers agree. For a normal program,
this often means:

1. The source parses.
2. The source passes the intended type checks.
3. The selected backend emits valid output.
4. The native toolchain accepts that output.
5. The program runs.
6. A check confirms the result. Printed output alone is not enough.
7. Relevant existing tests still pass.
8. The documentation describes the behavior that actually shipped.

For a compiler feature, add these conditions:

9. Invalid input has a clear diagnostic.
10. Other backends either support the feature or reject it honestly.
11. The self-hosted and Python hosts have an explicit parity decision.
12. A regression test fixes the behavior in place.

Do not let “the patch is written” mean “the task is done.”

---

## 2. Understand how Flow is constructed

The AI MUST form a correct mental model before it changes Flow. The most useful
model is a pipeline with several possible routes.

```text
.flow source
    |
    +--> flowc host (default, Stage-A subset) --> C --> cc/clang --> program
    |
    +--> Python host (full surface)
             |
             +--> C ---------------------------> cc/clang --> program
             +--> MLIR --> LLVM tools ----------------------> program/JIT
             +--> Metal / WGSL / SPIR-V --------------------> GPU artifact
             +--> C or MLIR --> Emscripten -----------------> WebAssembly
```

This layout affects how the AI must work.

### 2.1 There are two compiler hosts

`FLOW_HOST=flowc` is the default for `run` and `compile`. It uses the
self-hosted Stage-A compiler. Stage-A is intentionally smaller than the full
language. It covers the core needed to compile the compiler itself.

`FLOW_HOST=python` uses the Python implementation under `src/flow/`. Use it for
the broader language surface, including many DSLs, effects, tests, MLIR, GPU,
and graphics operations.

The AI MUST choose the host explicitly when a feature is outside Stage-A. It
MUST NOT report a Stage-A failure as a general Flow failure until it checks the
Python host.

Basic core command:

```bash
./flow run examples/basics/fibonacci.flow
```

Full-surface command:

```bash
FLOW_HOST=python ./flow run examples/evolution/pendulum_evolves.flow
```

### 2.2 C is the default portable backend

The C route is the normal baseline. It is easy to inspect, compile, link, and
debug. It also provides a clear boundary between Flow behavior and native
toolchain behavior.

Use C first unless the task specifically concerns MLIR, JIT, GPU, or another
target. A backend-specific task SHOULD still keep the C behavior in view when
the language construct is intended to be portable.

### 2.3 MLIR is a co-equal path, not the definition of Flow

MLIR supports optimization, JIT use, and paths toward GPU lowering. It is not
the only compiler path. A proposal that works only by changing MLIR may leave
the default C path inconsistent.

Use:

```bash
FLOW_HOST=python ./flow run program.flow --backend=mlir
FLOW_HOST=python ./flow mlir program.flow --optimize
FLOW_HOST=python ./flow mlir-run program.flow
```

The AI MUST state when MLIR or LLVM tools are required and unavailable.

### 2.4 The front end has ordinary compiler stages

For the Python host, the main files are:

| Stage | Main implementation | Purpose |
|---|---|---|
| Parse | `src/flow/parser.py` | Tokens, grammar, AST construction |
| Resolve | `src/flow/module_resolver.py` | Modules and imported declarations |
| Check | `src/flow/type_checker.py` | Names, types, effects, semantic rules |
| Special lowering | `src/flow/flow_blocks.py` and DSL modules | Convert higher forms to ordinary AST |
| Generic expansion | `src/flow/monomorphize.py` | Produce concrete generic instances |
| C output | `src/flow/c_generator.py` | Portable C generation |
| MLIR output | `src/flow/mlir_generator.py` | MLIR generation |
| Other targets | target-specific generator modules | Metal, WGSL, SPIR-V, Python, JavaScript |

For the self-hosted compiler, the corresponding sources are under
`compiler/src/`, including `lexer.flow`, `parser.flow`, `ast.flow`,
`typecheck.flow`, `resolve.flow`, and `cgen.flow`.

### 2.5 Higher-level forms use two implementation channels

Flow has core AST features and pre-parse DSL expansion. This distinction is
important.

- A feature belongs in the real AST when it needs lasting language semantics,
  type checking, accurate diagnostics, or backend-wide support.
- A feature may start as a pre-parse expander when it generates ordinary Flow
  from a specialised analysis description.

Current `flow` blocks, state, parameters, `evolves as`, `every`, and `when`
have core lowering support. Some dynamics, field, geometry, and analysis
surfaces are expanded before the main parser.

The AI MUST find which channel an existing feature uses before it edits that
feature. It SHOULD NOT move a feature between channels during an unrelated
task.

---

## 3. Use a truth hierarchy

Documents can be old. Examples can be experimental. A parser may accept syntax
that a backend does not implement. The AI needs an ordered method for deciding
what is true.

Use this evidence order:

1. A test that runs in the requested configuration.
2. A canonical example that runs in the requested configuration.
3. Current implementation code on the exact path.
4. Current command help and project configuration.
5. The language specification and focused feature documents.
6. The roadmap, vision, design sketches, and comments.

Items 5 and 6 explain intent. They do not override a failed executable check.

### 3.1 Mark every claim by status

When the AI researches a feature, it SHOULD classify it as one of the
following:

| Status | Meaning | Required action |
|---|---|---|
| Shipped and tested | A relevant test passes | Reuse the tested path |
| Shipped with limits | The implementation states important restrictions | Preserve and document the limits |
| Parsed only | Syntax exists without complete semantic or backend support | Do not present it as operational |
| Example only | A demo exists but lacks a stable contract | Verify before reuse |
| Designed | A document defines future behavior | Ask before implementing it |
| Planned | A roadmap item names a direction | Do not invent missing semantics |

### 3.2 Use repository data honestly

The generated repository snapshot dated 10 August 2026 reports:

| Area | Files | Physical lines |
|---|---:|---:|
| Flow source | 1,965 | 197,416 |
| Examples | 399 | 103,974 |
| Tests | 347 | 38,302 |
| Standard library | 105 | 31,989 |
| Python compiler | 62 | 47,130 |
| Self-hosted compiler | 17 | 9,440 |
| Runtime | 41 | 7,105 |
| Verification corpus | 1,078 | 18,715 |

These numbers show where evidence is likely to exist. They do not prove
quality. The AI SHOULD use the current
`docs/generated/repository-stats.json` when exact current counts matter.

---

# Part II: Directing the AI

## 4. Start every substantial session with context recovery

Before editing, tell the AI to perform a short context pass. The pass prevents
duplicate work and incorrect assumptions.

Use this instruction:

```text
Before changing files:
1. Read the local contribution instructions.
2. Inspect git status and preserve unrelated changes.
3. Read the current roadmap entries related to this task.
4. Find the nearest working example and nearest focused test.
5. Trace the execution path that the change will use.
6. State the selected compiler host, backend, and verification commands.
```

The AI SHOULD use fast repository searches, for example:

```bash
rg --files
rg -n "feature_name|syntax_token|runtime_symbol" src compiler tests examples docs
git log --oneline -30
git status --short
```

### 4.1 Protect a dirty worktree

The AI MUST assume that existing changes belong to the human. It MUST inspect
`git status` before broad edits. It MUST NOT discard, reset, overwrite, or
reformat unrelated work.

If the task overlaps an already modified file, instruct the AI to:

1. inspect the current diff;
2. identify which lines belong to the existing work;
3. make the smallest compatible edit;
4. report the overlap in the handoff.

### 4.2 Recover the project’s current direction

Use these files for different questions:

| Question | Source |
|---|---|
| Why does Flow exist? | `VISION.md` |
| What is presented to users? | `README.md` |
| What is planned? | `ROADMAP.md` and `docs/NEXT.md` |
| What needs a human decision? | `Questions.md` |
| What is the formal language surface? | `docs/LANGUAGE_SPEC.md` |
| How do the compiler paths fit? | `docs/project/architecture-writeup.md` |
| What does Stage-A support? | `compiler/README.md` |
| What patterns should examples use? | `docs/project/pattern-adoption.md` |
| What is known to work? | `tests/`, `examples/`, and CI configuration |

The AI SHOULD read only the relevant parts after it has found them. It SHOULD
not load the whole repository into its working context.

---

## 5. Write requests that produce reviewable work

A useful request gives the AI a narrow unit of work. It also states
which evidence must be returned.

### 5.1 Request a program

```text
Create a Flow program that [behavior].
Use [Stage-A core / Python full surface].
Target [C / MLIR / WASM / gfx / audio].
Start from [named example or library module].
Do not add new syntax or runtime APIs.
Make the program check [invariant or expected result] and return non-zero on
failure.
Run [specific commands].
```

### 5.2 Request a bug fix

```text
Reproduce [observed failure] in the smallest fixture.
Trace it to the earliest incorrect compiler stage.
Fix the cause. Do not stop after fixing a generated symptom.
Add one positive regression and one nearby negative or edge case.
Run the focused test first, then the relevant suite.
Do not change public behavior outside [scope].
```

### 5.3 Request a language feature

```text
Implement [feature] as one vertical compiler slice.
First find the approved syntax and semantic decision.
Cover lexer/parser, AST, type checking, lowering/code generation, formatter or
LSP when applicable, valid tests, invalid tests, and documentation.
State the parity decision for flowc and the Python host.
State the parity decision for C, MLIR, and other affected backends.
Stop for human direction if the semantics are not already decided.
```

### 5.4 Request a refactor

```text
Refactor [area] without changing observable behavior.
Capture the current behavior with tests before moving code.
Keep the patch mechanical where possible.
Do not combine cleanup with a new language feature.
Show that generated output or runtime results are unchanged where practical.
```

### 5.5 Request research or diagnosis

```text
Do not edit yet.
Find the current implementation and all supported routes.
Separate shipped behavior, known limitations, and planned behavior.
Give exact file references and reproduction commands.
Recommend the smallest next action with its risks.
```

Use this form when the goal is uncertain. It prevents early code changes.

---

## 6. Require an evidence ledger

For substantial work, tell the AI to keep a small evidence ledger. The ledger
is a table in its final report or a temporary note during work.

| Claim | Evidence | Result |
|---|---|---|
| Syntax is accepted | focused parser test | pass/fail |
| Invalid case is rejected | diagnostic test | exact diagnostic |
| C output is valid | generated C plus clang | pass/fail |
| Program behavior is correct | runtime exit and invariant | value |
| Existing behavior is safe | relevant regression suite | counts |
| Documentation is current | link and command check | pass/fail |

The AI MUST distinguish estimated values from measured values. This is already
a Flow design principle. For example, `flow explain` prints estimated element
operations for selection plans; benchmark documents contain measurements.
The AI MUST NOT describe a compiler cost estimate as a timing measurement.

### 6.1 Prefer invariants over attractive output

A program that draws a good image or prints plausible numbers may still be
wrong. Ask the AI to check an invariant.

Examples:

- a damped pendulum loses energy over measured intervals;
- bounce apexes decrease;
- a sort result is ordered and preserves required stability;
- an audio callback performs no forbidden allocation;
- a parser rejects an unsupported pattern with a precise message;
- two compiler generations produce identical output;
- a backend parity test returns the same result on C and MLIR.

The repository’s evolution demonstrations use this practice: they print a
measured quantity, compare it with theory, and return a failure code if the
relationship is broken.

---

# Part III: Producing Flow programs

## 7. Select the smallest suitable execution route

Before writing source, make the AI fill this table:

| Decision | Common choices | Default rule |
|---|---|---|
| Compiler host | `flowc`, `python` | Use `flowc` for Stage-A core; Python for full surface |
| CPU backend | C, MLIR | Use C unless MLIR is part of the goal |
| Program mode | run, compile, gfx, audio, wasm, shader | Use the mode closest to the final environment |
| Safety level | default, safety, flight | Use default during early work; add the required production profile |
| Test level | parser, unit, compile, runtime, parity, end-to-end | Start focused; expand by risk |

### 7.1 Stage-A core is useful for portable, simple programs

Use Stage-A when the program can stay within ordinary functions, structs,
fixed arrays, pointers, loops, basic `match`, imports supported by Stage-A,
and direct C interoperability.

```flow
function sum_to(n: i32) -> i32 {
    let mut total: i32 = 0
    for i in 0 to n + 1 {
        total = total + i
    }
    return total
}

function main() -> i32 {
    if sum_to(10) != 55 {
        return 1
    }
    return 0
}
```

Run:

```bash
./flow run program.flow
```

### 7.2 Use the Python host for Flow’s broader forms

Select the Python host for algebraic effects, generics beyond Stage-A,
declarative dynamics, specialised DSLs, broad module behavior, MLIR, GPU, or
other full compiler facilities.

```bash
FLOW_HOST=python ./flow run program.flow
```

Do not hide this requirement. Put it in the example header, tutorial command,
or project script when users need it.

### 7.3 Keep the route repeatable

The AI SHOULD return the exact command it used. Environment variables are part
of the command’s meaning. “It works with Flow” is less useful than:

```bash
FLOW_HOST=python FLOW_PROFILE=safety ./flow compile program.flow
```

---

## 8. Build ordinary Flow code first

Flow’s core surface is deliberately readable. Ask the AI to prefer explicit
types and direct control flow until a higher-level form clearly improves the
model.

### 8.1 Core forms

```flow
let x: i32 = 42
let mut count: i32 = 0

function add(a: i32, b: i32) -> i32 {
    return a + b
}

struct Point {
    x: f64,
    y: f64
}
```

Main scalar types include `i32`, `i64`, `f32`, `f64`, `bool`, `string`, and
`void`. Low-level work may use `ptr<T>`. Fixed-size arrays use the supported
array syntax for the chosen host and context.

### 8.2 Make mutation explicit

Use `let mut` for values that change. Do not ask the AI to invent a second
mutation convention.

```flow
let mut position: f64 = 0.0
position = position + velocity * dt
```

### 8.3 Keep interfaces narrow

Ask the AI to:

- give functions one clear purpose;
- make input and output types explicit;
- avoid global mutable state unless an existing runtime interface requires it;
- put low-level native interaction behind a small Flow function;
- use a struct when several values form one stable concept;
- use distinct types when equal runtime representations must not be confused.

### 8.4 Use C interoperability deliberately

Flow’s C target makes native integration practical. Declare only the native
surface that is needed.

```flow
extern {
    function fabs(x: f64) -> f64
}
```

The AI MUST check ABI type mapping, ownership, lifetime, and link flags. It
MUST NOT assume that a parser-accepted extern is correctly linked.

---

## 9. Express evolution as evolution

Flow’s main distinction is that a changing system can be stated directly. The
project’s successful adoption rule is: use the declarative Flow form in the
canonical example, and keep hand-written numerical code only when it teaches
the lowering or a specialised numerical method.

### 9.1 Use a `flow` block for persistent state

```flow
flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}
```

The compiler lowers the declaration to an ordinary representation and step
functions. The caller owns the instance and advances it.

```flow
let mut p: Pendulum = Pendulum_new()
Pendulum_step(&p, 0.001)
```

Important current rules include:

- derivatives read the pre-step state;
- continuous states advance together;
- the caller supplies `dt`, unless a supported solver form provides a default;
- shipped flow members currently have type restrictions;
- supported solver methods and event accuracy have explicit limits;
- generated function names are part of the current lowering contract.

The AI MUST read `docs/vision/north-star.md` and the focused tests before it
changes these rules.

### 9.2 Use events for hybrid systems

```flow
when height reaches 0.0 {
    velocity becomes -restitution * velocity
    height becomes 0.0
}
```

Event assignments are staged and applied together. Current zero-crossing
detection works at step granularity. It does not automatically provide exact
impact time. The AI MUST report this numerical limit when it matters.

### 9.3 Use `every` for supported periodic updates

Periodic behavior can be attached to the flow when the current grammar and
lowering support the body. The AI MUST check current restrictions on which
states may receive `becomes`, which statements are permitted in the body, and
how catch-up behavior works when `dt` is larger than the period.

### 9.4 Prefer namespaced dynamics forms in new code

The dynamics DSL has both older bare forms and newer namespaced forms. New code
SHOULD prefer the namespaced style where the feature document recommends it.
This reduces collisions with ordinary identifiers and helps editor support.

### 9.5 Reuse analysis and library helpers

Past work has been most useful when examples moved from private algorithms to
shared facilities:

- dynamics examples use `flow`, `evolves`, events, portrait helpers, and LQR
  helpers;
- linear algebra tourist examples use BLAS wrappers;
- ML tourist examples use Dual operations or checked-in gradient code
  generation;
- HTTP examples use owned response bodies;
- field examples use shared Laplacian and step helpers;
- graphics examples use shared frame-loop facilities where supported.

Tell the AI to search `lib/stdlib/` and canonical examples before writing a
local helper.

---

## 10. Use algebraic effects to separate needs from providers

Effects are useful when core logic needs an operation but should not know its
implementation. A request to the AI should name both the operation contract
and the handler contexts.

```flow
effect Log {
    info(msg: string) -> void,
}

function do_work() -> void {
    Log.info("work started")
}

capability QuietLog {
    effect Log,
    function info(msg: string) -> void {
    },
}
```

Install a handler for a dynamic scope:

```flow
handle Log with QuietLog {
    do_work()
}
```

Ask the AI to use effects when all these conditions are true:

- the call site should state what it needs;
- production and test behavior should differ;
- dynamic scoping is acceptable;
- the full Python compiler host is available;
- current effect-row and backend limits are understood.

Do not use effects only to make an ordinary pure function look advanced.

The AI SHOULD study `examples/effects/showcase.flow` and
`docs/effects-showcase.md`. That example shows one service running with
production handlers, test handlers, nested replacement, and composed handlers.

---

## 11. Organise modules and packages by logical name

The module rule is simple: imports name modules, not file-system traversal.

Preferred forms include:

```flow ignore="catalogue of import forms over illustrative module names"
import std.math.sin
import verify.nat { nat_zero_add, nat_add_succ }
import .sibling { helper }
export import .model
```

The project map lives in `flow.toml`. Logical roots belong in `[paths]`, and
dependencies belong in `[dependencies]`.

Ask the AI to follow this process:

1. Read the nearest `flow.toml`.
2. Find the existing logical root for the module.
3. Prefer explicit imported symbols.
4. Keep public exports intentional and small.
5. Use re-export only for a deliberate package surface.
6. Test resolution from the real project root.
7. Check Stage-A support separately if the default host must accept the module.

The AI MUST NOT replace a module import with a chain of `../../..` paths merely
to make one local command pass.

### 11.1 Start projects through the CLI

```bash
./flow init my_project
./flow add package_name
./flow pkg install
./flow build
```

Package registry behavior is still developing. Git and path dependencies may
be more appropriate than assuming a complete central registry. The AI MUST
read current package documentation before changing dependency strategy.

---

## 12. Treat generated C as a diagnostic instrument

Generated C is not an unwanted intermediate file. It is evidence about the
compiler.

When a program fails after parsing, ask the AI to inspect the generated C and
answer:

- Is the Flow AST already wrong?
- Is the type information wrong or absent?
- Did lowering produce the wrong ordinary form?
- Is the C expression malformed?
- Is the native declaration or link command incomplete?
- Is the runtime contract being violated?

Use compilation and preservation options that keep the artifact. For the
Python runner, structured execution can keep intermediates:

```bash
python3 -m flow.run program.flow --json --keep build/investigation
```

For ordinary debugging:

```bash
./flow debug program.flow
```

This creates a debug C file and a native debug binary, then uses LLDB or GDB
when available. Source mapping is useful but not statement-perfect. The AI
SHOULD break on the generated C function when the Flow mapping is unclear.

---

# Part IV: Verification and diagnosis

## 13. Use a verification ladder

Run the cheapest useful check first. Expand only after it passes. This reduces
noise and makes the first failure easier to understand.

### 13.1 Program ladder

1. Format or parse the one file.
2. Compile the one file on the required host and backend.
3. Run it with a deterministic input.
4. Check its exit code and invariant.
5. Add it to the appropriate focused test class.
6. Run the related suite.
7. Run a broader suite if shared compiler or runtime code changed.

### 13.2 Compiler ladder

1. Add or run one parser/type-checker/codegen unit test.
2. Inspect the AST or emitted fragment if available.
3. Compile emitted C with strict native warnings.
4. Run a small end-to-end fixture.
5. Add a negative diagnostic case.
6. Run all tests for the touched compiler stage.
7. Run backend parity when shared semantics changed.
8. Run Stage-A roundtrip or self-host checks when `compiler/src/` changed.

### 13.3 Common commands

```bash
./flow test --tier1
./flow test --strict --verbose
./flow test-runtime
./flow test-python
./flow test-mlir
./flow test-gpu
./flow test-all
```

Use a focused path when supported:

```bash
./flow test-runtime tests/runtime/test_arithmetic.flow
PYTHONPATH=src pytest tests/unit/test_specific_area.py -q
```

The AI MUST report what it actually ran. It MUST NOT say “all tests pass” when
it ran only a focused test.

### 13.4 Runtime test contract

A runtime `.flow` test has a simple contract:

- it defines `main() -> i32`;
- it returns `0` on success;
- it returns a non-zero code on failure;
- it may have a matching `.expected` file for exact standard output.

This pattern works well for AI-generated tests. The result is clear and a
machine can check it.

---

## 14. Diagnose from the earliest wrong stage

Do not patch the last visible symptom until the AI finds the first incorrect
stage.

Use this sequence:

```text
source
  -> tokens
  -> AST
  -> resolved names
  -> semantic types and effects
  -> lowered AST or selected plan
  -> generated target text
  -> native compile/link
  -> runtime state and output
```

For each stage, ask one question: “Is the representation correct here?” Stop at
the first “no.” The defect normally belongs at that boundary or immediately
before it.

### 14.1 Classify failures before editing

| Failure class | Typical sign | First place to inspect |
|---|---|---|
| Lexical | unexpected character | lexer and token tests |
| Grammar | expected token / unexpected declaration | parser and grammar tests |
| Resolution | missing or duplicate symbol/module | resolver and `flow.toml` |
| Type | incompatible types, unknown field | type checker and semantic type data |
| Lowering | valid high-level source becomes invalid ordinary form | DSL/flow lowering |
| Code generation | malformed or wrong C/MLIR | target generator |
| Native build | missing symbol, header, framework, library | driver and runtime link list |
| Runtime | crash, wrong result, race, leak | generated code, runtime, sanitizer |
| Numerical | plausible but unstable or inaccurate output | method, step size, invariant, reference data |

### 14.2 Minimise the reproduction

The AI SHOULD reduce a failure to the smallest source that preserves it. A good
compiler fixture normally has:

- one relevant declaration;
- one use of the feature;
- one check of the result;
- no unrelated library;
- a name that states the behavior.

The AI MUST then confirm that the reduced case fails before applying the fix.

### 14.3 Repair the abstraction boundary

Examples:

- If postfix chaining is parsed incorrectly, fix the unified postfix parser;
  do not special-case one ring-buffer example.
- If imported names are absent, fix resolution or export seeding; do not inject
  a global name in code generation.
- If a high-level flow update is sequential but should be simultaneous, fix the
  lowering; do not compensate in one example.
- If native linking omits a runtime object, fix the command assembly shared by
  that mode; do not copy runtime code into generated output.

---

## 15. Apply safety and performance checks in proportion to risk

### 15.1 Safety profiles

Flow can tighten generated C and static restrictions:

```bash
./flow compile program.flow --profile=safety
./flow show-flags --profile=safety --sanitize=ub,asan
```

Safety and flight profiles currently reject recursion and require a maximum
iteration annotation on `while` loops.

```flow
@max_iterations(1000)
while condition {
    step()
}
```

Counted `for` loops are already bounded. The AI SHOULD choose a bound that
comes from the system contract, not a large arbitrary number.

### 15.2 Sanitizers

Use the relevant sanitizer during native execution:

```bash
FLOW_UBSAN=1 ./flow run program.flow
FLOW_ASAN=1 ./flow run program.flow
FLOW_TSAN=1 ./flow run program.flow
```

Or use `--sanitize=ub,asan,tsan` where supported. ThreadSanitizer should be
used for concurrent code, but its environment and toolchain limitations must
be reported.

### 15.3 MISRA and CERT-oriented checks

Inspect compiler flags and scan generated C:

```bash
./flow show-flags --profile=safety
./flow analyze build/program.c --standard=misra-c-2024
./flow analyze build/program.c --standard=cert-c
```

These checks support evidence. They are not by themselves a certification.
WCET output is also an estimate; target hardware measurements are still
required for final timing evidence.

### 15.4 Real-time audio

For audio or other real-time work, instruct the AI to identify the real-time
boundary explicitly. Inside that boundary, it SHOULD avoid allocation,
unbounded work, blocking operations, file or network I/O, and uncontrolled
string construction. It SHOULD use fixed storage and existing audio safety
facilities.

Run the audio commands and tests. An ordinary CPU test is not sufficient:

```bash
FLOW_HOST=python ./flow audio program.flow
FLOW_HOST=python ./flow compile-audio program.flow
```

Read `docs/library/audio-safety.md` and `docs/library/rt-safety.md` before
claiming real-time safety.

### 15.5 Performance work

Performance claims MUST have:

- the benchmark source;
- the exact build command;
- hardware and operating system data;
- warm-up and repetition policy;
- a comparison baseline;
- result units;
- separation of compile time and run time;
- a correctness check before timing.

Use `flow explain` when a declarative selection is unexpectedly slow:

```bash
FLOW_HOST=python ./flow explain program.flow
```

The report shows candidate implementations, applicability, estimated cost,
scratch use, rejection reasons, and the chosen plan. It explains a decision;
it does not replace measurement.

---

# Part V: Extending the language and implementation

## 16. Implement compiler features as vertical slices

A parser-only feature creates misleading progress. A successful Flow feature
passes from source text to observable behavior.

Use this slice checklist:

1. **Decision:** Find the approved syntax and semantics.
2. **Grammar:** Update formal grammar or focused syntax documentation.
3. **Lexer:** Add tokens only when contextual recognition is not sufficient.
4. **AST:** Represent program meaning. Do not store source punctuation alone.
5. **Parser:** Accept valid forms and give clear invalid-form diagnostics.
6. **Resolver:** Bind imported and local names correctly.
7. **Checker:** Enforce type, ownership, effect, and context rules.
8. **Lowering:** Convert the feature to the simplest stable internal form.
9. **Backends:** Implement or explicitly reject each affected backend.
10. **Tools:** Update formatter, LSP, debug data, or explain output when relevant.
11. **Tests:** Add positive, negative, edge, and regression coverage.
12. **Example:** Add one canonical use that checks a real result.
13. **Documentation:** State behavior and limits without future-tense ambiguity.
14. **Self-hosting:** Decide whether Stage-A needs the feature now, later, or
    never.

### 16.1 Use contextual keywords carefully

Many evolution terms are contextual rather than globally reserved. This keeps
ordinary programs that use names such as `state` or `input` from breaking.
When extending such syntax, the AI SHOULD reuse the established lookahead
pattern. It MUST add regression tests proving that the word can still be an
ordinary identifier where allowed.

### 16.2 Lower to existing, well-tested constructs

Flow’s successful additions often lower to ordinary structs, functions, loops,
and calls. This has several benefits:

- every backend can share more behavior;
- generated C remains understandable;
- the runtime stays small;
- existing type and code-generation logic is reused;
- the surface can improve without requiring a new scheduler.

The AI SHOULD prefer this method unless the new feature truly needs a new
runtime semantic.

### 16.3 Make simultaneous semantics explicit

Systems that evolve over time are sensitive to update order. For continuous
state and event resets, the AI MUST identify whether right-hand sides read old
state or already updated state. If updates are simultaneous, lowering SHOULD
store temporary values and commit them together.

Never leave this behavior as an accident of declaration order.

### 16.4 Give unsupported paths a clear failure

If a new form works on C but not MLIR, or on the Python host but not Stage-A,
the AI MUST take one of these actions:

- implement parity;
- reject the unsupported route with a precise message;
- keep the feature out of the shared user surface until parity is ready.

Silent miscompilation is never an acceptable partial implementation.

---

## 17. Preserve self-hosting discipline

The self-hosted compiler is both a tool and a stress test. Changes under
`compiler/src/` need stronger checks than an ordinary Flow example.

### 17.1 Know the bootstrap ladder

The present ladder is:

1. Checked-in bootstrap C can build a compiler with `cc` and no Python.
2. That compiler emits the compiler sources.
3. Later compiler generations emit the same source again.
4. Fixed-point checks compare the generated artifacts.

The key commands are:

```bash
./compiler/scripts/bootstrap_from_c.sh --verify
./compiler/scripts/selfcompile_audit.sh
./compiler/scripts/self_host_full.sh
./compiler/scripts/roundtrip.sh
```

After an intentional compiler-source change, bootstrap C may require
regeneration through the documented script. The AI MUST inspect the relevant
script and current diff first. It MUST NOT hand-edit a large generated
bootstrap artifact unless the workflow explicitly requires that action.

### 17.2 Require fixed-point evidence

Success requires agreement between successive generations under the defined
comparison. A compiler that only compiles itself is not enough. Ask the AI to
report:

- which generations were built;
- which artifacts were compared;
- whether compiler self-tests passed;
- whether a normal program compiled and ran under the generated compiler;
- whether any step used the Python escape hatch.

### 17.3 Keep the subset honest

Stage-A deliberately lacks much of the full Python-host surface. The AI SHOULD
add only what self-hosting or approved user goals require. It MUST update the
Stage-A support table when behavior changes. It MUST avoid describing partial
name checking as a complete semantic type system.

---

## 18. Extend backends without splitting language meaning

### 18.1 C backend

Use C as the semantic reference for portable CPU work, but do not make C
syntax leak into the Flow surface without need. Test generated C with the
project’s normal C standard and warnings. Preserve ABI behavior and runtime
link lists.

### 18.2 MLIR backend

When adding MLIR support, inspect both the emitted dialects and the complete
lowering pipeline. A fragment that parses as MLIR may still fail later during
conversion to LLVM IR. Add end-to-end `mlir-run` coverage when the tools are
available.

### 18.3 GPU routes

Flow has several GPU-related routes with different maturity:

- Metal is the main macOS compute and shader route;
- WGSL produces WebGPU-oriented output;
- MLIR GPU to SPIR-V provides an emit route;
- some SPIR-V execution support depends on external loaders or platform work.

The AI MUST name the exact route. “GPU support” is too broad to be a useful
verification claim.

### 18.4 WebAssembly

WebAssembly can use C or MLIR before Emscripten. Browser facilities need
explicit crossings and stubs. Use:

```bash
FLOW_HOST=python ./flow wasm program.flow --backend=c --out build/wasm
```

Add only the required preloaded directory, linked object, threading mode, or
file-system mode. Verify the generated page or module in a real browser path
when browser behavior is part of the task.

### 18.5 Graphics

Use the high-level command that assembles the correct runtime:

```bash
FLOW_HOST=python ./flow gfx program.flow
```

For deterministic visual evidence, use the headless recorder:

```bash
FLOW_HOST=python ./flow record program.flow --frames 120 --out build/frames
```

The AI SHOULD also add non-visual checks for model state, layout, collision,
or other logic. Screenshots and GIFs are useful evidence, but they are not the
only evidence.

---

# Part VI: Methods that have worked

## 19. Use adoption before invention

One of the clearest lessons in the repository is “adoption first; new sugar
second.” When a good feature already exists but examples bypass it, the first
task is to route canonical examples through it.

The method works for these reasons:

- tests the real feature under realistic load;
- reveals ergonomic problems with evidence;
- reduces duplicate local algorithms;
- makes user documentation truthful;
- delays syntax expansion until a concrete need exists.

Instruction to the AI:

```text
Before proposing new syntax, find whether the requested result can be stated
with a current Flow construct or standard-library helper. If it can, build the
canonical example with that facility and record any remaining friction. Propose
new syntax only for friction that is repeated, measured, and not solved by a
small library interface.
```

## 20. Grow the seed; do not fork the language

Flow has grown specialised behavior by lowering it into the existing language
and backend pipeline. This is more reliable than building a second execution
model beside the first one.

Apply this rule:

- make a `flow` behave like a struct plus generated operations;
- make a declarative analysis form generate ordinary Flow calls;
- make selection plans use shared facts and a common selector;
- make package surfaces use the existing module system;
- make native integrations cross a small ABI boundary;
- migrate experimental expansion into the AST only when lasting semantic
  checking requires it.

The AI SHOULD name the internal form that a new surface will lower to before
implementation begins.

## 21. Build narrow, complete increments

Successful work in this repository often closes one precise gap and proves it
end to end. Examples include adding one postfix chain behavior, one import
resolution rule, one Stage-A expression form, or one supported dynamics
surface with a focused fixture.

Use this unit of work:

```text
one semantic rule
+ one valid fixture
+ one invalid or boundary fixture
+ one complete target path
+ one focused document update
```

Avoid combining several new grammar families, a backend rewrite, and a large
example migration in one patch.

## 22. Make failures loud

The self-hosting work records this rule: output that fails loudly is
safer than output that compiles with the wrong meaning. Apply it across Flow.

The AI MUST prefer:

- a parser diagnostic over ambiguous recovery;
- a type error over an invented default type;
- a backend “not supported” message over silently dropped behavior;
- a runtime failure code over a plausible but unchecked printout;
- a failed fixed-point comparison over updating the expected artifact without
  investigation.

## 23. Use differential evidence

When a fix affects a large corpus, count behavior before and after. The
repository has used pass-set comparison to show that a parser or resolver
change recovered intended files with zero unrelated regressions.

Ask the AI to record:

```text
Before: passing set, failing set, and failure classes.
After: passing set, failing set, and failure classes.
Difference: newly passing, newly failing, and changed diagnostics.
```

This is stronger than reporting only a new total.

## 24. Keep design questions in durable files

AI sessions lose context. Flow uses repository files to carry decisions across
sessions. When a question changes semantics and cannot be answered from current
authority, the AI SHOULD prepare:

- context;
- two or three real options;
- advantages and costs;
- a recommendation;
- the specific work blocked by the decision.

The human decides. The final decision then belongs in the relevant design file,
question log, test, or specification. A decision that lives only in chat will
be rediscovered and may be reversed accidentally.

## 25. Use explainability as a feature

Declarative source lets the compiler choose an implementation. That choice
must remain inspectable. Flow’s plan selector records each candidate, its
constraints, estimated cost, scratch use, rejection reason, and winner.

Use the same principle for new adaptive systems:

1. State all facts given to the selector.
2. List all candidates.
3. Give a sentence for every rejection.
4. Give comparable cost units.
5. State resource budgets.
6. State why the winner beat the next valid candidate.
7. Keep estimates clearly separate from measurements.

An AI can generate complex selection code easily. Requiring an explanation
makes that code reviewable.

## 26. Make examples scientific, not decorative

A Flow example SHOULD have five parts:

1. A model or algorithm stated in the most direct Flow form.
2. A small driver that exercises it.
3. A quantity that can be measured.
4. A relation or invariant that should hold.
5. A non-zero exit when the relation fails.

For a visual example, add recorded frames. For a numerical example, print a
small table. For a performance example, add a reproducible benchmark. The
program should still be able to say “wrong” without a person judging the
picture.

---

# Part VII: Common failure patterns

## 27. Do not trust the first nearby document

Problem: an AI finds a design document and implements planned behavior as if it
were shipped.

Correction:

1. Find the status label.
2. Find the implementation symbol.
3. Find a focused test.
4. Run the current command.
5. State the verified limit.

## 28. Do not use the wrong compiler host

Problem: a declarative or effect example fails under default Stage-A, and the
AI rewrites it into lower-level code.

Correction: rerun on `FLOW_HOST=python`, then decide whether Stage-A parity is
actually in scope. Do not remove useful language features to satisfy the wrong
route.

## 29. Do not patch only generated output

Problem: emitted C is wrong, so the AI edits the generated file or inserts a
one-off string replacement.

Correction: identify the incorrect AST, lowering, type, or generator rule.
Repair that rule and regenerate the artifact.

## 30. Do not add syntax to remove one repeated line

Problem: a single example has ceremony, so the AI creates a new grammar form.

Correction: try a library function, helper, convention, or targeted lowering.
Collect evidence from several uses before expanding syntax.

## 31. Do not confuse compilation with correctness

Problem: the file compiles and prints values, so the AI calls the task complete.

Correction: check the values against an invariant, reference implementation,
or expected output. Return non-zero on failure.

## 32. Do not hide unsupported parity

Problem: a feature works on one backend, while other routes ignore it.

Correction: add parity, add explicit rejection, or narrow the documented scope.

## 33. Do not make broad unrelated cleanup

Problem: a focused task produces formatting, renaming, file movement, and
dependency changes across the repository.

Correction: preserve the requested semantic diff. Put mechanical cleanup in a
separate task with behavior-preserving evidence.

## 34. Do not use AI consensus as design authority

Multiple AI views can reveal risks and dependencies. They cannot decide human
product intent. Weighted votes are input to a decision, not the decision.
Use human authority for syntax, public meaning, priorities, and acceptable
trade-offs.

---

# Part VIII: Reusable operating procedures

## 35. Procedure: create a new Flow example

1. Select the correct example domain.
2. Read `examples/README.md` and the nearest canonical example.
3. Decide Stage-A or Python host.
4. Decide command mode and backend.
5. Reuse the standard library and declarative surface.
6. Write the smallest complete program.
7. Add a measurable result and invariant.
8. Return non-zero on failure.
9. Run the exact advertised command.
10. Add it to the example index or status system if required.
11. Run the example verifier or related tests.
12. Document limitations in the file header.

Prompt:

```text
Create one canonical Flow example for [concept]. Inspect neighboring examples
and the standard library first. Use the current preferred surface. The example
must run with [exact route], measure [quantity], verify [invariant], and return
non-zero on failure. Add only the focused index or status update required for
discovery.
```

## 36. Procedure: fix a compiler defect

1. Record the exact failing command and output.
2. Reduce the source to a focused fixture.
3. Confirm the fixture fails.
4. Locate the earliest incorrect stage.
5. Find adjacent behavior that must remain unchanged.
6. Add the failing test before or with the fix.
7. Make the smallest rule-level change.
8. Inspect emitted output.
9. Run the fixture end to end.
10. Run the focused stage suite.
11. Run broader regression or parity checks based on risk.
12. Report remaining unsupported cases.

## 37. Procedure: add a language construct

1. Confirm human approval of syntax and meaning.
2. Write examples of valid and invalid source.
3. Decide whether words are contextual or reserved.
4. Define the AST meaning.
5. Define name, type, effect, update-order, and lifetime rules.
6. Define the lowering or runtime behavior.
7. Define host and backend support.
8. Implement one vertical slice.
9. Add formatter and editor behavior when the construct affects them.
10. Add positive, negative, nesting, and interaction tests.
11. Add one canonical example with an invariant.
12. Update specification and status documents.
13. Run the full risk-based verification ladder.

## 38. Procedure: investigate a backend mismatch

1. Run the same minimal program on C and the target backend.
2. Record result, output, exit status, and tool versions.
3. Compare semantic AST and lowering inputs.
4. Inspect both generated targets.
5. Separate unsupported feature from incorrect implementation.
6. Add a parity test for shared semantics.
7. Repair the first divergent rule.
8. Run backend-specific verification tools.
9. Run the program on both routes again.

## 39. Procedure: improve performance

1. Prove correctness before timing.
2. Run `flow explain` for declarative selection sites.
3. Inspect generated C or MLIR.
4. Measure the current version with a written method.
5. Form one performance hypothesis.
6. Change one relevant factor.
7. Measure again with the same method.
8. Check code size, memory, scratch, and latency effects.
9. Run correctness and sanitizer checks again.
10. Publish method and raw result data with the conclusion.

## 40. Procedure: close an AI work session

The AI SHOULD return this handoff:

```text
Outcome:
Files changed:
Behavior changed:
Compiler host and backend used:
Verification run and exact results:
Generated or measured artifacts:
Known limits:
Unrelated existing changes preserved:
Recommended next action, if any:
```

The final report MUST be accurate even if some checks could not run. A blocked
tool is a reported limit, not a passing result.

---

# Part IX: Prompt library

## 41. General implementation prompt

```text
Work in the current Flow repository. First inspect local instructions, git
status, the nearest working example, and the nearest focused test. Preserve all
unrelated changes.

Goal: [goal]
Reason: [reason]
Scope: [included work]
Not in scope: [excluded work]
Required route: [FLOW_HOST, backend, command mode]
Done when: [observable behavior and tests]

Use current Flow patterns and standard-library facilities before creating new
ones. If a language or architecture choice is not already decided, stop that
part and present concrete options. Implement in a small vertical slice. Verify
the exact user path, then run risk-based regressions. Return exact commands and
results.
```

## 42. Program-generation prompt

```text
Write a Flow program for [system]. Use simplified, readable Flow and explicit
types. Prefer a `flow` declaration when the central concept is state evolving
through time. Prefer existing stdlib helpers over private algorithms. Use
[host/backend]. Include deterministic input, measured output, a correctness
invariant, and non-zero failure exits. Run it and report the command and result.
```

## 43. Numerical-model prompt

```text
Implement [model] in Flow from these equations and parameters: [data]. State
units, initial conditions, solver method, step size, duration, and event rules.
Use the current declarative evolution surface where supported. Compare at least
one measured quantity with theory or a reference. Identify numerical error and
stability limits. The program must fail when the invariant is outside the
defined tolerance.
```

## 44. Compiler-feature prompt

```text
Add [feature] to Flow. The approved syntax is [syntax], and the semantics are
[rules]. Cover the full vertical slice: parsing, AST, resolution/type checks,
lowering/code generation, diagnostics, focused tests, one checked example, and
documentation. State support for flowc versus Python and C versus MLIR/other
affected backends. Unsupported routes must fail clearly. Do not expand the
syntax or semantics beyond the approved rules.
```

## 45. Audit prompt

```text
Audit [feature or claim] without editing. Determine what is shipped, limited,
parsed only, designed, or planned. Use tests and runnable examples as the
strongest evidence. Give exact file references and commands. Identify stale or
conflicting documents. End with the smallest high-value correction, but do not
make it until asked.
```

## 46. Documentation prompt

```text
Update the Flow documentation for [behavior]. Verify every command and example
against the current implementation. Use simplified technical English. Lead
with instructions and operational limits. Link to canonical details instead of
duplicating long specifications. Do not describe planned behavior as shipped.
Run the documentation link or example checks relevant to the edited files.
```

---

# Part X: Reference

## 47. Command map

| Goal | Command |
|---|---|
| Show version | `./flow version` |
| Show command help | `./flow help` |
| Run Stage-A core | `./flow run file.flow` |
| Run full surface | `FLOW_HOST=python ./flow run file.flow` |
| Compile only | `./flow compile file.flow` |
| Use MLIR CPU | `FLOW_HOST=python ./flow run file.flow --backend=mlir` |
| Emit MLIR | `FLOW_HOST=python ./flow mlir file.flow` |
| JIT | `FLOW_HOST=python ./flow jit file.flow` |
| Explain a plan | `FLOW_HOST=python ./flow explain file.flow` |
| Format | `./flow fmt file.flow` |
| Debug | `./flow debug file.flow` |
| Run graphics | `FLOW_HOST=python ./flow gfx file.flow` |
| Record graphics | `FLOW_HOST=python ./flow record file.flow --frames 120 --out build/frames` |
| Run audio | `FLOW_HOST=python ./flow audio file.flow` |
| Build WASM | `FLOW_HOST=python ./flow wasm file.flow --backend=c --out build/wasm` |
| Focused Flow tests | `./flow test --strict --verbose` |
| Runtime tests | `./flow test-runtime` |
| Python unit tests | `./flow test-python` |
| MLIR tests | `./flow test-mlir` |
| GPU tests | `./flow test-gpu` |
| All main tests | `./flow test-all` |
| Safety flags | `./flow show-flags --profile=safety` |
| MISRA scan | `./flow analyze build/file.c --standard=misra-c-2024` |
| Create project | `./flow init name` |
| Install project packages | `./flow pkg install` |
| Build project | `./flow build` |

Always confirm the current form with `./flow help`. This table is a starting
point, not a replacement for the executable help.

## 48. Repository map

| Path | Use |
|---|---|
| `flow` | Main command driver |
| `flow.toml` | Root project and path configuration |
| `src/flow/` | Full Python compiler and tooling |
| `compiler/src/` | Self-hosted Stage-A compiler in Flow |
| `compiler/bootstrap/` | Checked-in C bootstrap |
| `runtime/` | Native runtime support |
| `lib/stdlib/` | Standard library modules |
| `examples/` | Domain examples and canonical demonstrations |
| `tests/unit/` | Python-level compiler tests |
| `tests/runtime/` | Compile-and-run Flow tests |
| `tests/integration/` | Cross-component checks |
| `tests/benchmarks/` | Benchmark sources and results |
| `docs/language/` | Focused language documents |
| `docs/library/` | Standard-library documents |
| `docs/project/` | Architecture, maturity, process, and project state |
| `docs/vision/` | Evolution-language direction and grammar mapping |
| `scripts/` | Verification, generation, publishing, and maintenance tools |

## 49. Completion checklist

Before accepting AI work, check:

- [ ] The result matches the stated goal.
- [ ] The patch does not include unrelated changes.
- [ ] The compiler host is named.
- [ ] The backend and command mode are named.
- [ ] The source uses current preferred Flow patterns.
- [ ] Existing helpers were considered before new helpers were added.
- [ ] Valid behavior has a focused test.
- [ ] Invalid or edge behavior has a test where relevant.
- [ ] Runtime behavior checks an invariant or expected output.
- [ ] Generated target output was inspected when compiler code changed.
- [ ] Relevant regression tests ran.
- [ ] Unsupported paths fail clearly or are documented.
- [ ] Estimates and measurements are labelled correctly.
- [ ] Documentation states current behavior and current limits.
- [ ] Exact commands and results are in the handoff.
- [ ] Existing human work in the worktree was preserved.

# Part XI: Coverage audit

## 50. How completeness is defined

This part is the coverage ledger for the handbook. “Every feature” means every
user-facing feature family that can be found in these sources
at this edition’s repository baseline:

- executable `./flow help` and the command dispatch in `flow`;
- the language specification and its implementation matrix;
- focused language and library documents;
- the standard-library module tree;
- compiler, runtime, example, test, and tool directories;
- `VISION.md`, `ROADMAP.md`, `docs/NEXT.md`, and `Questions.md`;
- the AI collaboration rules in `CONTRIBUTING.md`.

This definition does not mean that every standard-library function receives a
full API entry here. The generated standard-library reference already provides
that function-by-function detail. This handbook names every module and feature
family, gives its operating rule, and directs the AI to the authoritative API.

Use these status words throughout this part:

| Status | Meaning |
|---|---|
| **Shipped** | Implemented on at least one stated route and supported by current evidence |
| **Limited** | Implemented with important host, backend, grammar, or semantic restrictions |
| **Experimental** | Present for evaluation; not a stable production contract |
| **Parsed** | Source is recognized, but operational behavior is incomplete |
| **Designed** | Semantics or architecture are described but not fully implemented |
| **Planned** | Named as future work; details may still require human authority |
| **External** | Requires a native tool, library, platform, or third-party package |

The AI MUST attach a route to a status. For example, “closures are shipped on
the C backend and unsupported by MLIR” is useful. “Closures are supported” is
not complete enough.

### 50.1 Coverage rule for future versions

At the start of a new edition, the AI MUST diff these inventories:

```bash
./flow help
rg -n '^#{1,4} ' docs/LANGUAGE_SPEC.md docs/language docs/library
find lib/stdlib -type f -name '*.flow' | sort
find examples -type f -name '*.flow' | sort
find tests -type f | sort
rg -n '🔲|partial|^- \[ \]' ROADMAP.md docs/NEXT.md Questions.md
```

Any new command, module, status row, or open decision must either be added to
this ledger or explicitly declared internal.

---

## 51. Core-language reference

### 51.1 Lexical forms

| Family | Forms | Status and AI rule |
|---|---|---|
| Comments | `#` to end of line | Shipped. C `//` and block comments are not Flow comments. |
| Integers | decimal, negative, hexadecimal | Shipped. Binary `0b...` is not lexed. |
| Floats | decimal and exponent forms | Shipped. Check target precision and NaN behavior. |
| Strings | quoted strings with escapes | Shipped. Treat ownership and concatenation lifetime explicitly. |
| Booleans | `true`, `false` | Shipped. |
| Null | `null` | Shipped for pointer use. Do not treat it as an option value. |
| Arrays | `[a, b, c]` | Shipped. Length and element type are checked by context. |
| Struct values | `Type { field: value }` | Shipped. Use named fields. |
| Duration literals | `ns`, `us`, `ms`, `s`, `min` in supported flow positions | Limited contextual surface; verify the exact grammar position. |
| Quantity literals | RF and unit-related forms in focused modules | Limited; check current parser and type rules. |
| Claim coordinates | `«carrier» «structure» «law»` | Limited verification surface; legacy claim paths still exist. |

### 51.2 Operators

| Family | Forms | Rule |
|---|---|---|
| Arithmetic | `+ - * / %` | Check integer overflow, division, units, and overloaded Dual/Tensor cases. |
| Comparison | `== != < > <= >=` | Normal float comparison uses IEEE behavior; NaN is unordered. |
| Logical | `&& || !` and `and or not` | Short-circuit behavior must be tested on each affected backend. |
| Bitwise | `& \| ^ ~ << >>` | Shipped. Safety checking covers invalid literal shifts; signed rules still need care. |
| Assignment | `=` and supported compound forms | Mutation requires a mutable binding or valid mutable target. |
| Range | `to` and `..`; optional `step` | `to` is preferred. Test negative and non-unit steps. |
| Pipeline | `|>` with optional `_` placeholder | Shipped on the Python host; used by ordering and DSP pipelines. |
| Address/pointer | unary `&` and `*` | Shipped mainly on C; inspect ABI and lifetime. |
| Access | `.`, `[]`, postfix chains | Shipped; includes forms such as `ptr[0].field`. |
| Arrows | `->`, `=>` | Return/function types and match arms. |
| Effect scope | `::` where supported | Used by effect operations; prefer the syntax in current examples. |
| Cast | `as` | Explicit conversion, including distinct types and unit literals. |

### 51.3 Keywords and declarations

The list covers the keyword families in the specification.

| Family | Keywords/forms | Status and use |
|---|---|---|
| Functions | `function`, `return` | Shipped. Parameters and return types are static. |
| Bindings | `let`, `mut`, `const` | Shipped. Top-level mutable `let` creates a restricted module static. |
| Records | `struct` | Shipped. Value semantics are the default. |
| Algebraic data | `enum` | Limited across C and MLIR. Use focused tests for variants and payloads. |
| Interfaces | `trait`, `impl` | Limited backend surface. Confirm method resolution and codegen. |
| Type naming | `type`, `distinct` | Transparent alias versus nominal boundary. |
| FFI | `extern` and optional ABI string | Shipped on C. Linkage is a separate required check. |
| Modules | `import`, `export`, `module` | Imports/exports ship; `module` blocks are flattened, not namespaces. |
| Branching | `if`, `elif`, `else` | Statements and shipped if-expressions. |
| Loops | `while`, `for`, `in`, `to`, `step`, `parallel` | Parallel uses OpenMP when available and serial fallback otherwise. |
| Loop control | `break`, `continue` | Shipped, with a known C mismatch for `break` inside a match inside a loop. |
| Cleanup | `defer` | Shipped. Verify scope-exit order and early returns on each backend. |
| Pattern matching | `match`, `default` | Limited but broad: literals, structs, guards, alternatives, and exhaustiveness for bool/enums. |
| Effects | `effect`, `capability`, `handle`, `with` | Shipped on C; MLIR parity remains limited. |
| Debug/test helpers | `dbg`, `expect`, `test` | C has behavior; MLIR evaluates only; `test` blocks are not automatically run. |
| Codegen hints | `inline`, `noinline`, `always_inline`, `target` | C attributes; they guide code generation and do not change semantics. |
| Verification | `theorem`, `assume`, `therefore` | Limited/third-party verification route; corpus is ahead of the checker. |
| Units | `unit` | Shipped on C with dimensional checking and runtime erasure. |
| Evolution | contextual `flow`, `state`, `input`, `output`, `param`, `evolves`, `becomes`, `every`, `when`, `reaches`, `solver`, `represent` | Shipped in defined slices; read the north-star status before use. |
| UI layout | `ui_layout`, `ui_row`, `ui_column`, `ui_stack`, `ui_grid` | Parsed and host-dependent; use its snapshots and demo commands. |

### 51.3.1 Attribute vocabulary

| Attribute family | Forms | Purpose and status |
|---|---|---|
| Build mode | `@only(...)`, `@guard(...)`, `@compile`, `@jit`, `@hot`, `@interp`, `@mlir`, `@c` | Include a function only in selected compiler modes. |
| Native codegen | `@inline`, `@noinline`, `@always_inline`, `@target(...)` | Guide the C compiler; target validity is finally decided by the native compiler. |
| GPU | `@gpu`, supported `@workgroup_size(...)`, shader `@binding` and `@builtin` forms | Select device/shader behavior on the relevant GPU path. |
| Real-time | `@rt_safe` | Reject direct or transitive calls to the currently forbidden allocation set. |
| Safety boundary | `@safe`, `@unsafe` | Mark certified versus escaped operations; safety-profile extern use requires explicit care. |
| Stable ABI | `@flow_api` | Preserve a plain exported C name. |
| Lifetime | `@lifetime(callback|frame|session|application)` | Apply lifetime-domain checking. |
| Loop bound | `@max_iterations(N)` before supported while loops | Required by safety/flight profiles. |
| Internal compiler | `@test`, synthesized `@monomorphized` | Compiler metadata; not a general user optimisation control. |
| Selection proposals | `@require(...)`, `@prefer(...)` | Documented target surface; not fully wired into ordinary source compilation. |

Tags such as `@module`, `@means`, `@from`, `@tier`, `@needs`, and `@docs`
inside comment headers are documentation/provenance metadata, not ordinary
function attributes. Proposed Python export annotations are also not shipped.

### 51.4 Primitive and composite types

| Family | Types | Important limits |
|---|---|---|
| Signed integers | `i8 i16 i32 i64 i128` | C supports `i128` through `__int128`; target and MLIR parity differ. |
| Unsigned integers | `u8 u16 u32 u64 u128` | `u128` is unsupported in MLIR. |
| Floats | `f32 f64` | Arithmetic comparison and total ordering are intentionally different. |
| Complex | `c64 c128` | C99 complex operations and selected built-ins; verify backend parity. |
| Other scalars | `bool void string` | Strings are pointer-backed and need lifetime discipline. |
| Dynamic arrays | `array<T>` | Check the exact allocation and runtime helper used. |
| Fixed arrays | `array<T, N>` and supported bracket notation | Strongest portable container for bounded and real-time work. |
| Pointers | `ptr<T>`, `ptr<void>` | Low-level interop; no general borrow checker. |
| SIMD vectors | `vec<T, N>` | Limited parsing/codegen; do not assume arbitrary lanes or operations. |
| Spans | `span<T>`, `&[T]`, mutable and static-extent forms | Concrete element types ship on C; MLIR and inferred/trait-shaped spans do not. |
| Structs | named aggregates | Shipped across main CPU backends with some layout/ABI differences to test. |
| Function types | `(A, B) -> R` | Used for non-capturing functions and closure fat pointers on C. |
| Aliases | `type Name = T` | Transparent. |
| Distinct types | `distinct type Name = T` | Nominal; cross the boundary with explicit `as`. |
| Units | base and derived unit types | C only in the current matrix; erased after checking. |
| RF types | IQ aliases, IQ samples, rate-typed signals | Library/domain surface; inspect `rf.flow` and RF examples. |
| AD/ML types | Dual, Tensor, neural-network records | Operator support is route-dependent; compiler `loss.grad` is not shipped. |

### 51.5 Functions and callable forms

The AI must account for all of these callable behaviors:

- typed parameters and returns;
- omitted return type for `void` where accepted;
- early returns;
- recursion and mutual recursion;
- generic functions and generic structs through monomorphization;
- methods and receiver calls where implemented;
- trait implementations and enum-associated behavior where implemented;
- non-capturing lambdas as function pointers;
- capturing closures with snapshot-by-value environments on the C backend;
- escaping closure environments allocated for the required lifetime;
- C function-pointer call-through via the documented ABI helper;
- variadic C extern functions such as `printf`;
- build-mode guards: `@only`, `@guard`, and `@compile`;
- stable C export names through `@flow_api` and export-ABI tooling.

The safety and flight profiles reject recursion. An AI writing portable or
safety-oriented code SHOULD prefer counted loops to recursion.

### 51.6 Pattern matching and algebraic data

Match support includes literal patterns, boolean patterns, enum/variant paths,
struct patterns, nested literal fields, guards, alternatives using `|`, binding
patterns, wildcard/default behavior, and exhaustiveness checks for booleans and
enums. Integer exhaustiveness is not a complete proof.

Known critical limit: on the C backend, `break` inside a match arm becomes a C
`switch` break and can leave the switch instead of the enclosing loop. MLIR
branches to the intended loop exit. The AI MUST avoid or explicitly test this
shape until parity is fixed.

---

## 52. Memory, lifetime, error, and ABI reference

### 52.1 Storage models

| Model | Use | AI responsibility |
|---|---|---|
| Stack values | Local scalars, structs, fixed arrays | Check size and recursion depth. |
| C heap | `malloc`, `calloc`, `realloc`, `free` wrappers | Pair ownership and release on every path. |
| Typed allocation helpers | Typed buffers from memory modules | Use matching free function and element count. |
| Arena | Bulk allocations with one reset/destroy | Ensure no value escapes the arena lifetime. |
| Frame arena | Per-frame temporary storage | Reset once per frame after all borrowers finish. |
| Temp arena | Compiler/runtime string and closure support | Process-lifetime cleanup; avoid repeated long-lived concat in servers. |
| GPU buffers | shared/unified or private device memory | Probe availability, copy/sync explicitly, and free. |
| Module statics | restricted primitives, fixed arrays, null pointers | C backend only; initializer must be compile-time constant. |
| Runtime task/fiber storage | concurrency runtime | Use the owning concurrency API; do not expose backing storage. |

### 52.2 Pointers, spans, and lifetime domains

Pointers allow address-of, dereference, indexing, field chaining, null, and C
interop. They do not provide Rust-style ownership checking.

Spans are borrowed views over contiguous storage. They provide immutable,
mutable, and static-extent forms. A span does not own storage. The AI MUST keep
the owner alive, respect mutability, and check the current lowering. Inferred
bare spans and dependent/trait-shaped extents are not shipped.

Lifetime domains use `@lifetime(callback|frame|session|application)` and enforce
four current rules:

1. a shorter-lived value may not enter a longer-lived static;
2. a function may not return a reference into its own shorter domain;
3. allocation must follow the domain discipline;
4. calls may not violate the declared domain order.

The domains are annotation-based in the current version. `domain {}` block
sugar is future work.

### 52.3 Error and assertion forms

Use the appropriate layer:

- return a status or `Result_*` for expected operational failure;
- use `Option_*` for possible absence;
- use `expect condition` for a C-backend aborting development assertion;
- use non-zero `main` exits for runtime tests and examples;
- use exact diagnostics for invalid source tests;
- use sanitizer failures for memory, undefined behavior, and races;
- use audio safety meters and guards for signal failures;
- use capability/effect handlers when the failure policy must be replaceable.

`test "name" {}` currently creates a boolean function but does not arrange to
run it. Do not rely on it as the main test harness.

### 52.4 C, native, and exported ABI

The native surface includes:

- `extern` declarations and variadic externs;
- C header import/parsing support and `@cImport` on relevant routes;
- C function-pointer call-through;
- `@flow_api` and generated aliases for stable exported names;
- `--export-abi` and related C/WASM export support;
- native project sources and system libraries from `flow.toml`;
- `build-native` and `run-native` package workflows;
- generated ABI bindings through `scripts/gen_abi_bindings.py`;
- Python extension/wheel generation through the C backend;
- WebAssembly exports and Emscripten-visible aliases.

For every ABI task, the AI MUST record name mangling, calling convention,
integer width, struct layout, pointer ownership, string encoding, library
flags, and the target platform.

---

## 53. Control, concurrency, and composition reference

### 53.1 Ordinary control flow

Flow supplies if/elif/else statements, if-expressions, while loops, counted for
loops with range aliases and steps, parallel for, return, break, continue,
defer, match, expression statements, assignment, and nested blocks.

Safety work MUST prefer bounded `for` loops. A safety-profile `while` requires
`@max_iterations(N)`. The bound is enforced by a runtime counter.

### 53.2 Pipelines

`value |> f(args)` inserts the value as the first argument. `_` selects another
argument position. Chains are left-associative. Pipelines support ordinary
functions, named functions, compatible lambdas, DSP helpers, declarative sort,
and declarative search.

The compiler can fuse adjacent supported operations:

- `map_f32` and `map_f64` composition;
- adjacent `scale_f32` or `scale_f64` by multiplying scale factors;
- adjacent `offset_f32` or `offset_f64` by adding offsets.

This removes an intermediate buffer for recognized AST shapes. The AI MUST
measure the result and confirm the fusion pass actually saw the expected
shape.

### 53.3 Algebraic effects

Effects declare operations. Capabilities implement them. `handle` installs a
handler for a dynamic scope. Handlers may compose and may use other effects.
Signature effect rows can declare required effects and support stricter
checking.

Operational limits:

- C has the broadest effect implementation;
- MLIR support is partial;
- strict effect checking is enabled by the relevant flags/environment;
- unhandled operations may use defaults unless strict behavior is requested;
- capability implementations are currently stateless; pass explicit state
  where required.

### 53.4 Threads and synchronization

The concurrency library covers:

- OS threads;
- mutexes and condition variables;
- read/write locks;
- spin locks;
- once initialization;
- wait groups;
- atomics;
- buffered channels and select forms where implemented;
- parallel loops through OpenMP with serial fallback;
- fibers, fiber async, and runtime task storage;
- network polling support;
- C-channel and concurrency runtime variants.

The AI MUST verify which channel type has working send/receive operations.
Some roadmap text still notes a missing high-level `Channel_i32` pipeline even
though lower runtime/channel demonstrations exist.

### 53.5 Async through effects

Flow does not require `async` and `await` keywords. The `Async` and `AsyncIO`
effects let a call site use interchangeable capabilities such as simulated,
blocking, threaded, fiber, and netpoll implementations.

Use the capability that matches the evidence goal:

| Capability class | Best use |
|---|---|
| Simulated | deterministic unit tests and logical time |
| Blocking I/O | simplest functional reference |
| Threaded | OS-thread concurrency and blocking work isolation |
| Fiber | cooperative tasks and lower scheduling cost |
| Netpoll | socket readiness and many-connection experiments |

Resumable continuation semantics and full cross-platform epoll/kqueue/IOCP
coverage remain limited. Never infer non-blocking behavior from the word
“async”; inspect the installed handler.

---

## 54. Declarative and domain-language reference

### 54.1 Evolution blocks

A `flow` may declare states, inputs, outputs, parameters, derivative equations,
periodic updates, zero-crossing events, solver settings, and representations.
The shipped lowering produces a struct plus constructors, derivative helpers,
step functions, outputs, and bookkeeping.

Current ordering is significant and defined: continuous integration, due
periodic work, events/resets, output maps, and supported checks. Derivatives
and synchronous reset right-hand sides read a common pre-update state.

Current limitations include solver-method coverage, member-type restrictions,
event time resolution, body-statement restrictions, and incomplete constraints
and connection forms. The AI MUST take exact status from the north-star card
table and focused tests.

### 54.2 Dynamics and control DSL

The dynamics surface includes:

- `dsys` system declaration;
- named analysis `horizon`;
- `sense` open-loop analysis;
- `ga evolve` gain search;
- `closed` closed-loop certification;
- `analyze` unified reporting and LQR forms;
- namespaced `dyn.` and `dynamics {}` spellings;
- plant stepping and selected `connect` composition;
- controllability, observability/Gramians, spectral measures, LQR, GA, and
  state-space library operations;
- experimental WFC/GA coupled forms.

These forms use a mix of pre-parse expansion and ordinary Flow libraries.
MLIR support is not general. State dimensions and scratch arrays have stated
caps in several helpers.

### 54.3 Field and PDE surface

The field DSL recognizes field declarations, one-dimensional domains,
`laplacian`, boundary conditions, and generated Euler step helpers. Shared PDE
library operations include a 1D Laplacian and heat step. Two-dimensional and
general mesh forms are later work.

### 54.4 Ordering, search, and multi-implementation selection

The shipped ordering intent includes:

- ascending and descending sort;
- scalar, string, single-key, and multi-key struct ordering;
- stability policies;
- adaptive and general policies;
- in-place `unique` prefix compaction with stale fixed-size tail;
- `find` returning the first index or `-1`;
- parsed entropy, parallel, GPU, SIMD, and other policies that are not all
  specialized.

Float ordering uses IEEE 754 `totalOrder`; ordinary float operators keep IEEE
comparison. The sort selector has six plans: already ordered, reverse in
place, counting, insertion, natural merge, and bottom-up merge. Search has
binary and linear plans. Facts come from type ranges and conservative ordering
provenance. Compiler scratch is capped at 256 KiB for these plans.

General plan selection also models naive versus blocked matrix multiplication
and sequential versus parallel-tree reduction. Hard memory/scratch/latency
constraints and soft preferences are partly implemented programmatically;
the proposed attribute surface is not fully wired. Only `prefer(parallel)`
currently affects cost among the documented soft preferences.

### 54.5 Shaders, GPU simulation, graphics, UI, and 3D

The visual surface includes:

- fill-shader declarations and math/builtin inputs;
- Metal shader execution on macOS;
- Metal compute kernels from `@gpu` functions;
- WGSL generation for WebGPU-oriented output;
- MLIR GPU and SPIR-V emit paths;
- GPU simulation grid/layout helpers;
- native `gfx` drawing, input, image/blit, and window operations;
- SDL2 routes for Linux and Windows;
- headless frame recording, PPM frames, and GIF assembly;
- UI, 2D UI, and declarative UI-layout helpers;
- UI layout snapshots and window demonstrations;
- software 3D rendering, ray casting, cameras, meshes, and fixed-limit demos;
- Vulkan native examples, ABI renderer modules, and Flow-driven game demos.

The AI MUST identify the platform and execution path. Metal, WGSL, SPIR-V,
Vulkan, SDL, software rendering, and headless recording are not interchangeable
claims.

### 54.6 Verification and knowledge surface

The optional `flow-verify` package uses theorem-like Flow syntax, claim paths
or claim coordinates, tiers, provenance, assumptions, therefore steps,
properties on real code, proof documents, LaTeX, proof kernels, dependency
graphs, and a generated proof book/catalog.

Tools and workflows include:

- `flow doc proof` for one proof artifact;
- recursive proof document generation;
- kernel JSON, DOT, and plot output;
- `flow know` and knowledge/duplicate checks where supported;
- wiki proof catalogs;
- the large `lib/verify` and `examples/verify` corpus.

Do not claim that the entire corpus is mechanically verified. The checker and
parser have known gaps. Third-party package status is separate from ordinary
Flow compilation.

---

## 55. Compilation targets and platforms

| Route | Construction | Status rule |
|---|---|---|
| Stage-A C | Flow source → self-hosted `flowc` → C → native compiler | Default core route; subset is documented in `compiler/README.md`. |
| Python-host C | full parser/check/lowering → C → native compiler | Broadest general route and normal semantic baseline. |
| MLIR CPU | Flow AST → MLIR → LLVM conversions/link | Co-equal but incomplete; require parity tests. |
| JIT | MLIR-oriented generation and runtime execution | External LLVM tools; use for iteration and ML workloads. |
| ML workflow | `ml run`, `jit`, `bench`, `test` | MLIR-first convenience surface; state exact subcommand. |
| Metal compute | `@gpu` kernels → Metal source/runtime | macOS and Apple GPU route. |
| Fill shader | FSL/shader surface → Metal window | macOS route. |
| WGSL | Flow → WGSL text | WebGPU-oriented emit; browser/runtime integration is separate. |
| SPIR-V | MLIR GPU path → SPIR-V emit | Execution loader maturity differs from emission. |
| WebAssembly C | Flow → C → Emscripten | Default browser build route where Emscripten is installed. |
| WebAssembly MLIR | Flow → MLIR/LLVM → Emscripten | More external tools and narrower feature coverage. |
| Python package | Flow → C extension bindings → wheel | macOS/Linux documented; ABI-compatible exports only. |
| JavaScript | Stage-A or browser-oriented JS generation | Limited surface; match/other parity differs. |
| Native mixed project | Flow plus `[native]` sources/libs | Package build-native/run-native route. |
| Audio | Flow C plus miniaudio/runtime | Device and callback constraints apply. |
| Graphics | Flow C plus Cocoa/CoreGraphics/Metal or SDL2 | Platform-specific runtime selection. |

Platform coverage is strongest on macOS and Linux with the C backend. Windows,
WASM, GPU, and parts of MLIR are partial. x86-64 and Apple arm64 are the main
tested native architectures; Linux arm64 coverage is less systematic.

### 55.1 WebAssembly crossings

WASM work may require:

- exported ABI names;
- JavaScript-to-WASM and WASM-to-JavaScript crossings;
- browser file-system mode: memory or IDBFS;
- directory preloading;
- extra linked C objects;
- threads and cross-origin isolation;
- socket/WebSocket relay support;
- browser graphics stubs;
- a generated runnable page and a real browser verification pass.

The AI MUST test the crossing. The existence of a `.wasm` file is not enough.

### 55.2 Python package target

The Python target automatically selects public ABI-compatible functions and
structs, excludes `main` and private names, generates a CPython extension, and
can build a wheel. Scalars map to Python numeric/string/bool values, pointers
may cross as capsules, and structs may cross as dictionaries.

Current limitations include struct methods, Python async mapping, NumPy array
integration, complex nested generics, and Windows packaging. Proposed
`@python(...)` export controls are future syntax and MUST NOT be presented as
shipped.

---

## 56. CLI workflow map

This table expands the shorter command map and covers the executable command
families in the current driver.

| Command | Workflow |
|---|---|
| `version` | Print toolchain version and current host mode. |
| `help` | Print current commands, flags, and environment controls. |
| `check` | Run source checking without the full run workflow. |
| `run` | Compile and execute through the selected host/backend. |
| `compile` | Compile without executing. |
| `show-flags` | Display native C flags for profiles and sanitizers. |
| `analyze` | Scan C for MISRA/CERT patterns or analyze Flow WCET/stack when given Flow/flags. |
| `audio` | Compile and run with the audio runtime. |
| `compile-audio` | Build the audio program without running it. |
| `debug` | Make an unoptimized debug binary and launch or prepare LLDB/GDB. |
| `dap` | Serve the IDE debug-adapter workflow. |
| `window` | Use the SDL window route. |
| `gfx` | Use the platform-selected native graphics route. |
| `record` | Run graphics headlessly and write frames or GIF output. |
| `shader` | Run the fill-shader route, normally Metal on macOS. |
| `demo` | Run named Vulkan, Vulkan-Flow, or UI-layout demonstrations. |
| Vulkan/UI aliases | `vulkan-demo`, `vulkan-demo-basic`, `vulkan-demo-advanced`, `vulkan-2048`, `vulkan-tetris`, `vulkan-snake`, `vulkan-pong`, `vulkan-breakout`, `vulkan-layout`, `vulkan-layout-dsl`, `ui-layout`, and `ui-layout-window`. |
| `mlir` | Emit MLIR and optionally run the optimisation pipeline. |
| `mlir-run` | Compile through MLIR and execute. |
| `jit` | JIT compile and execute. |
| `ml` | Run, JIT, benchmark, or test MLIR-first ML workloads. |
| `gpu` | Generate GPU compute kernels, especially Metal sources. |
| `fir-g` | Dump/analyze the FIR-G program graph; calibrate routes or list opt candidates. |
| `explain` | Print declarative implementation selection records. |
| `transpile` | Enter the advanced transpiler flag surface directly. |
| `fmt` | Format Flow files. |
| `test` | Tiered Flow transpile/native validation. |
| `test-strict` | Strict test shortcut. |
| `test-runtime` | Compile and execute runtime tests. |
| `test-lang` | Strict language tests that compile and run. |
| `test-python` | Python compiler/tool unit tests. |
| `test-interop` | Native interoperability tests. |
| `test-gpu` | GPU feature and code-generation tests. |
| `test-mlir` | MLIR verification tests. |
| `test-matmul` | Matrix optimisation/assembly demonstration. |
| `test-all` | Main aggregate test workflow. |
| `init` | Create a new project and `flow.toml`. |
| `add` | Add registry, git, URL, or path dependency. |
| `pkg install` | Install project dependencies into `flow_packages`. |
| `search` | Search the configured registry index. |
| `info` | Show package versions and source. |
| `publish` | Add the current package to the local/configured index. |
| `build` | Build the current project. |
| `build-native` | Build Flow with configured native sources/libraries. |
| `run-native` | Build and run a mixed native project. |
| `clean` | Remove known build artifacts; review scope before use. |
| `install` | Install project dependencies when a project exists, otherwise tools. |
| `setup` | Install/check LLVM and compiler tooling. |
| `python` | Generate Python extension source or wheel. |
| `wasm` | Produce WebAssembly and a runnable page with optional crossings. |
| `repl` | Start the interactive read/evaluate loop. |
| `examples` | List example programs. |
| `playground` | Start the local compile API and open the playground. |
| `know` | Query or maintain Flow’s knowledge/claim tooling where supported. |
| `doc proof` | Generate one proof document or recursively process a directory. |
| `doc bundle` | Build the combined proof book. |
| `doc kernel` | Emit a parameterized proof kernel and optional plot. |
| `install-tools` | Compatibility alias for toolchain setup. |

Because the advanced `transpile`, `record`, `wasm`, `mlir`, `fir-g`, package,
and test commands have their own flags, the AI MUST read their current help or
implementation before constructing a production command.

### 56.1 Environment controls

Important environment families include:

- `FLOW_HOST=flowc|python|auto`;
- `FLOW_CPU_BACKEND=c|mlir`;
- `FLOW_PROFILE=default|safety|flight`;
- `FLOW_SANITIZE` and individual UBSan/ASan/TSan switches;
- `FLOW_STRICT_EFFECTS`;
- `FLOW_RUN_PYTHON` for the shell-independent runner;
- `FLOW_LDFLAGS` and relevant native compiler flags;
- `FLOW_REGISTRY_PATH`, `FLOW_REGISTRY_URL`, and `FLOW_HOME`;
- Stage-A `FLOWC_*` controls for input, output, bundle, backend, and checking;
- `FLOW_FIR_G_THRESHOLDS` for calibrated graph routing;
- target-specific audio, GPU, WASM, and recorder variables documented near
  those workflows.

The AI MUST include each relevant environment setting in every reproduction.

---

## 57. Optimisation catalog

### 57.1 Optimisation authority

Correctness and profitability are separate:

- deterministic compiler rules and verification decide whether a transform is
  legal;
- heuristics, measurements, GPU analysis, or learned models may propose and
  score profitable choices;
- no profitability system may bypass type, effect, lifetime, alias, or semantic
  checks.

### 57.2 C and native compiler optimisation

Flow’s C route can use ordinary native optimisation levels and platform
libraries. Function attributes provide `@inline`, `@noinline`,
`@always_inline`, and `@target("features")`. `@always_inline` may fail when
the caller cannot legally absorb a target-specific body. Exported symbols and
library builds need external visibility, so inline spelling differs.

Use BLAS/LAPACK rather than private matrix loops for production linear algebra.
macOS uses Accelerate; Linux commonly uses OpenBLAS. Preallocate outputs and use
in-place operations when allocation cost matters.

### 57.3 MLIR pass levels

| Level | Current documented pipeline |
|---|---|
| O0 | no optimisation passes |
| O1 | canonicalization, CSE, symbol DCE |
| O2 | O1 plus inline, SCCP, mem2reg, LICM, affine loop fusion |
| O3 | O2 plus affine super-vectorization |

Individual disabling flags cover vectorization, loop fusion, mem2reg, SCCP,
LICM, CSE, DCE, and inline. `--print-pass-pipeline` inspects the selected
pipeline; `--opt-report` prints pass statistics.

Important honesty rule: affine vectorization and fusion can be soft no-ops when
the generator does not emit affine loops. A flag being present is not evidence
that a program changed.

### 57.4 Generator-side SIMD

The MLIR generator recognizes simple elementwise counted loops over supported
`f32` or `i32` memrefs. It emits vector transfers with width four plus a scalar
remainder. Pointer bases and loop-carried accumulators remain scalar. Required
vector-to-SCF and vector-to-LLVM conversion passes must stay in the lowering
pipeline.

The Flow SIMD vector surface and audio SIMD helpers are separate features. The
AI MUST not confuse explicit vectors, generator auto-vectorization, C compiler
auto-vectorization, and GPU execution.

### 57.5 Pipeline fusion

The AST fusion pass recognizes nested map, scale, and offset calls for `f32`
and `f64`. Map composition makes one lambda; scale factors multiply; offsets
add. It does not mean every `|>` chain is fused. Unsupported calls, effects,
different shapes, and aliasing-sensitive operations remain separate.

### 57.6 Declarative selection optimisation

Sort, search, selected matmul, and selected reduce operations use registered
implementations, applicability predicates, scratch claims, and static cost
models. `flow explain` is the audit surface.

Optimisation facts include element count, element kind/size, key range,
ordering provenance, direction, keys, stability, expected runs, policies, and
budgets. Facts are conservatively invalidated by mutation, calls, and complex
control flow.

### 57.7 FIR-G whole-program analysis

FIR-G is a dense-ID structure-of-arrays program graph with call graph, use-def,
coarse CFG, effects, reachability, dead-function, and purity analyses.

Device routes are CPU, NumPy, MLX, and auto. CPU is the correctness oracle.
Bulk implementations must match it. `--calibrate` measures routing break-even
and stores thresholds. Uncalibrated auto stays on CPU.

`--opts` currently discovers and scores dead-elimination and inline candidates.
It does not rewrite production IR. FIR-S and FIR-M are staged architecture;
existing C/MLIR/WASM/Metal/SPIR-V emitters remain the production routes.

Learned cost models, beam/speculative search, complete alias analysis,
dominators, and FIR-M lowering are future work. ML/GPU may propose; they do not
enter the trusted correctness core.

### 57.8 GPU and domain optimisation

Additional optimisation routes include:

- Metal compute and unified memory on Apple hardware;
- private GPU memory with explicit blit copies;
- GPU kernel and gradient scaffolds;
- MLIR GPU to SPIR-V emission;
- blocked/tiled matrix examples;
- audio SIMD and fixed-block processing;
- graph scheduling and bus routing for audio;
- shared numerical helpers for dynamics and PDEs;
- deterministic procedural generation and staged planet computation;
- arena allocation and bounded fixed storage;
- profile-guided choices made by external native compilers where configured.

### 57.9 Required AI optimisation workflow

1. Define the metric and correctness invariant.
2. Select the exact host, backend, target, and build flags.
3. Capture the baseline output and measurement distribution.
4. Run `explain`, pass reports, FIR-G, or generated-target inspection as
   appropriate.
5. Form one falsifiable bottleneck hypothesis.
6. Change one optimisation layer.
7. Prove semantic equivalence with focused and parity tests.
8. Measure with the same method and environment.
9. Record latency, throughput, memory, scratch, binary size, compile time, and
   energy only when each is relevant and actually measured.
10. Check safety regressions, especially allocation, bounded work, races, and
    numerical stability.
11. Keep the change only if the evidence supports it.

---

## 58. Testing, diagnostics, safety, and tools

### 58.1 Test forms

| Layer | Evidence |
|---|---|
| Lexer/parser unit | token and AST structure, valid/invalid syntax |
| Type/semantic unit | accepted types, rejected combinations, exact diagnostics |
| Lowering/codegen unit | generated C/MLIR fragments and structural properties |
| Native compile | target compiler acceptance with required warnings |
| Runtime Flow test | `main` returns 0; optional exact `.expected` output |
| Language test | strict compile and execution of a feature contract |
| Integration test | complete driver/backend/runtime path |
| Backend parity | same program and observable result on C and MLIR |
| Fuzzing | mutation, grammar-directed input, and crash pinning |
| Torture | deep/nested and resource-boundary shapes |
| Corpus differential | before/after passing and failing sets |
| Self-host fixed point | multiple compiler generations agree |
| Visual | recorded frames plus model/layout invariants |
| Audio | offline render, signal meters, safety chain, and device smoke |
| Benchmark | correctness-gated reproducible measurement |
| Documentation | link checks, runnable snippets, generated site checks |

### 58.2 Diagnostics and development tools

The tool surface includes strict and lenient checking, formatted source,
LSP syntax/intelligence/hover/dynamics/ordering support, VS Code integration,
REPL, LLDB/GDB debug builds, debug adapter protocol, coarse `#line` mapping,
generated C inspection, structured JSON runner output, kept intermediates,
playground/compiler API, documentation generation, wiki build and validation,
repository statistics, example verification, and failure triage scripts.

There is no complete Flow source linter or full source-level debugger yet.
Tree-sitter, upstream Pygments, and full external Linguist recognition are also
open ecosystem work.

### 58.3 Safety facilities

The safety surface includes:

- safety and flight profiles;
- strict native warnings;
- checked literal division and shift rules;
- optional signed overflow guards;
- recursion rejection;
- `@max_iterations` for while loops;
- `@rt_safe` direct and transitive heap-call checking;
- UBSan, ASan, and TSan;
- MISRA-C-2024 and CERT-C pattern scans;
- WCET and stack-depth estimates with budgets;
- reproducible-build and certification evidence documents;
- lifetime-domain rules;
- audio NaN/Inf guards, DC blocking, denormal handling, limiter, fades,
  watchdog, feedback guard, and meters;
- runtime race and concurrency support;
- explicit GPU allocation/copy/sync contracts.

Open safety gaps include full no-heap enforcement, device/file/GPU/lock checks
inside real-time regions, comprehensive undefined-behavior specification,
fault/radiation handling, formal certification, and target-measured WCET.

---

## 59. Standard-library and domain catalog

For exact signatures, use `docs/library/stdlib-api.md`, generated from the
current module sources. These groups name the full module surface
visible in `lib/stdlib` at this edition’s audit.

### 59.1 Core data, math, and system modules

| Area | Modules |
|---|---|
| Core data | `array`, `slice`, `collections`, `option`, `result`, `string`, `text`, `bigint` |
| Math/numeric | `math`, `checked_arith`, `vec`, `tensor`, `psychstats`, `fmm2d` |
| Sorting | `sorting/core`, `sorting/quadratic`, `sorting/gapped`, `sorting/heap`, `sorting/merge`, `sorting/quick` |
| Memory | `memory`, `memory_simple`, `memory_working` |
| I/O/system | `io`, `posix`, `process`, `sys_info`, `time`, `logpkg`, `keys` |
| Network | `net`, plus package-level HTTP/DNS facilities |
| Concurrency | `concurrent`, `async` |
| Interop | `python_embed`, C extern/header facilities outside the stdlib |
| Units/RF | `units_si`, `rf` |

### 59.2 Scientific, optimisation, and ML modules

| Area | Modules |
|---|---|
| Linear algebra | `blas`, dynamics `linalg`, Tensor operations |
| DSP | `dsp` and audio DSP modules |
| Autodiff | `autodiff`, `autodiff_reverse` |
| Neural networks | `nn`, `nn_autogen`, `ml_nn`, `ml_opt`, `nn_xor_loss_clean`, `nn_xor_loss_clean_grad`, `nn_xor_loss_params`, `nn_xor_loss_params_grad` |
| GPU gradients/kernels | `gpu_gradients`, `gpu_kernels` |
| AI/experiments | `ai`, `experiment` |
| Automata/circuits | `automata`, `circuit`, `spice` |
| Crypto | `crypto` |
| Spatial response | `srir` |

Autodiff includes forward Dual operations, reverse helpers, and checked-in
gradient-generation tools. Full compiler-integrated `loss.grad`, higher-order
AD, complete Jacobians, and general GPU reverse mode are not shipped.

### 59.3 Dynamics modules

The dynamics group contains:

`dynamics`, `dynamics/core`, `dynamics/linalg`, `dynamics/state_space`,
`dynamics/gramian`, `dynamics/attractor`, `dynamics/ga`,
`dynamics/ga_analysis`, `dynamics/lqr`, `dynamics/pde`,
`dynamics/portrait`, `dynamics/schur_lattice`, `dynamics/wfc`, and
`dynamics/wfc_ga_coupling`.

Together they cover matrices, system construction, stepping, rollouts,
controllability, Gramians, attractors/RK4, Lyapunov proxies, gain search,
closed-loop analysis, LQR, PDE helpers, phase portraits, Schur-lattice models,
wave-function collapse, and coupled WFC/GA analysis.

### 59.4 Audio modules

The audio group contains:

`audio`, `audio/clock`, `audio/control`, `audio/delay`, `audio/delay_line`,
`audio/effects`, `audio/envelopes`, `audio/filters`, `audio/gpu`,
`audio/graph`, `audio/graph_bus`, `audio/graph_scheduler`, `audio/io`,
`audio/lattice_allpass`, `audio/livecode`, `audio/notation`,
`audio/oscillators`, `audio/processor`, `audio/safety`, `audio/scales`,
`audio/simd`, `audio/sink`, `audio/synth`, `audio/verify`, and `audio/wav`.

The surface covers sample/frame types, clocks and tempo, smoothing, delays,
filters, common effects, envelopes, oscillators, synthesis, notation/scales,
graphs/buses/scheduling, device I/O, WAV, live code scaffolding, SIMD, GPU
fallback selection, lattice all-pass processing, safety chains, meters, and
offline verification.

### 59.5 Graphics, GPU, UI, and procedural modules

| Area | Modules |
|---|---|
| Graphics | `gfx`, `font`, `gif`, `sdl2` |
| GPU | `gpu_memory`, `gpu_sim`, `gpu_kernels`, `gpu_gradients` |
| 3D | `render3d` |
| UI | `ui`, `ui2d`, `ui_layout` |
| Vulkan | `vulkan`, `vulkan_abi_renderer`, `vulkan_renderer` |
| Procedural | `procgen`, `planet` |

The planet module is a staged cubesphere system with grid, tectonics,
elevation, erosion, climate, hydrology, and biome phases plus evidence hooks.
The procgen module provides deterministic gradient/value noise, fBm, ridged
fields, and domain warp.

### 59.6 Package-level ecosystem

The bundled registry adds pure Flow and native-wrapped packages, including
JSON, TOML, serde-style helpers, strings, CLI, logging, testing, extended
collections, HTTP, SQLite/SQL helpers, compression, DNS, image, FFI, and sample
libraries. `flow-verify` is an optional third-party package even though its
corpus lives in the repository.

The package manager supports registry names, exact/caret/range requirements,
path dependencies, git dependencies, monorepo subdirectories, lockfile commit
pins, local/remote JSON indexes, search, info, publish, and native dependency
collection. Hosted accounts, a yank API, a full transitive solver, and CDN
archives remain out of scope.

### 59.7 Example-domain coverage

Examples cover basics, functions/types, generics and traits, effects, async and
concurrency, memory and systems, networking, crypto, compilers, data/stats,
DSP/audio/RF/circuits, linear algebra, ML/AI, GPU/graphics/UI/3D, WASM,
dynamics/evolution/physics, games, morphogenesis, neuroscience, evolutionary
ecology, social models, numerical methods, procedural generation, and planets.

The AI SHOULD begin a domain task by finding the canonical example in that
domain and reading its status. The existence of an example is not by itself a
production-readiness claim.

---

## 60. Suggestion and proposal register

The AI MUST separate a suggestion from a commitment. This section records all
current proposal families discovered in the question, roadmap, maturity, and
next-action documents. Status may change; tests and implementation outrank old
checkboxes.

### 60.1 Open or partly open language decisions

| Proposal | Current direction or unresolved point |
|---|---|
| Lifetime `domain` blocks | Annotation-only domains shipped; block sugar remains future work. |
| Graphics frame blocks | Runtime/stdlib callback and frame-pump helpers ship; dedicated block sugar remains optional. |
| Phase-portrait representation | Helpers and a representation path exist; verify how much grammar is current before extending. |
| LQR beyond small fixed systems | Stdlib/DSL support has grown, but general LAPACK DARE and broader dimensions remain follow-on work. |
| Field/Laplacian | 1D helper and grammar MVP ship; 2D/general domains remain open. |
| Self-host cutover | Stage-A is default for the subset; Python remains the full-surface escape hatch. Hard removal is not complete. |
| Ordering `unique` result | Fixed array compacts the prefix and leaves stale tail; a length-bearing result remains a design choice. |
| Ordering copy versus mutate | Current surface is in-place; a pure sorted-copy default remains undecided. |
| Entropy | Syntax is reserved/parsed; effect versus seed API remains open. |
| `order {}` blocks | Pipeline surface ships; block sugar remains open. |
| Dynamics namespace | Additive `dyn.`/`dynamics` style is preferred; bare forms remain compatible. |
| Web playground debugger | Visual step debugger is desired; depends on a stronger browser compiler/interpreter route. |
| Module blocks | Currently flattened; real namespace semantics require a separate approved design. |
| Multi-implementation constraints | Programmatic selector exists; user attribute syntax and real-unit cost IR remain open. |

Some entries in `Questions.md` still say pending even where later pattern
adoption documents report an MVP as shipped. The AI MUST reconcile by running
the named example and test, then update stale status in a dedicated task.

### 60.2 Physical systems and safety proposals

The physical-systems sequence proposes:

1. fused DSP pipelines plus rate analysis and stronger guarantees;
2. MMIO/SVD, bitfields, fixed-point, and saturating arithmetic;
3. bare-metal/RTOS, interrupts, and explicit state machines;
4. identical simulation and deployment code for digital twins;
5. `@hardware` lowering toward RTL, clock-domain crossings, and partitions;
6. fault/radiation support and a stronger flight profile.

DSP fusion and parts of the safety profile ship. Rate analysis, the embedded
surface, hardware lowering, and fault tolerance remain partial or planned.

### 60.3 Example and domain proposals

Open or partial showcase areas include a complete TCP echo loop, a high-level
channel pipeline, checkable hybrid guarantees, a digital-twin example, a
stronger no-allocation embedded path, a shader coupled directly to a simulation,
crypto beyond existing SHA material, broader JSON/TSV demonstrations, deeper
compiler dogfood, honest physics-DSL limits, QR/eigen linear algebra, and more
polished interactive games.

The AI SHOULD treat these as product candidates. It MUST not implement all of
them merely because they are listed.

### 60.4 Performance and compiler proposals

Open performance work includes broader loop vectorization, effective inlining,
dead-code elimination, constant propagation, GPU autodiff, wider SIMD
intrinsics, FIR-G rewrites/FIR-M, learned profitability models, full alias and
control-flow analyses, and execution support for emitted cross-platform GPU
artifacts.

Several names also exist as partial passes, C compiler behavior, MLIR flags, or
FIR-G proposals. The AI must state which layer is meant before accepting a
performance task.

### 60.5 Tooling, ecosystem, and governance proposals

Open maturity work includes:

- freeze and test the specification for a 1.0 gate;
- define compatibility, deprecation, and feature lifecycle policies;
- publish a clause-mapped conformance suite;
- add a Flow source linter and fuller source debugger;
- improve Windows installers and distribution recipes;
- add signed release artifacts where required;
- improve tree-sitter, Pygments, and GitHub Linguist recognition;
- define a formal RFC process, named language team, and registry governance;
- grow curated third-party libraries and independent implementations;
- eventually consider formal standardization.

These require human authority and often external coordination.

### 60.6 Explicit non-goals and deferred areas

Current documents explicitly avoid or defer several large claims: a full
compiler reverse-mode tape, universal GPU reverse mode, exact event-time
refinement, a complete resumable effect-based TCP stack, immediate deletion of
the Python compiler, MLX in the correctness core, a hosted package service,
and a frozen formal standard. The AI SHOULD preserve these boundaries unless
the human changes them.

---

## 61. AI workflow catalog

This table lists the recurring types of AI work in this handbook.

| Workflow | First evidence | Required completion evidence |
|---|---|---|
| Explain or answer | implementation, test, focused document | sourced status with limits; no unrequested edit |
| Audit a claim | truth hierarchy and exact route | shipped/limited/designed split and reproduction |
| Write a core program | nearest Stage-A example | compile, run, invariant, exit code |
| Write a full-surface program | canonical Python-host example | explicit host/backend plus runtime check |
| Numerical/scientific model | equations, units, reference quantity | stability/tolerance evidence and measured invariant |
| Evolution/hybrid system | north-star status and canonical flow | step/event semantics plus theory check |
| Audio/real-time work | RT boundary and audio safety docs | no forbidden calls, offline render, device/path check |
| Graphics/UI/3D work | platform example and recorder | headless frames plus non-visual state/layout test |
| GPU work | exact Metal/WGSL/SPIR-V route | emitted artifact, tool validation, runtime check where supported |
| WASM/browser work | crossing and browser requirements | generated page/module and real browser behavior |
| Concurrency/network work | chosen handler/runtime primitive | deterministic reference, stress/race checks, shutdown behavior |
| FFI/native work | ABI declaration and link configuration | compile/link/run plus ownership/layout evidence |
| Python package work | ABI export analysis | built wheel/source, import call, excluded-symbol diagnostics |
| Package/library work | `flow.toml`, module/export conventions | install/build, lock behavior, consumer example |
| Bug diagnosis | minimal failing fixture | earliest wrong stage and passing regression |
| Compiler feature | approved syntax/semantics | complete vertical slice and host/backend parity decision |
| Backend feature | shared semantic fixture | target validation and parity or explicit rejection |
| Optimisation | correctness-gated baseline | comparable measurement and generated-plan evidence |
| Safety/certification support | threat/standard/profile scope | scanner/sanitizer/static evidence with limitations |
| Refactor | behavior pins before edit | unchanged outputs/tests and scoped diff |
| Documentation | current implementation and runnable example | link/example checks and honest status |
| Proof/knowledge work | claim coordinate, tier, dependencies | generated proof/kernel artifacts and checker status |
| Corpus repair | classified before-set | differential pass/fail sets and zero unintended regressions |
| Self-host work | bootstrap and fixed-point scripts | multiple agreeing generations and normal-program smoke |
| Release/package work | release policy and clean build | archives, checksums, install/use smoke, platform matrix |
| Repository maintenance | git status and generated-source rules | preserved unrelated work and focused verification |
| Design exploration | vision, constraints, current gaps | options, trade-offs, recommendation, human decision point |

### 61.1 Universal AI work sequence

Every change workflow follows this sequence:

1. **Receive intent.** Restate outcome, reason, scope, exclusions, and risk.
2. **Recover context.** Read instructions, status, current design, examples,
   tests, and the dirty worktree.
3. **Select the route.** Name host, backend, platform, command mode, profile,
   and external dependencies.
4. **Define proof.** State what commands, invariants, measurements, or artifacts
   will prove completion.
5. **Find the precedent.** Reuse a canonical construct, library, test harness,
   and file layout.
6. **Plan a narrow slice.** Keep one semantic objective and make dependencies
   explicit.
7. **Implement safely.** Preserve unrelated changes and repair the correct
   abstraction boundary.
8. **Verify progressively.** Focused checks first, then risk-based regression,
   parity, sanitizers, or corpus work.
9. **Inspect artifacts.** Generated C/MLIR, plan reports, frames, audio, graphs,
   packages, or benchmark data.
10. **Update durable knowledge.** Tests, focused docs, status matrices, and
    decision logs record the result.
11. **Handoff.** Lead with outcome, list files, exact checks, known limits, and
    the next safe action.

### 61.2 AI decision rules

- The human controls language meaning, public syntax, priority, architecture,
  and material scope changes.
- The AI may choose ordinary local implementation details established by
  precedent.
- The AI must ask when an unresolved choice changes user-visible semantics.
- The AI must not expand authority from “diagnose” to “fix,” or from “write” to
  “publish,” without the request supporting that action.
- Read-only inspection is preferred for uncertainty.
- Reversible, narrow changes are preferred for implementation.
- Destructive changes require exact target resolution and explicit authority.
- A dirty worktree is protected human work.
- Passing focused tests must never be reported as a full-suite pass.
- An unavailable dependency or backend is reported as unverified, not assumed.

### 61.3 AI communication rules

During work, the AI SHOULD provide short updates when the work changes stage:
inventory complete, cause found, implementation complete, verification result,
or blocker. Updates state evidence and next action, not generic reassurance.

The final response is self-contained and includes:

- the outcome first;
- clickable files or artifacts;
- exact test and run results;
- important limitations;
- preserved unrelated changes;
- one optional next action only when it adds value.

### 61.4 Multi-agent or multi-view analysis

Parallel or specialised AI views can help when subtasks are independent, such
as auditing different backends or ranking a large backlog. They SHOULD NOT edit
the same files without coordination. Their outputs need one deterministic
integration pass.

Agent voting may reveal consensus, disagreement, dependencies, and blind spots.
It does not replace human design authority or executable evidence. Random,
persona, and “chaos” opinions are exploratory inputs only.

---

## 62. Coverage audit and acceptance procedure

Before saying that this handbook covers a new repository state, run this audit:

1. Capture `./flow help` and diff every command against chapter 56.
2. Diff the spec implementation matrix against chapters 51–55.
3. Diff all `lib/stdlib/**/*.flow` modules against chapter 59.
4. Diff focused language/library page names against the contents and matrix.
5. Diff example top-level domains against chapter 59.7.
6. Diff test command families and directories against chapter 58.
7. Diff `src/flow/*optimizer*`, `*plans*`, `fir_*`, routing, and fusion modules
   against chapter 57.
8. Diff roadmap unchecked/partial entries and open questions against chapter
   60.
9. Run all handbook links.
10. Render the PDF and visually inspect the cover, one code-heavy page, one
    wide table, the proposal register, and the last page.

The audit result SHOULD report counts and uncovered items. An empty uncovered
set means coverage under the definition in chapter 50, not permanent universal
completeness.

---

# Part XII: Flow as a language for vibe coding

## 63. Direct outcomes without managing every line

Flow is meant to be **vibe coded**. The user describes the system, its limits,
and the required proof. The AI reads the repository, writes the program, runs
it, and reports the result. The user can direct the work through intent and
observed behavior. There is no need to supervise every source line.

The user still controls the work. The main interface is a written goal rather
than manual code entry:

```text
human intent
    -> AI interpretation and implementation
    -> Flow compiler and runtime
    -> tests, measurements, artifacts, and behavior
    -> human judgment
```

The user checks whether the result meets the request and whether its risks are
controlled. Source review is one way to do this. Tests, measurements, generated
files, and observed behavior can give better evidence for many tasks. New or
high-risk work still requires source review.

### 63.1 Why the same Flow program can be written in many ways

A Flow program states behavior. It rarely requires one exact spelling or one
implementation route. Two valid programs can produce the same result with
different structures, targets, or performance methods.

The AI may choose among variations such as:

- a loop, recursion, a collection operation, or a fused pipeline;
- a direct calculation, a helper function, a generic function, or a library
  call;
- a tuple, struct, enum, array, vector, span, or another suitable data model;
- explicit state updates or an evolution declaration;
- a general implementation or a constrained specialised implementation;
- scalar, SIMD, native-library, MLIR, or GPU execution;
- direct sorting or searching, or declarative selection among plans;
- ordinary error returns, option/result values, assertions, or effect handling;
- a compact program or a more explicit program with intermediate values;
- the self-hosted Stage-A route or the broader Python-host route when the
  feature requires it.

The user states the invariant, input range, performance target, platform, and
safety boundary. The AI chooses an established form that meets those terms.
The user does not need to dictate the syntax.

Programs that look equivalent can still differ in rounding, allocation, error
behavior, event order, parallel scheduling, real-time safety, or backend
support. The request MUST name each observable property that matters. The AI
MUST test those properties.

### 63.2 How Flow facilitates outcome-level direction

Flow supports this style in ten direct ways.

1. **Readable, compact source.** The language has a small core and direct
   notation. An AI can produce or revise complete units without excessive
   scaffolding.
2. **Static checks.** Parsing, name resolution, types, effects, lifetimes, and
   other analyses reject many invalid constructions before execution.
3. **Explicit execution routes.** Host, backend, build mode, and target can be
   named and recorded. Generated C, MLIR, shader, WASM, package, graphics, or
   audio artifacts can be inspected separately from source.
4. **Several valid levels of expression.** Ordinary imperative code, functional
   composition, domain declarations, evolution blocks, effects, GPU forms, and
   library calls let the AI choose a level close to the requested result.
5. **Executable examples.** The repository supplies patterns that an AI can
   reuse. Each generated program can start from working code.
6. **Evidence-producing tools.** Check, run, test, explain, analyze, benchmark,
   render, record, and target-specific commands expose behavior to both the AI
   and the human.
7. **Portable lowerings.** A high-level request can become ordinary native code,
   MLIR, a GPU artifact, WebAssembly, or another supported product without the
   human managing all intermediate text.
8. **Domain knowledge in the language and libraries.** Numerical, dynamic,
   graphics, audio, verification, and optimisation surfaces let prompts name
   domain intent instead of rebuilding infrastructure.
9. **Repository-held decisions.** Tests, status matrices, examples, design
   records, and documentation preserve what earlier work established.
10. **Explainable construction.** Generated plans and intermediate files can
    show which route was selected and why.

Each person can work at the required depth. A user can work with goals and
results. A reviewer can inspect tests and generated files. A specialist can
read the Flow source. A compiler engineer can trace lowering and runtime
behavior. Most tasks do not require all four levels of review.

### 63.3 When it is reasonable not to read the code

A user can accept an AI-created Flow program without reading every line when
all of these conditions are true:

- the task is low consequence and reversible;
- the required behavior is stated as observable tests or invariants;
- inputs, outputs, and failure conditions are bounded;
- the AI used established repository patterns;
- the compiler route and target are known;
- automated checks cover the important behavior;
- generated artifacts or runtime output can be inspected directly;
- performance, memory, and numerical limits are measured where relevant;
- no secret, permission, deployment, payment, or destructive action is hidden
  behind the program;
- the resulting change is narrow enough to replace or revert.

Suitable examples include a disposable visualization, a small data conversion, a
bounded numerical experiment, a generated example, a test fixture, a local
graphics sketch, an offline audio render, or a program whose full result can be
compared with a trusted reference.

For these tasks, check the contract and the evidence. A numerical test can
check conservation, tolerance, and reference values. A recorded frame sequence
can check a rendering requirement. A differential backend test can find a
lowering defect. A quick reading of the source might miss all three faults.

Code can remain unread, but the work must still be checked. Review this evidence
package:

```text
request and constraints
testable acceptance criteria
commands and exact results
selected generated artifacts
measurements and invariants
known limitations
focused source review only where risk points demand it
```

### 63.4 When source inspection remains necessary

The human or a qualified reviewer SHOULD inspect relevant code when a failure
could be costly, irreversible, difficult to observe, or unsafe. Inspection is
normally required for:

- security boundaries, authentication, cryptography, secrets, and permissions;
- financial, medical, legal, industrial, or safety-critical decisions;
- destructive file, database, infrastructure, or deployment operations;
- public ABI, package, protocol, storage-format, or language-semantics changes;
- unsafe memory, FFI, concurrency, lifetime, and real-time code;
- novel compiler lowering or optimisation work;
- insufficient test or specification coverage;
- nondeterministic systems whose failures are hard to reproduce;
- numerical work where error bounds are not established;
- large changes with weak precedents or unclear provenance;
- any case in which the evidence conflicts with the requested behavior.

For high-risk work, the AI can list the risk points, find the relevant files,
write adverse tests, and explain intermediate forms. This reduces the amount
of code that needs manual review. The user remains responsible for the result.

### 63.5 The context-growth method used to build Flow

Flow was built through a long sequence of LLM coding sessions. The working
context grew with the implementation. It did not stay inside one model or one
prompt. Context windows are finite, and sessions end. The repository stores the
context that must survive.

The durable context includes:

- working compiler and runtime code;
- canonical programs and counterexamples;
- focused tests and corpus tests;
- status matrices that separate shipped, partial, and proposed behavior;
- architecture and self-hosting documents;
- language decisions, open questions, and non-goals;
- generated artifacts and differential evidence;
- contribution rules and established implementation patterns;
- failures preserved as regression tests;
- this handbook and its coverage audit.

Each AI session reads this context from the repository. A completed task adds
verified knowledge for the next session. The process is cumulative:

```text
recover durable context
    -> make one bounded change
    -> produce executable evidence
    -> record the established result
    -> next session recovers a larger, better context
```

Flow's tools, tests, and examples have all been used in AI-directed work. Later
sessions can find and reuse the resulting patterns. Diagnostics expose wrong
assumptions. Tests preserve established behavior. Documentation restores the
project's terms and limits.

The repository holds the long-term memory. The compiler checks program meaning.
Tests and generated files show what happened. The user supplies purpose and
judgment. The LLM reads, writes, and repeats the work quickly.

### 63.6 A practical no-code-inspection workflow

Use this procedure when outcome-level review is safe.

1. State the desired outcome in ordinary language.
2. Name important inputs, outputs, platforms, limits, and forbidden behavior.
3. Ask the AI to find the nearest working Flow patterns before implementation.
4. Require it to choose and report the host, backend, and execution route.
5. Define observable acceptance tests, invariants, tolerances, or visual/audio
   reference properties.
6. Ask for a narrow, reversible implementation.
7. Require compile, runtime, regression, and domain-specific checks.
8. Request the exact command results and selected artifacts.
9. Ask the AI to state unverified assumptions and remaining risks.
10. Inspect the behavior and evidence. Inspect source only at identified risk
    points or when evidence is incomplete.
11. Preserve successful behavior in tests and documentation so the next AI
    session inherits it.

Example direction:

```text
Build a Flow program that simulates a damped pendulum and produces a CSV file.
Use an existing evolution example as the pattern. The energy must not increase
beyond a stated numerical tolerance after damping is applied. Choose the
simplest supported host and backend. Run the program, test the invariant against
a reference calculation, and report the output path, commands, measurements,
and limitations. Keep the change local and reversible. I will review the result
and evidence; identify any source section that still needs human inspection.
```

### 63.7 Direct the space of solutions, not one spelling

Many Flow programs can satisfy one request. Control the choices by stating:

- semantic invariants;
- accuracy and determinism requirements;
- latency, throughput, memory, or real-time limits;
- portability and backend requirements;
- safety and failure behavior;
- interfaces that must remain stable;
- evidence needed for acceptance;
- freedom the AI may use.

For example: “You may choose loops, pipelines, or an existing library operation.
The result must be deterministic. Do not allocate memory in the audio callback.
Process each block within the measured deadline.” The AI can choose the code,
but it cannot change these requirements.

Do not require familiar syntax without a technical reason. Require a specific
form when the product, lesson, interface, or safety rule depends on it. State
the intent clearly even when the AI can choose the implementation.

### 63.8 The trust ladder

Use more delegation when the evidence supports it:

| Level | Human review | Suitable work |
|---|---|---|
| 1. Source-led | Read all changed code and evidence | novel, risky, or foundational work |
| 2. Risk-led | Read critical sections and all evidence | bounded production changes with good tests |
| 3. Evidence-led | Review contract, tests, artifacts, and limits | established patterns with observable behavior |
| 4. Outcome-led | Review the produced result and concise evidence summary | low-risk, reversible, fully bounded generation |

Move to a lower level when the AI finds ambiguity, new language behavior, weak
coverage, backend disagreement, unexplained performance, or a failed invariant.
Move to a higher level after repeated successful checks. Judge the evidence,
not the confidence of the response.

### 63.9 Rule

Flow lets the user state intent at several levels. The AI can choose from
several valid program forms. The compiler, tests, and generated files make the
result checkable. The repository also gives each new model session the context
created by earlier sessions.

Use this rule:

> You may delegate the writing and avoid reading most code when the outcome is
> bounded and the evidence is strong. You may not delegate the definition of
> success, the judgment of material risk, or responsibility for the result.

---

## 64. Final principle

Use AI with Flow to produce the smallest complete piece of evidence that moves
the language, program, or model toward the human goal. A large amount of code
is not a useful target by itself.

Direct the AI with clear intent. Make it study the current construction. Keep
the execution route explicit. Prefer the language’s existing patterns. Make
each important claim inspectable. Test the model and the syntax. Record
decisions in the repository. Then repeat in narrow, complete increments.

That process has been fruitful because it keeps human judgment, AI speed, and
executable evidence in one loop.

---

## Source notes

This handbook was derived from the repository’s current executable help,
compiler and runtime structure, contribution protocol, architecture and
self-hosting documents, pattern-adoption record, language documents, tests,
canonical examples, and generated repository statistics. Important companion
sources are:

- [Contribution protocol](../CONTRIBUTING.md)
- [Project overview](../README.md)
- [Vision](../VISION.md)
- [Roadmap](../ROADMAP.md)
- [Getting started](getting-started.md)
- [Compiler architecture](project/architecture-writeup.md)
- [Pattern adoption](project/pattern-adoption.md)
- [Self-hosting](project/self-hosting.md)
- [Stage-A compiler](../compiler/README.md)
- [Evolution grammar map](vision/north-star.md)
- [Explainable compilation](language/explainable-compilation.md)
- [Safety profiles](language/safety-profiles.md)
- [Modules](language/modules.md)
- [Runtime test contract](../tests/runtime/README.md)
- [Repository statistics](generated/repository-stats.json)
