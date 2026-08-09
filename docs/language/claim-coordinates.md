# Claim Coordinates

> **Replaces:** `Nat/+.zero-left` and all path/shorthand addressing.

## Why the old paths failed

`Nat/+.zero-left` parses as "Nat plus zero-left", a filesystem fragment, not a mathematical sentence.
Symbols (`+`) mixed with English fragments (`zero-left`) do not compose.
Nobody says "Nat plus zero-left" in a seminar.

## The fix: three full-word layers

| Layer | Question it answers | Example |
|-------|---------------------|---------|
| **carrier** | What kind of thing? | `Nat`, `Bool`, `FullAdder` |
| **structure** | Which operation or transform? | `addition`, `disjunction`, `output` |
| **law** | What property holds? (full English) | `zero is the left identity` |

**Display:** `Nat › addition › zero is the left identity`  
**Syntax:** `«Nat» «addition» «zero is the left identity»`  
**Slug (tools):** `Nat.addition.zero_is_the_left_identity`

The guillemets `«»` are the syntax novelty, visually distinct, unambiguous, read aloud as quoted phrases.

## Syntax

```flow
theorem «Nat» «addition» «zero is the left identity» (m: Nat) {
    therefore 0 + m == m
}

assume «Nat» «addition» «zero is the left identity»(0)

export «Nat» «addition» «zero is the left identity»
```

Surface math still uses `+`, `succ`, `==`, only **addresses** use full words.

## Legacy mapping

| Old (deprecated) | New coordinate |
|------------------|----------------|
| `Nat/+.zero-left` | `«Nat» «addition» «zero is the left identity»` |
| `Nat/+.zero-right` | `«Nat» «addition» «zero is the right identity»` |
| `Nat/+.succ-right` | `«Nat» «addition» «successor on the right steps the sum»` |
| `Nat/+.commutes` | `«Nat» «addition» «order does not matter»` |
| `Bool/||.commutes` | `«Bool» «disjunction» «order does not matter»` |
| `Eq/=.reflexive` | `«Eq» «equality» «everything equals itself»` |

Legacy paths still parse; new code should use guillemets.

## Proof kernel (parameterize & plot)

Every proof compiles to a **kernel**, a DAG of numbered steps with explicit edges:

```bash
flow doc kernel examples/verify/math/derived/Nat-plus-zero-right.flow \
  --param n=0 --plot build/proofs/zero-right-n0.png
```

Outputs:
- `.proof.kernel.json`, nodes, edges, parameters, active branch flags
- `.png` / `.dot`, dependency plot (green = active under instantiation)

Use kernels for teaching widgets, CI proof visualization, and LLM trace audit.