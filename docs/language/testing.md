# Testing Flow projects

Flow has a first-class project test command:

```bash
flow test
```

The default convention is simple: place `.flow` tests under `tests/` and write named `test` blocks using the language's existing `expect` assertion form.

```flow
test "addition is exact" {
    expect 20 + 22 == 42
}

test "state update is deterministic" {
    let mut x: i32 = 3
    x = x * 4
    expect x == 12
}
```

A passing `expect` is silent. A failing `expect` aborts the isolated test case and `flow test` reports that named case as failed.

## Why tests are language constructs

Testing should use the same types, module system, compiler, runtime and effects as the code under test. `test "name" { ... }` is therefore ordinary Flow syntax rather than a macro package or a Python testing DSL.

The CLI is responsible only for discovery, isolation, compilation, execution and reporting. Test bodies remain Flow.

This separation also means a domain package such as `flow-audio` can build rich test helpers without inventing another runner.

## Discovery

From a Flow project, `flow test` finds the nearest `flow.toml` and searches:

```text
tests/
```

recursively by default. Files beginning with `_` are treated as helper modules rather than runnable test files. Build/package/WIP directories are ignored.

Override the roots in the manifest:

```toml
[test]
paths = ["tests", "conformance"]
backend = "c"
timeout = 30
```

Or pass paths directly:

```bash
flow test tests/dsp.flow
flow test tests/unit tests/integration
```

A test file may contain any number of named test blocks. Each block is compiled and executed as an isolated case, so one abort or crash does not hide the identity of another case.

## Compatibility with executable tests

Existing Flow test programs remain valid:

```flow
function main() -> i32 {
    if 6 * 7 != 42 {
        return 1
    }
    return 0
}
```

A `.flow` file with no named test blocks but with `main()` is treated as one compatibility test. Exit code zero passes unless a sibling `.exitcode` says otherwise.

This keeps the existing `tests/lang` / runtime-test corpus usable while projects migrate toward named tests.

## Listing and filtering

```bash
flow test --list
flow test --filter delay
flow test -f 'tests/filter*'
```

Case IDs have the form:

```text
tests/delay.flow::integer delay is exact
```

A filter without glob metacharacters is a case-insensitive substring match. A filter containing `*`, `?` or `[` uses glob matching.

## Backends

The normal project default is the portable C backend:

```bash
flow test
flow test --backend=c
```

Run the same semantic tests through MLIR:

```bash
flow test --backend=mlir
```

Or qualify both:

```bash
flow test --backend=all
```

`--backend=all` deliberately duplicates each case across backends. A backend mismatch is therefore visible as an ordinary test failure rather than being hidden by a special parity harness.

## Sanitizers and safety profiles

Test compilation accepts the same native safety options as normal Flow compilation:

```bash
flow test --sanitize=ub
flow test --sanitize=asan
flow test --sanitize=ub,asan
flow test --profile=safety
```

You can also select the compiler host while the self-hosted compiler is converging:

```bash
flow test --host=flowc
flow test --host=python
flow test --host=auto
```

The runner does not reimplement compilation. It invokes the same internal driver used by `flow compile` and executes that binary directly.

## Golden output and expected failures

Program-style tests support sibling files:

```text
tests/parser.flow
tests/parser.expected
tests/parser.expected-stderr
tests/parser.exitcode
```

`.expected` is exact stdout.

`.expected-stderr` is exact stderr.

`.exitcode` contains the expected integer process exit code; the default is `0`.

For a named test, use its stable slug. `flow test --list` shows the test names; slugs are lower-case words joined by `_`:

```flow
test "rejects a zero-delay cycle" {
    ...
}
```

may use:

```text
tests/graph.rejects_a_zero_delay_cycle.expected
tests/graph.rejects_a_zero_delay_cycle.expected-stderr
tests/graph.rejects_a_zero_delay_cycle.exitcode
```

Most named tests should use `expect` rather than goldens. Goldens are intended for observable protocol/diagnostic/output contracts.

## Timeouts and failure control

```bash
flow test --timeout=10
flow test --fail-fast
flow test -v
```

The timeout applies independently to compilation and execution of each case. `-v` prints output even for passing tests. Generated isolation wrappers are removed automatically; `--keep` retains them for debugging.

## Project vs compiler-repository tests

The Flow compiler repository historically used `flow test` for its own broad transpile/clang tier sweep. That maintenance workflow remains available:

```bash
flow test --compiler
```

When invoked from the Flow repository root, `flow test` keeps that historical behavior by default. To exercise project-test semantics on the Flow repository itself:

```bash
flow test --project tests/project_testing
```

All other Flow projects get the project test runner from plain `flow test`.

## Test design guidance

Prefer small named semantic properties over large scenario scripts:

```flow
test "automation changes exactly at its frame" { ... }
test "feedback without positive delay is rejected" { ... }
test "state roundtrip is deterministic" { ... }
```

Use executable compatibility tests when the thing being tested is inherently process-level. Use goldens only when exact text or bytes are the public contract.

For numerical systems, an `expect` should encode a meaningful tolerance or invariant rather than merely checking that a number exists. Domain libraries are encouraged to provide richer helpers such as approximate equality, spectra/error bounds, property generators and deterministic fixtures.

## What comes next

The runner intentionally starts with a small durable semantic core. Natural extensions include:

- package-provided test fixtures and setup/teardown;
- property-based test generation with deterministic seeds;
- benchmark cases separated from pass/fail tests;
- structured numerical/audio/image golden artifacts;
- test metadata such as `@slow` or required capabilities;
- compiler-native test enumeration so the temporary source-isolation transform can disappear;
- parallel execution once compiler/build artifact isolation is fully namespaced.

Those additions should extend `flow test`, not create competing test commands.
