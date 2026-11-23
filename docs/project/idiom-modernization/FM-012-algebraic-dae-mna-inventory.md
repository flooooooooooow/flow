# FM-012 slice 3: algebraic residuals, DAE and MNA inventory

Status: evidence inventory for [#1740](https://github.com/flooooooooooow/flow/issues/1740) and FM-012, base `2168bdcbb` (post #1756). This is a discovery document. It does not approve semantics, assign feature status, or complete FM-012. Companion to [slice 1](FM-012-flow-evolution-inventory.md) (flow/evolution equation syntax) and [slice 2](FM-012-dynamics-field-inventory.md) (matrix dynamics and restricted field lowering). Operator precedence/type constraints for the equation forms that *do* exist are covered separately in `docs/LANGUAGE_SPEC.md` section 4.2 (PR #1759).

## Scope and non-scope

**In scope (this slice):** whether Flow has any language-level surface for algebraic equations, residuals, implicit DAE or modified nodal analysis; where those concerns are actually handled (library vs. compiler); and the documented counterexample that motivates keeping them out of `evolves`.

**Out of scope for this slice:**

- ODE RHS via `evolves as` (slice 1).
- Matrix state-space `dsys` and restricted 1D heat field (slice 2).
- Typed symbolic PDE DAG (PR #1703, science scope) and Sofia.
- Numeric integrator internals and `circuit.flow` implementation details beyond their documented public contract.
- C/MLIR target equivalence for any of these forms (still `unverified`).

## Finding: no language syntax for algebraic equations or DAE

Search of `compiler/src/` (parser, lexer, flow_blocks, dynamics_dsl, field_dsl, expr_type, sem_check) and `lib/` finds no grammar, keyword or lowering path for an algebraic equation, residual or implicit DAE. Specifically:

- No token or parser rule for `=` as an equation (as opposed to assignment/binding), for `0 = f(x)`, for `residual`, for `constraint`, or for a DAE index.
- `flow_blocks.flow` treats `evolves as` as the only continuous derivative form; a state has exactly one derivative and the RHS must be pure (slice 1). There is no `algebraic`/`constraint` member in a `flow` block.
- `dynamics_dsl.flow` (`dsys`) describes explicit numeric state-space matrices (`A`, `B`, `C`, `D`) with a discrete/continuous mode and an Euler discretisation; it does not accept a general nonlinear algebraic equation or infer matrices from equations.
- `field_dsl.flow` accepts only `T evolves as laplacian(T)` (with at most one multiplier) on a `Line` domain; no algebraic constraint on a field.
- `math_prose.flow` is a rendering helper for claim coordinates (LaTeX type names, carrier/structure phrases); it is not an executable equation surface and not a parser for mathematical notation.

Conclusion: algebraic residuals, index-1 DAE and MNA are **not** language features. They are library-level concerns, and the language's only continuous-time construct is the explicit ODE RHS in `evolves as`.

## Where these concerns are actually handled

| Concern | Owner | Evidence anchor | Notes |
|---|---|---|---|
| Modified nodal analysis (linear/nonlinear circuits, DC operating point, transient companion models, Newton-Raphson) | `lib/stdlib/circuit.flow` | module header documents MNA: node-voltage unknowns plus branch currents for V/E/L; KCL rows; backward Euler and trapezoidal companion models; `pnjlim`; caps `CIRC_MAX_NODES 80`, `CIRC_MAX_EXTRA 80`, `CIRC_MAX_DIM 160`, `CIRC_MAX_ELEMS 256`; dense LU with reuse when the matrix is constant | This is a library concern. It is not a language syntax concern. Allocates workspace once; `circ_finalize` returns false on cap overflow rather than truncating. |
| ODE-shaped circuits (RC, RL, RLC, LC, logic gate delays) | `flow` blocks with `evolves as` | `examples/circuits/rc_rl_rlc.flow`, `lc_tank.flow`, `logic_delays.flow`, `chua.flow` (three `evolves as` lines) | Chosen where the circuit is "an ODE in disguise" (README). |
| Ideal voltage source / algebraic loop counterexample | documented in `lib/stdlib/circuit.flow` header and `examples/circuits/README.md` | "an ideal voltage source has no state to integrate at all", so `v evolves as ...` cannot be written for a node pinned by a source; use MNA | This is the explicit anti-example that motivates FM-013's domain distinction. |
| Autodiff (forward/reverse) | `lib/stdlib/autodiff.flow`, `lib/stdlib/autodiff_reverse.flow` | `Dual` struct with `val`/`grad`; `dual_var` seeds ∂/∂x; reverse mode via tape/effects | Derivatives are computed with a library type. No symbolic notation surface such as `grad(f)` or `d/dt` exists. |

## Negative evidence (what is rejected or absent)

- No compiler fixture under `compiler/fixtures/` exercises an algebraic equation, residual or DAE; the dynamics/field fixtures cover only `evolves as`, `dsys` matrices and the restricted heat field.
- No `tests/lang/` file constructs an implicit equation; the circuit examples are the only DAE-flavoured programs and they use the `circuit` library rather than flow blocks.
- `examples/circuits/README.md` states the rule explicitly: four of thirteen examples carry `flow` blocks; `rc_rl_rlc` carries both so the two routes compare on a problem with a known answer. The choice is per-circuit, documented in each file header.

## Semantic classification

- **Algebraic residual / implicit equation:** `not supported` as language syntax. Expressible only as library code (MNA matrix assembly) or, where the system reduces to an ODE, as `evolves as`.
- **Index-1 DAE:** `not supported` as language syntax; same route as above. No index reduction, no consistent initialisation, no algebraic-loop detection in the compiler.
- **MNA:** supported as a library (`lib/stdlib/circuit.flow`) with documented caps and measured accuracy in `examples/circuits/`; not a compiler feature and not subject to the flow-block parity gate.
- **Symbolic differentiation:** not supported as notation; available only via the `Dual`/tape library (FM-019 owns that audit).

## Open / unverified items

- Whether any future syntax for algebraic constraints should exist at all is a design decision (FM-013, `decision_gate: architecture`); this slice records only current evidence.
- C/MLIR target status for `circuit.flow` (it is plain Flow + extern C math) is `unverified` here; it is not part of the MLIR corpus manifest.
- The `examples/circuits/` measured-error claims are example-level, not compiler-level, and are owned by FM-032.

## Verification performed for this slice

- Evidence gathered by reading `lib/stdlib/circuit.flow` header, `examples/circuits/README.md`, `lib/stdlib/autodiff.flow` header, and searching `compiler/src/` for algebraic/equation/residual/constraint surfaces (none found) at `2168bdcbb`.
- No `compiler/src/` or generated files changed.
- Planned repo gates before PR: `./flow tool doc_links`, `./flow tool script_refs`.
