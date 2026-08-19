# 17. Engineering, diagnostics, safety, and verification

Flow includes tools for editing, testing, debugging, inspecting programs, static analysis, safety profiles, and experimental verification tooling.

## 17.1 Formatting and interactive work

```bash
./flow fmt src/main.flow
./flow repl
./flow examples
./flow version
```

Native files remain the right unit for target, module, effect, DSL, and runtime work.

## 17.2 Compiler diagnostics

```bash
FLOW_HOST=python ./flow transpile program.flow --c --strict -o build/program.c
```

A useful diagnostic names the source location, failed rule, actual/expected types, and operation that required them. Fix the first causal error before later cascades.

## 17.3 Debugging

```bash
./flow debug program.flow
./flow debug program.flow --break main
./flow debug program.flow --break 42
./flow dap program.flow
```

Generated C carries source mappings so LLDB/GDB and editor integrations can relate native code to Flow source.

## 17.4 Test tiers

```bash
./flow test --tier1
./flow test --tier2
./flow test --strict --verbose
./flow test-runtime
./flow test-lang
./flow test-mlir
./flow test-python
./flow test-interop
./flow test-gpu
./flow test-all
```

Language tests normally return zero from `main` on success and distinct nonzero codes for failures.

## 17.5 Sanitizers

```bash
./flow run program.flow --sanitize=ub
./flow run program.flow --sanitize=asan
./flow run program.flow --sanitize=tsan
```

Sanitizers detect classes of faults on executed paths; they do not constitute proofs.

## 17.6 Safety profile

```bash
./flow compile control.flow --profile=safety --show-flags
./flow show-flags --profile=safety --sanitize=ub
```

The safety profile strengthens supported generated-C warnings/checks. It is compiler policy, not certification.

## 17.7 MISRA and CERT scans

```bash
./flow analyze build/control.c --standard=misra-c-2024
./flow analyze build/control.c --standard=cert-c --fail-on-violation
```

See [MISRA C:2024](../certification/misra-c-2024-compliance.md) and [CERT C](../certification/cert-c-compliance.md) for the documented coverage/deviation boundary.

## 17.8 WCET and stack analysis

The WCET tooling estimates source-level bounds and stack requirements where structure and annotations provide enough information. Caches, interrupts, DMA, device latency, and external calls still require target evidence. See [WCET and stack analysis](../certification/wcet-stack-analysis.md).

## 17.9 Explainable compilation

```bash
./flow explain examples/basics/declarative_sort.flow
```

The report exposes candidate plans, applicability failures, costs, constraints, and the selected implementation.

## 17.10 FIR-G

```bash
./flow fir-g program.flow
./flow fir-g program.flow --calibrate --opts
```

FIR-G is a compiler graph/analysis representation, not ordinary source syntax.

## 17.11 Reproducible builds

Reproducibility requires fixed compiler versions, dependency locks, generated inputs, target flags, environment, and external toolchains. See [reproducible builds](../certification/reproducible-builds.md).

## 17.12 Verification syntax

The theorem/assume/therefore surface belongs to experimental `flow-verify` design work and is not current host Flow. It is deliberately labelled as future syntax:

```flow-future
theorem add_zero(n: Nat) {
    assume definition_of_addition
    therefore n + 0 == n
}
```

A proof document may be a checked artifact, stepped derivation, or scaffold awaiting checker support. Presence in the proof catalog does not imply acceptance by the current host compiler.

The authoritative status pages are [verification design](../language/verification.md), [claim paths](../language/epistemology.md), [claim coordinates](../language/claim-coordinates.md), [parser status](../third-party/flow-verify-parser-status.md), and [proof catalog](../third-party/flow-verify.md).

## 17.13 Evidence levels

Example output establishes one run; regression tests establish repeatable stated behavior; sanitizers cover detected faults on executed paths; static analysis covers modeled patterns; convergence studies quantify numerical refinement; proof-kernel acceptance establishes derivability under its assumptions; certification establishes compliance with a defined process and target scope. These are distinct levels of evidence.

## Exercises

Give failing branches distinct exit codes, run a sanitizer on an intentionally invalid program, compare explain plans before/after a hint, and classify one proof by its actual checker status.

Next: [A complete instrument](18-a-complete-instrument.md).
