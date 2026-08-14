# Introduction to Flow

Flow is a statically typed, compiled language for programs and systems that
change over time. The book starts with small executable programs. Later parts
cover the full v0.11.1 language, numerical models, native runtimes, testing,
and deployment.

Most rules are shown with a complete program. Source files for the numbered
examples are kept in
[`examples/book`](../../examples/book/). Commands are written from the root of
the Flow repository.

## Compiler convention

Flow v0.11.1 has two compiler hosts:

| Host | Invocation | Use in this book |
|---|---|---|
| Self-hosted Stage A | `./flow run file.flow` | Core syntax, functions, control flow, arrays, and structs |
| Python host | `FLOW_HOST=python ./flow run file.flow` | The full language, including pipelines and evolution blocks |

The host requirement is printed beside each example. A program that requires
the Python host is still a Flow program. Only the compiler implementation is
different. The Python host accepts more of the language.

## Coverage contract

The book accounts for every public feature listed by the v0.11.1 language
specification and command-line interface. Each feature is classified as full,
partial, target-dependent, host-dependent, or planned in the
[feature coverage index](appendix-b-feature-coverage.md). Standard-library
families are mapped separately. The generated API lists individual functions.

## Contents

### Part I: The executable core

1. [A complete program](01-a-complete-program.md): source, compilation,
   execution, output, and exit status
2. [Values and types](02-values-and-types.md): numeric types, Boolean values,
   bindings, mutation, expressions, and casts
3. [Decisions and repetition](03-decisions-and-repetition.md): conditions,
   loops, ranges, accumulators, and termination
4. [Functions](04-functions.md): contracts, calls, return values, composition,
   and recursion
5. [Records and fixed arrays](05-records-and-arrays.md): structured values,
   indexed storage, traversal, and small data sets

### Part II: Composition and failure

6. [Pipelines and explicit results](06-pipelines-and-results.md): data flow,
   argument placement, validation, and recoverable failure

### Part III: Complete language and evolving systems

7. [From update loops to flows](07-from-updates-to-flows.md): numerical state,
   time steps, differential equations, and `flow` declarations
8. [Types and declarations beyond the core](08-types-and-declarations.md):
   wide and complex numbers, nominal types, units, generics, traits, and attributes
9. [Expressions, matching, and declarative operations](09-expressions-and-matching.md):
   closures, patterns, deferred cleanup, parallel loops, sorting, forks, and choices
10. [Memory, spans, and lifetime domains](10-memory-and-lifetimes.md): pointers,
    heap ownership, arenas, borrows, lifetime rules, and real-time safety
11. [Modules, projects, packages, and interoperation](11-modules-packages-and-interop.md):
    imports, exports, manifests, dependencies, C, ABI, and Python wheels
12. [Effects and concurrency](12-effects-and-concurrency.md): handlers, effect
    rows, channels, threads, fibers, and asynchronous I/O
13. [Evolution, hybrid systems, dynamics, and fields](13-evolution-and-dynamics.md):
    events, composition, representations, control analysis, LQR, and PDEs

### Part IV: Engineering and deployment

14. [Numerics, automatic differentiation, and machine learning](14-numerics-autodiff-and-ml.md):
    linear algebra, duals, reverse mode, tensors, training, and validation
15. [Graphics, shaders, GPU, UI, and audio](15-media-gpu-and-audio.md): native
    media runtimes, device code, recording, 3D, layout, and real-time DSP
16. [Compilation targets and distribution](16-targets-and-distribution.md): C,
    MLIR, JIT, WebAssembly, Python, graphics, audio, and stable ABI exports
17. [Engineering, diagnostics, safety, and verification](17-engineering-and-verification.md):
    tests, sanitizers, debugging, plan analysis, certification, and proofs
18. [A complete instrument](18-a-complete-instrument.md): model, controller,
    callback, effects, display, project layout, and evidence

### Part V: Practice

19. [Flow-specific coding challenge series](19-coding-challenge-series.md):
    36 checked problems covering data flow, types, memory, effects,
    concurrency, evolution, dynamics, device code, and a capstone

### Appendices

- [Language and command card](appendix-a-language-card.md)
- [Feature coverage index](appendix-b-feature-coverage.md)
- [Command reference](appendix-c-command-reference.md)
- [Standard-library map](appendix-d-standard-library-map.md)

## How to read the examples

Each complete program has four parts:

1. the source;
2. the command that runs it;
3. the observable result;
4. a short account of the rule being demonstrated.

Fragments that intentionally fail type checking are labelled **Rejected
program** and are not presented as runnable examples. Output blocks omit the
runner's coloured status lines and retain only program output.

## Notation

- `T` denotes a type.
- `x: T` means that `x` has type `T`.
- `[a, b)` denotes a half-open interval: it contains `a` and excludes `b`.
- “Lowering” means translating a higher-level Flow construct into a simpler
  intermediate form before code generation.
- “State” means a value retained from one update to the next.

The language reference defines the grammar and edge cases. The book explains
the language in order and provides working programs.
