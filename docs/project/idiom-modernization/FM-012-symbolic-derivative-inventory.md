# FM-012 slice 4: symbolic derivative notation inventory

Status: evidence inventory for [#1740](https://github.com/flooooooooooow/flow/issues/1740) and FM-012, base `2168bdcbb` (post #1756). This is a discovery document. It does not approve semantics, assign feature status, or complete FM-012. Companion to [slice 1](FM-012-flow-evolution-inventory.md) (flow/evolution equation syntax) and [slice 2](FM-012-dynamics-field-inventory.md) (matrix dynamics and restricted field lowering). Slice 3 covers algebraic residuals, DAE and MNA. The full derivative-type audit is owned by FM-019.

## Scope and non-scope

**In scope (this slice):** whether Flow has any surface syntax for symbolic or implicit differentiation (Leibniz/Newton notation, gradient/Jacobian operators, `grad(f)` calls), and where derivatives are actually computed.

**Out of scope for this slice:**

- Autodiff library correctness and numerical stability (FM-019).
- Derivative typing inside `evolves as` RHS (FM-010, FM-011).
- `math_prose.flow` rendering helpers (compiler-internal; not an executable equation surface).

## Finding: no symbolic derivative notation in the language

Search of `compiler/src/` (parser, lexer, expr_type, sem_check, flow_blocks, dynamics_dsl, field_dsl) finds no grammar, keyword or operator for symbolic differentiation. Specifically:

- No token for `d/dt`, `∂`, `∇`, `grad`, `jacobian`, `hessian` or `derivative`.
- No parser rule producing a derivative expression node. `evolves as <expr>` parses the RHS as an ordinary expression; the derivative relationship is implicit in the `evolves` member and is not a first-class expression.
- No type-level derivative constructor. `expr_type.flow` contains no derivative/gradient type.
- `flow_blocks.flow` validates the RHS of `evolves as` as a pure expression; it does not transform or differentiate it.

Conclusion: Flow has no symbolic derivative notation. Derivatives are computed with libraries. There is no language syntax for them.

## Where derivatives are actually computed

| Facility | Owner | Evidence anchor | Notes |
|---|---|---|---|
| Forward-mode autodiff via dual numbers | `lib/stdlib/autodiff.flow` | `Dual` struct with `val` and `grad`; `dual_var` seeds ∂/∂x with gradient 1; `dual_const` seeds 0; arithmetic operators implement the product/quotient/chain rules | Library type. User writes `Dual` arithmetic by hand or via the provided helpers. No implicit differentiation of an arbitrary expression. |
| Reverse-mode helpers | `lib/stdlib/autodiff_reverse.flow` | `UnaryResult`/`BinaryResult` carrying local gradients; `op_add`, `op_sub`, `op_mul`, `op_div` and friends return both value and gradient components | Manual backpropagation building blocks. No tape is auto-generated from a loss expression. |
| Continuous-time derivative | `flow` blocks with `evolves as` | `compiler/src/flow_blocks.flow`: state must be declared, exactly one `evolves` per state, RHS checked pure (slice 1) | The derivative is implicit in the member. The RHS is an ordinary expression evaluated at runtime. It is not differentiated. |
| Matrix state-space | `dsys` (dynamics DSL) | `dy_compile` emits `dsys_continuous` then `dsys_euler_discretize` (slice 2) | Linear matrices are supplied by the user. No derivation from equations. |

## Negative evidence

- No `tests/lang/` or fixture exercises a `grad(f)` or `d/dt` expression; all derivative-bearing programs use `Dual` or `evolves as`.
- `examples/ml/autodiff/` (e.g. `nn_gradcheck.flow`) uses the `Dual` library and manual gradient checks. No symbolic notation is involved.
- No compiler diagnostic mentions an unsupported derivative operator, because no such operator is parsed.

## Semantic classification

- **Symbolic derivative notation:** not supported as language syntax.
- **Forward-mode autodiff:** supported as a library (`lib/stdlib/autodiff.flow`) with `Dual` numbers; correctness and stability are owned by FM-019.
- **Reverse-mode autodiff:** supported as library helpers (`lib/stdlib/autodiff_reverse.flow`); tape generation is manual.
- **Continuous-time derivative:** supported only as the implicit RHS of `evolves as` (slice 1).

## Open / unverified items

- Whether Flow should ever gain symbolic or implicit differentiation syntax is a design decision; this slice records only current evidence.
- `Dual` is `f32`-only in the inspected helpers; `f64`/unit-bearing differentiation is unverified (FM-019, FM-010).
- No gradient-check test was executed for this slice; FM-019 owns that.

## Verification performed for this slice

- Evidence gathered by searching `compiler/src/` for derivative/gradient/jacobian tokens (none found in parser/expr_type/sem_check), and reading `lib/stdlib/autodiff.flow` and `lib/stdlib/autodiff_reverse.flow` headers at `2168bdcbb`.
- No `compiler/src/` or generated files changed.
- Planned repo gates before PR: `./flow tool doc_links`, `./flow tool script_refs`.
