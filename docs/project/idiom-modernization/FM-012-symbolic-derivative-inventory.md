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

- No `grad(f)` or `d/dt` expression fixture was identified in the original slice. Derivative-bearing programs also use field stencils and the experimental Sofia IR library, described in the follow-up below.
- `examples/ml/autodiff/` (e.g. `nn_gradcheck.flow`) uses the `Dual` library and manual gradient checks. No symbolic notation is involved.
- No compiler diagnostic mentions an unsupported derivative operator, because no such operator is parsed.

## Semantic classification

- **Symbolic derivative notation:** not supported as language syntax.
- **Forward-mode autodiff:** supported as a library (`lib/stdlib/autodiff.flow`) with `Dual` numbers; correctness and stability are owned by FM-019.
- **Reverse-mode autodiff:** supported as library helpers (`lib/stdlib/autodiff_reverse.flow`); tape generation is manual.
- **Continuous-time derivative:** `evolves as` declares an explicit RHS (slice 1); numerical library APIs can also integrate user-supplied derivatives.

## Open / unverified items

- Whether Flow should ever gain symbolic or implicit differentiation syntax is a design decision; this slice records only current evidence.
- `Dual` is `f32`-only in the inspected helpers; `f64`/unit-bearing differentiation is unverified (FM-019, FM-010).
- No gradient-check test was executed for this slice; FM-019 owns that.

## Verification performed for this slice

- Evidence gathered by searching `compiler/src/` for derivative/gradient/jacobian tokens (none found in parser/expr_type/sem_check), and reading `lib/stdlib/autodiff.flow` and `lib/stdlib/autodiff_reverse.flow` headers at `2168bdcbb`.
- No `compiler/src/` or generated files changed.
- Planned repo gates before PR: `./flow tool doc_links`, `./flow tool script_refs`.

## Slice 6: typed PDE expressions and mathematical rendering

Evidence for #1789 at `f5ea0f9a917efefbde71a3d9acbefefda6b5fcba`. This follow-up records the merged experimental Sofia IR (#1703) and the separate mathematical-prose renderer. Neither adds symbolic equation grammar. FM-018 still owns the architectural decision about PDE/field ownership.

### Sofia IR: typed library expressions

The owner is `lib/stdlib/science/sofia_ir.flow`. Nodes carry an operation tag, earlier node indices, a literal value and three integer unit exponents (length, time and dependent quantity; lines 12–44). These are ordinary Flow structs, constructed and validated at runtime; they are not the compiler's typed expression AST or MLIR dialect.

| Facility | Exact source anchor | Positive or negative evidence |
|---|---|---|
| Caller-owned graph, one evolved scalar field | `sofia_ir_new:47–51`, `sofia_ir_push:53–63`, `sofia_ir_field:70–84` | Allocation-free construction; null/full storage and second field rejected by source; dedicated tests for those limits not identified |
| Dimensioned literal | `sofia_ir_constant:87–96` | `test_sofia_ir_diffusion.flow:18–23` constructs diffusivity with exponents (2,-1,0) |
| Addition, subtraction, multiplication | `sofia_ir_binary:98–128`, wrappers 130–140 | Add/sub require equal exponents; multiply adds exponents; `test_sofia_ir_boundary_units.flow:77–81` rejects mismatched addition |
| First/second spatial derivative | `sofia_ir_gradient_x:143–155`, `sofia_ir_laplacian_x:158–170` | Direct field only, length exponent decreases by 1 or 2; advection-diffusion composition in diffusion test 64–76; no nested derivative fixture identified |
| Set RHS and validate DAG | `sofia_ir_set_rhs:173–188`, `sofia_ir_validate:191–233` | RHS must be field/time; earlier operands only; reject invalid tags/field and recheck intermediate exponents; boundary test 61–81 corrupts metadata and checks rejection |
| Numerical derivative evaluation | `sofia_ir_sample:235–252`, `sofia_ir_eval:255–278` | Centered difference and three-point Laplacian, recursive evaluation; diffusion test 55–62 compares exact semidiscrete eigenmode and conserved mass |
| Boundary sampling and RHS | `sofia_ir_rhs_1d:281–297`, `sofia_ir_enforce_boundary:299–306` | Periodic wrapping, fixed Dirichlet endpoints with zero endpoint RHS; boundary test 30–39 preserves a linear steady field, 48–59 rejects invalid BC and NaN spacing/time |
| Time integration | `sofia_ir_step_1d:311–354` | Euler, midpoint RK2, classical RK4; diffusion test 44–62 exercises Euler/RK4; boundary test 42–47, 83–96 rejects invalid step/method and duplicate buffers. Independent RK2 accuracy remains unverified here |

