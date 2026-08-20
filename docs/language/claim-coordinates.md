# Claim Coordinates

Claim coordinates are an experimental addressing scheme for the `flow-verify` proof surface. They are not current host-Flow syntax, so examples on this page are explicitly labelled `flow-future`.

## Three full-word layers

| Layer | Question it answers | Example |
|-------|---------------------|---------|
| carrier | What kind of thing? | `Nat`, `Bool`, `FullAdder` |
| structure | Which operation or transform? | `addition`, `disjunction`, `output` |
| law | What property holds? | `zero is the left identity` |

Display form: `Nat › addition › zero is the left identity`.

The proposed source coordinate uses guillemets:

```flow-future
theorem «Nat» «addition» «zero is the left identity» (m: Nat) {
    therefore 0 + m == m
}

assume «Nat» «addition» «zero is the left identity»(0)
```

Surface mathematics still uses ordinary operators; the coordinate only changes how a proof claim is addressed.

## Legacy mapping

| Old form | Proposed coordinate |
|----------|---------------------|
| `Nat/+.zero-left` | `«Nat» «addition» «zero is the left identity»` |
| `Nat/+.zero-right` | `«Nat» «addition» «zero is the right identity»` |
| `Nat/+.commutes` | `«Nat» «addition» «order does not matter»` |
| `Bool/||.commutes` | `«Bool» «disjunction» «order does not matter»` |

## Proof kernels

The experimental proof tooling can emit graph-shaped proof artifacts for teaching, visualization, and audit. These artifacts belong to `flow-verify`; they are not evidence that the same source is accepted by the current host compiler.

```bash
flow doc kernel examples/verify/math/derived/Nat-plus-zero-right.flow --param n=0 --plot build/proofs/zero-right-n0.png
```

See [Verification](verification.md) and [Epistemology](epistemology.md) for the experimental proof-language status.
