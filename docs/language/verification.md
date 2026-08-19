# Flow Verification: Same Language, Same Syntax

> **Third-party library — not core Flow.** Formal math verification lives in the **`flow-verify`** package ([overview](../third-party/flow-verify.md)). Core Flow is a general-purpose compiled language; the proof surface below is a design for that package, not current runnable host Flow.

> **Status:** Design spec (not yet implemented end-to-end)

The intended proof surface reuses ordinary Flow structure while adding theorem-oriented constructs. Because this page is a design specification, examples are labelled `flow-future`; they are deliberately not counted as current compilable Flow until the proof toolchain implements them.

## Proposed proof vocabulary

The design adds theorem declarations, assumptions, derived steps, and properties attached to code.

```flow-future
theorem nat_add_zero(n: Nat) {
    assume nat_zero_add(0)
    therefore n + 0 == n
}
```

## Claim paths

Facts are addressed by what they claim rather than by arbitrary snake-case aliases. The proposed coordinate form is:

```flow-future
theorem «Nat» «addition» «zero is the right identity» (n: Nat) {
    therefore n + 0 == n
}

assume «Nat» «addition» «zero is the right identity»(n)
```

The claim-coordinate design is described in [claim-coordinates.md](claim-coordinates.md) and [epistemology.md](epistemology.md).

## Theorem as function

```flow-future
theorem nat_add_commutes(a: Nat, b: Nat) {
    if a == 0 {
        assume nat_add_zero(b)
        assume nat_zero_add(b)
        therefore a + b == b + a
    } else {
        let n = pred(a)
        assume nat_add_commutes(n, b)
        assume nat_add_succ(n, b)
        therefore a + b == b + a
    }
}
```

Automation suffixes such as `by exhaustive`, `by smt`, and `by symbolic` are also design syntax rather than current host-compiler features.

## Properties on code

```flow-future
function ring_push(rb: ptr<RingBuffer>, value: i32) -> i32
    has property not ring_is_full(rb) before
    has property ring_size(rb) == old(ring_size(rb)) + 1 after
{
    ...
}
```

## Documentation and provenance

The design requires proof declarations to carry plain-English meaning, provenance, tier, dependencies, and downstream uses. The intended checker can then lint missing provenance, orphan derived theorems, synonym claims, and malformed claim coordinates.

## Planned implementation phases

The intended sequence is theorem/assume/therefore parsing and metadata first, then foundational libraries, then exhaustive/SMT backends, then graph/orphan checks and explainable proof traces.

## Proof artifacts

The proposed documentation tooling emits Markdown and LaTeX proof companions from verification sources. Existing `flow-verify` material varies in checker maturity; presence in the proof corpus does not imply acceptance by the current host Flow compiler.

```bash
flow doc proof examples/verify/math/derived/Nat-plus-zero-right.flow
flow doc proof examples/verify -r
```

See [flow-verify](../third-party/flow-verify.md), [epistemology](epistemology.md), and [claim coordinates](claim-coordinates.md) for the current experimental tooling and corpus status.
