# FM-012 slice 2: matrix dynamics and field equation inventory

Evidence for #1744 at base revision `2539febcca52a3f8586b7a6eeeb7c96903ca96cb`. Companion to [slice 1](FM-012-flow-evolution-inventory.md). Discovery only; no feature approval or compiler change.

## Distinguish the semantic owners

Both of these DSLs expand to ordinary Flow source before parsing. They do not establish a general symbolic differentiation, equation-solving or dimensional-analysis facility.

| Surface | Implementation owner and exact anchor | Lowering/semantics | Positive evidence | Negative or absence evidence |
|---|---|---|---|---|
| `dsys Name { discrete; dt ...; n ... m ... p ...; A ...; B ...; C ... }` (items on separate lines) | `compiler/src/dynamics_dsl.flow:2986–3062`, `dy_parse` | `dy_compile:3581–3641` emits flat numeric arrays and Matrix values with shapes n×n, n×m, p×n; calls `dsys_discrete` | `examples/dynamics/ga_dsys_syntax.flow:10–17`; `compiler/fixtures/dynamics_dsl/ex_ga_dsys_syntax.expected:18–24` | `dy_validate_raw:2803–2878` requires n,p positive and m nonnegative; when matrices are supplied, rejects mismatched entry counts. Redeclaration rejected at 3049–3058. |
| `continuous` in a `dsys` block | `dy_parse:3013–3018` | `dy_compile:3604–3632` emits `dsys_continuous` then `dsys_euler_discretize` | Source emitter establishes the call sequence; a dedicated continuous golden/runtime case was not inspected in this slice | No arbitrary nonlinear RHS or higher-order solver is established by this path |
| `horizon Name finite N` / `horizon Name infinite gamma G` | `dy_parse:3064–3089` | `dy_compile:3568–3580` emits `horizon_finite` / `horizon_infinite` | Same GA example, lines 19–20 and expansion lines 18–19 | Invalid horizon syntax diagnosed at 3087–3088; numeric domain constraints not audited |
| `field T : f64[32] on Line` | `compiler/src/field_dsl.flow:335–401` (`fx_match_field`), `fx_parse:803–840` | `fx_emit_helpers:702–747` emits `T_field_n` and `T_field_step(u,next,r)` | `examples/evolution/heat_diffusion.flow:20–22`; multiplier golden below | Literal decimal size and f64 only in matcher; domain must be Line, size > 1, unique names, limit 64 (805–821) |
| `T evolves as laplacian(T)` / `c * laplacian(T)` / `laplacian(T) * c` | `fx_match_evolve:429–460`; `fx_match_lap` area 461–550; `fx_parse:948–985` | `fx_emit_helpers:719–728` calls `heat_euler_step_1d(u,next,N,r * (c),left,right)` with optional coefficient; imports `stdlib/dynamics/pde.flow` at 1061–1063 | `compiler/fixtures/field_dsl/ok_post_mul.flow:1–13`, `.expected:5–24`; runtime checks lines 14–29 | Only same-field Laplacian shape accepted; at most one multiplier; missing evolution rejected at 991–1004 |
| `boundary T { left = A right = B }` | `fx_match_boundary_head:404–428`; `fx_parse:842–946` | `fx_emit_helpers:729–740` passes endpoint expressions to heat step; absent boundary defaults both endpoints to 0.0 | `tests/lang/test_field_inline_boundary.flow:3–26` verifies two inline boundaries and subsequent declarations survive, and numerical endpoint/interior values | Field must already be declared (847–851), both sides required when boundary block supplied (928–937) |

## Matrix dynamics is not symbolic differentiation

The pre-parser `dy_expand:4370–4385` calls `dy_parse` and `dy_compile`, with the module header at lines 1–10 identifying the historical Python reference. A `dsys` declaration describes explicit numeric state-space matrices, not equations from which the compiler infers matrices. The mode defaults to discrete, dt to 0.1, and n/m/p to 2/1/1 (2993–3004). These defaults are source observations, not recommendations.

