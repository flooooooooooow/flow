# Flow Epistemology: Claim Paths

> **Third-party `flow-verify` design, not current host Flow syntax.**

Claim Paths are an experimental way to address formal facts by what they claim rather than by invented snake-case theorem names. All source examples on this page are labelled `flow-future` until the proof toolchain implements the surface end-to-end.

## Core idea

A claim address has a domain, morphism, and facet, for example `Nat/+.zero-right` or `Bool/||.commutes`. Literature provenance belongs in metadata rather than in the identifier.

```flow-future
# @means Adding zero on the right gives the same number.
# @from peano/induction
# @tier derived

theorem Nat/+.zero-right(n: Nat) {
    if n == 0 {
        assume Nat/+.zero-left(0)
        therefore 0 + 0 == 0
    } else {
        let k = pred(n)
        assume Nat/+.zero-right(k)
        therefore n + 0 == n
    }
}
```

## Import and export design

```flow-future
assume Nat/+.zero-right(n)
export Nat/+.zero-left, Nat/+.succ-right
import verify.Nat/+ { zero-left, succ-right }
```

These forms are proof-language design syntax, not ordinary module syntax accepted by the current host compiler.

## Epistemic tiers

The proposed metadata distinguishes `definition`, `axiom`, and `derived`. The path says what the claim is; `@tier` says how it is justified; `@from` records provenance.

```flow-future
# @tier axiom
# @from leibniz

theorem Eq/=.reflexive(x: Nat) {
    therefore x == x
}
```

## Duplicate prevention

The design canonicalizes a theorem conclusion into a fingerprint so two names cannot be created for one claim.

```flow-future
theorem Nat/+.zero-right(n: Nat) { therefore n + 0 == n }
theorem Nat/+.identity-right(n: Nat) { therefore n + 0 == n }
```

The second declaration is intended to be rejected as a duplicate claim when this checker layer ships.

## Proof artifacts

The experimental documentation tooling can emit Markdown and LaTeX proof companions and expose claims through `flow know` / proof-document commands. The proof corpus has mixed checker maturity, so an artifact existing in the repository does not imply acceptance by the current host compiler.

```bash
flow doc proof examples/verify/math/derived/Nat-plus-zero-right.flow
flow doc proof examples/verify -r
```

See [Verification](verification.md), [Claim Coordinates](claim-coordinates.md), and the [flow-verify overview](../third-party/flow-verify.md) for current status.
