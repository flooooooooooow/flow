# 17. Engineering, diagnostics, safety, and verification

Flow includes tools for editing, testing, debugging, and inspecting programs.
The repository also contains static checks, graph analysis, safety profiles,
and an experimental verification language.

## 17.1 Formatting and interactive work

```bash
./flow fmt src/main.flow
./flow repl
./flow examples
./flow version
```

The formatter establishes canonical source layout. The REPL is suitable for
small core expressions; native files remain the correct unit for target,
module, effect, DSL, and runtime work.

## 17.2 Compiler diagnostics

Strict compilation turns type and effect findings into failures:

```bash
FLOW_HOST=python ./flow transpile program.flow --c --strict -o build/program.c
```

A good diagnostic names the source location, the failed rule, the actual and
expected types, and the operation that required them. Fix the first cause
before working through later errors.

## 17.3 Debugging

```bash
./flow debug program.flow
./flow debug program.flow --break main
./flow debug program.flow --break 42
./flow debug program.flow --no-launch
```

Generated C carries source line mappings so LLDB or GDB can relate native code
to the Flow file. `dbg expression` and `expect condition` provide lighter
instrumentation on the C backend.

The Debug Adapter Protocol server connects the native debugger to editors:

```bash
./flow dap program.flow
```

## 17.4 Language server and editor support

The LSP supplies syntax diagnostics, document structure, completion and related
intelligence to the VS Code extension. Because host and backend support differ,
confirm an editor diagnostic with the build command used by
the project.

The repository includes VS Code language, theme, and extension packaging under
`third_party/integrations/vscode/`.

## 17.5 Test tiers

```bash
./flow test --tier1              # transpile only
./flow test --tier2              # transpile and C syntax check
./flow test --strict --verbose
./flow test-runtime              # compile and execute runtime tests
./flow test-lang                 # strict language programs
./flow test-mlir
./flow test-python
./flow test-interop
./flow test-gpu
./flow test-matmul
./flow test-all
```

A language test is usually a program whose `main` returns zero on success and
a distinct nonzero code for each failed assertion. Tests that validate printed
behaviour also use an expected-output file.

## 17.6 Sanitizers

```bash
./flow run program.flow --sanitize=ub
./flow run program.flow --sanitize=asan
./flow run program.flow --sanitize=tsan

FLOW_UBSAN=1 ./flow run program.flow
FLOW_ASAN=1 ./flow run program.flow
FLOW_TSAN=1 ./flow run program.flow
```

Undefined-behaviour sanitising detects selected invalid arithmetic and pointer
operations. AddressSanitizer detects many bounds, lifetime, and allocation
errors. ThreadSanitizer detects many data races. Sanitizers alter execution and
do not prove the absence of bugs they cannot observe.

## 17.7 Safety profile

```bash
./flow compile control.flow --profile=safety --show-flags
./flow show-flags --profile=safety --sanitize=ub
```

The default C profile uses C11 and warnings. The safety profile promotes the
supported warning set to errors, rejects selected literal undefined behaviour,
and applies stricter checks to generated C. The profile is compiler policy; it
is not a certification.

`@safe` marks a function whose checked call graph may not enter `@unsafe`
functions or bare dangerous extern declarations. `@unsafe` identifies a
reviewed escape; under the safety profile, extern boundaries require the
explicit unsafe marking. Neither annotation makes raw C intrinsically safe.

## 17.8 MISRA and CERT scans

```bash
./flow analyze build/control.c --standard=misra-c-2024
./flow analyze build/control.c --standard=cert-c --fail-on-violation
```

The scanner reports known generated-C patterns against the selected rule set.
The certification documents distinguish covered rules, deviations, compiler
assumptions, and work still requiring process evidence:

- [MISRA C:2024 compliance](../certification/misra-c-2024-compliance.md)
- [CERT C compliance](../certification/cert-c-compliance.md)

## 17.9 WCET and stack analysis

The WCET tool estimates loop bounds, call relationships, and stack
requirements where source structure and annotations provide enough
information. Hardware caches, pipelines, interrupts, DMA, device latency, and
external calls require a target-specific timing argument.

See [WCET and stack analysis](../certification/wcet-stack-analysis.md) and the
corresponding language tests.

## 17.10 Explainable compilation

Declarative constructs can have several valid implementations. Inspect the
selection:

```bash
./flow explain examples/basics/declarative_sort.flow
```

The report lists candidate plans, applicability failures, costs, constraints,
and the selected implementation. The report is most useful for sorting,
search, matrix operations, and reductions.

## 17.11 FIR-G

```bash
./flow fir-g program.flow
./flow fir-g program.flow --calibrate --opts
```

FIR-G exposes a graph representation and analyses used for routes,
dependencies, calibration, and optimisation work. FIR-G is compiler analysis,
not ordinary source syntax.

## 17.12 Reproducible builds

Reproducibility requires fixed compiler versions, dependency locks, generated
source inputs, target flags, environment, and external toolchains. The project
documents its reproducible-build boundary in
[reproducible builds](../certification/reproducible-builds.md).

Keep generated C or structured build metadata when a review or certification
process must reconstruct the executable.

## 17.13 Verification syntax

The verification syntax includes theorem documents, assumptions,
derivations, and claim paths:

```flow
theorem add_zero(n: Nat) {
    assume definition_of_addition
    therefore n + 0 = n
}
```

Claim coordinates record domain, corpus, work, and numbered claim so a result
can be addressed and cited. The proof kernel and `flow-verify` corpus include
logic, arithmetic, data structures, circuits, transforms, and Euclid material.

## 17.14 Verification status

Theorem syntax and tooling are partial and intentionally ahead of the core
parser/checker in parts of the corpus. A `.proof.md` document may be a formal
artefact, a stepped derivation, or a scaffold awaiting checker support. Do not
equate “present in the proof catalog” with “machine-checked by the current
kernel”.

The authoritative distinctions are:

- [verification design](../language/verification.md);
- [claim paths](../language/epistemology.md);
- [claim coordinates](../language/claim-coordinates.md);
- [parser status](../third-party/flow-verify-parser-status.md);
- [proof catalog](../third-party/flow-verify.md).

## 17.15 Evidence levels

Use precise language for engineering evidence:

| Evidence | Establishes |
|---|---|
| example output | one observed run |
| regression test | repeatable behaviour for stated inputs |
| sanitizer run | absence of detected faults on executed paths |
| static analysis | absence or presence of modelled patterns |
| numeric convergence study | agreement under refinement |
| proof-kernel acceptance | derivability under the kernel and assumptions |
| certification | compliance with a defined process and target scope |

No row implies the rows beneath it automatically.

## Exercises

1. Give each failing branch of a program a distinct exit code.
2. Run AddressSanitizer on a deliberately out-of-bounds pointer example.
3. Compare an explain report before and after supplying an ordering hint.
4. Classify one repository proof by its actual checker status.

Next: [A complete instrument](18-a-complete-instrument.md).