The discrete example contains a state transition matrix A, input matrix B and observation matrix C. Its corresponding expansion constructs `DynamicalSystem` via `dsys_discrete(2,1,1,0.1, ...)`. The continuous mode produces a separate continuous object and immediately calls the Euler discretization routine; the exact stdlib numerical implementation is not audited here.

The related `represent linear` path is a particularly important negative anchor: `dy_rep_to_dsys:2356–2368` rejects absent A coefficients, explicitly stating automatic Jacobian linearization is not implemented even when an operating point was provided. A dimensions are inferred from a square matrix or checked against explicit n at 2370–2403. This section is source evidence only; a positive represent fixture and derivative-to-matrix equivalence remain unverified.

The `dsys` parsing loop does not explicitly diagnose every unknown item inside the block (3033–3042). Do not infer that accepting an arbitrary line means its meaning is implemented. No `d/dt` or Unicode partial-derivative notation is evidenced in this source's matrix lowering. This is not a global assertion about other compiler modules.

## Concrete field fixture

The following excerpt is verbatim from `compiler/fixtures/field_dsl/ok_post_mul.flow` (lines 1–7):

```flow
const alpha: f64 = 0.3

field V: f64[ 008 ] on Line
V evolves as laplacian( V ) * alpha
boundary V {
    left=0.5 right=1.5
}
```

The golden normalizes the size and produces:

```flow
const V_field_n: i32 = 8

function V_field_step(
    u: ptr<f64>,
    next: ptr<f64>,
    r: f64
) -> void {
    heat_euler_step_1d(u, next, 8, r * (alpha), 0.5, 1.5)
}
```

The companion Q example places the coefficient before the Laplacian and forwards `r * (2)`. For V the fixture checks endpoints 0.5 and 1.5, and interior values 0.94 and 1.06 after a step with r=0.4. For Q it checks 0.2, 0.6, 0.2 around an impulse at r=0.1. This distinguishes actual coefficient lowering from merely accepting the spelling.

The generated API requires caller-controlled buffers and r. It does not infer physical spacing, timestep, stability, boundary type or a general PDE solution from the surface notation. A source-level `field` declaration here is an explicit 1D heat-step convenience, not a symbolic PDE engine.

## Verification surfaces

| Command | Existing gate coverage | Execution in this slice |
|---|---|---|
| `./flow tool compiler/scripts/parity_dynamics_dsl.flow` | Fixtures against .expected/.error; corpus passthrough or mirrored expansion; GA example compiled and executed without Python | Not run |
| `./flow tool compiler/scripts/parity_field_dsl.flow` | Native fixture goldens, passthrough, heat example, inline boundary and coefficient runtime checks | Not run |
| `./flow tool doc_links` | Documentation link integrity | Pending PR CI |
| `./flow tool script_refs` | Script reference integrity | Pending PR CI |

The dynamics gate's end-to-end build explicitly sets `FLOWC_TYPECHECK=0` (script lines 251–256, rationale #988). Do not claim that this proves fully typechecked native bundle support. The field gate intentionally differs from the historical Python expander on corrected multiplier fixtures (script lines 20–22); its independent coefficient runtime gate is at 244–277. The language test `tests/lang/test_dynamics_dsl.flow` evaluates comment and namespace helpers, not numerical state-space semantics.

All cited source and fixture paths were fetched at the pinned base. Local execution was unavailable in this review workspace; no passing current-revision gate is asserted. No compiler, generated files, tests or fixtures changed.

## Remaining FM-012 scope

General symbolic derivative notation, typed PDE, algebraic residuals, implicit/DAE/MNA equations, ordinary equation-like typed functions, math-prose rendering, operator precedence/type constraints outside the inspected DSL matchers, and C/MLIR target equivalence are not established by this slice. Further inventory must identify their actual semantic owners and positive/negative fixtures before making support claims.