Test paths in this table are under `tests/lang/`. The executable example `examples/science/sofia/symbolic_diffusion.flow:19–24` constructs the heat equation using the following actual API calls (inside the example's main, with caller-owned nodes already declared):

```flow
let mut equation: SofiaIrProgram = sofia_ir_new(nodes, 16)
let u: i32 = sofia_ir_field(&equation, 0, 0, 1)
let dxx: i32 = sofia_ir_laplacian_x(&equation, u)
let alpha: i32 = sofia_ir_constant(&equation, 0.025, 2, -1, 0)
let rhs: i32 = sofia_ir_mul(&equation, alpha, dxx)
if sofia_ir_set_rhs(&equation, rhs) != 0 { return 1 }
```

This graph represents the time derivative of u as diffusivity times the spatial Laplacian of u. The evaluator computes the numerical RHS at each grid location. It does not symbolically differentiate an arbitrary expression, infer discretizations, emit executable source or generate GPU kernels.

The caller supplies grid spacing, timestep, method, boundary values and seven distinct n-element buffers. Raw pointer equality checks do not prove that distinct buffers cannot overlap. Capacity/extent, valid memory and numerical stability remain caller obligations. The code checks positivity for spacing and timestep (including rejection of NaN); finite-value guarantees beyond those checks were not established.

The separate field DSL in slice 2 emits a fixed heat-kernel call from source syntax. Sofia instead interprets a graph composed by library calls. Do not automatically rewrite between them: their API, boundary and integration contracts differ.

### Mathematical English and LaTeX: presentation, not execution

`compiler/src/math_prose.flow` exposes string-to-string renderers for Claim Coordinates. It does not parse executable equations into ASTs or establish theorem validity.

| Renderer | Exact anchor | Evidence and limitations |
|---|---|---|
| Mathematical English | `flowc_flow_expr_to_mathematical_english:1094–1120` | Strips by-clause, normalizes identifiers/geometry, rewrites logical and arithmetic spellings; demo lines 30–55 and 82–85 |
| Generic LaTeX | `flowc_flow_expr_to_latex:1210–1229` | Chooses geometry/analysis renderer or rewrites operators; demo 57–64 |
| Geometry LaTeX | `flowc_geometry_expr_to_latex:1085–1091` | Normalizes geometry vocabulary; demo 71–80 |
| Analysis LaTeX | `flowc_analysis_expr_to_latex:1198–1207` | Recognizes a limited analysis vocabulary, formats Taylor/sine/near-zero phrases; returns empty string for unrecognized analysis input at 1199; demo 66–69 |

The demo is `examples/compilers/math_prose_expr_demo.flow`. It supplies quoted strings, not executable mathematical declarations. In particular, derivative-looking identifiers such as `sin_prime_at_zero` are text inputs in the demo, not differentiation operators.

The actual consumers include `compiler/src/proof_doc.flow:2007,2021–2022,3208–3209` (proof document lines) and `compiler/src/know.flow:300–302` (knowledge presentation). Their calls demonstrate the direction of transformation: existing claim text becomes prose or LaTeX, not the reverse. A complete malformed-input/escaping contract is unverified; the rendering demo is not a parser rejection test.

### Verification and scope

The original merged #1703 reported passing both new IR tests and 329/329 language tests at its initial head. That is historical CI evidence, not a current-revision result. The pinned sources include subsequent validation regressions. No new execution was possible in this workspace; the exact commands for reviewers are:

```sh
./flow run tests/lang/test_sofia_ir_diffusion.flow
./flow run tests/lang/test_sofia_ir_boundary_units.flow
./flow run examples/science/sofia/symbolic_diffusion.flow
./flow run examples/compilers/math_prose_expr_demo.flow
./flow tool compiler/scripts/smoke_math_prose.flow
./flow tool compiler/scripts/parity_proofs.flow
./flow tool doc_links
./flow tool script_refs
```

No compiler/library code or fixtures changed. C/MLIR runtime equivalence, GPU lowering, arbitrary PDE syntax, general differentiation and solver-IR stabilization remain unverified or explicitly outside this slice.
