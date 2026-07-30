# Flow North Star — From Vision to Grammar

> Maps every construct in [VISION.md](../../VISION.md) onto concrete, implementable
> grammar and semantics, grounded in what the compiler supports today
> (`src/flow/parser.py`, `src/flow/type_checker.py`, `src/flow/c_generator.py`,
> `src/flow/dynamics_dsl.py`). This is the reference spec for the Helm epic
> **"Vision: Evolution"**. Someone picking up the `evolves-syntax` or
> `time-blocks` card should be able to implement directly from this document.
>
> Status: design document. Nothing in here is implemented unless explicitly
> marked SHIPPED. Aspirational example programs live in
> [`docs/vision/examples/`](examples/) — deliberately outside `tests/` and
> `examples/` so neither `./flow test` discovery (`git ls-files tests examples`)
> nor `scripts/verify_examples.py` (roots: `examples`, `apps`, `benchmarks`)
> picks them up.

## Card status

| Card | Status |
|---|---|
| evolves-syntax | **SHIPPED**: `flow` blocks, `state`/`input`/`output`/`param` members, `evolves as`, Euler `_step` with factored `_derivs`, `_new`/`_init`/`_outputs`; lowering in `src/flow/flow_blocks.py`, example `examples/evolution/pendulum_evolves.flow` |
| time-blocks | design |
| hybrid-events | **SHIPPED** (zero-crossing form): `when x reaches L { x becomes expr ... }` with sign-change detection at step granularity, synchronous resets, hidden `__guard_k_prev` memory; lowering in `src/flow/flow_blocks.py`, example `examples/evolution/bouncing_ball_evolves.flow` |
| constraints | design |
| connect | design |
| represent-linear | design |
| analyze-block | design |
| units | design |

Shipped-scope notes for evolves-syntax: the `solver` block is deferred to the
time-blocks card because its `dt 1 ms` form needs duration literals (§4.1);
`Name_step` already takes caller-supplied dt, so nothing blocks on it. A
`Name_new()` constructor is generated alongside `Name_init` so ordinary Flow
code can construct an instance with declared defaults. Flow members are
limited to `f64` and `f32` in this version. Outputs require an inline map
until `every`/`when` land.

Shipped-scope notes for hybrid-events: the zero-crossing guard form is in.
`when x reaches L` requires a continuous (`evolves`) state and a threshold
built from params and literals; bodies contain `becomes` resets, staged and
assigned together per §3.2, checked after integration in declaration order.
The boolean edge form (§5.1), ordinary statements in event bodies, and
crossing-time refinement (§5.3) stay open on this card. One deliberate
divergence from the §5.3 sketch: the firing test compares strict signs,
`(g < 0) != (g_prev < 0) || g == 0`, and `__guard_k_prev` stores the
post-reset value of g. The sketch's `<=` comparison with a pre-reset store
re-fires on the step after a reset lands the guard state exactly on the
surface (the clamped bounce of A.2 would flip its own reset back every
step). Semantics are otherwise as specified.

---

## 0. Method and global decisions

### 0.1 Grow the seed, don't fork the language

Flow today is a statically-typed general-purpose language (functions, structs,
enums, traits, generics, effects, theorem blocks) compiling to C, with a
*separate* pre-parse dynamical-systems surface (`dsys` / `sense on` /
`ga evolve`, expanded by `src/flow/dynamics_dsl.py` before the real parser ever
sees the source — hook: `src/flow/module_resolver.py:93-94`).

The north-star constructs split across those two channels deliberately:

| Channel | Constructs | Why |
|---|---|---|
| **Real AST** (lexer + `parser.py` + `type_checker.py` + `c_generator.py`) | `flow` blocks, `state/input/output/param`, `evolves as`, `becomes`, `every`, `when`/`reaches`, `always`/`never`, units, `connect` | These are core language semantics; they need type checking, good errors, and composable codegen. Regex expansion cannot scale to them. |
| **Pre-parse expansion** (`dynamics_dsl.py` style) | `represent linear`, `analyze` blocks | They *generate* analysis programs over the existing `dsys` + stdlib-dynamics machinery. Matching the existing architecture gets them shipped fastest, and they can migrate to the AST later without changing surface syntax. |

### 0.2 Contextual keywords only

**Decision:** none of `flow`, `state`, `input`, `output`, `param`, `evolves`,
`becomes`, `every`, `when`, `reaches`, `always`, `never`, `connect`, `unit`,
`represent`, `solver` become reserved words. They are recognized *contextually*
(identifier token + lookahead), exactly because the current lexer keyword table
(`parser.py`, `self.keywords`, ~line 660) turns reserved words into dedicated
token types globally — reserving `state` or `input` would break every existing
program using them as variable names (and they are common). `./flow test` runs
~hundreds of files; zero of them may regress.

Cost of the tradeoff: parse functions need one-token lookahead
(`self.peek()`-style) instead of a clean token-type dispatch, and error messages
must be written by hand for the contextual forms. Accepted.

Two existing tokens are reused: `AS` (`evolves as` — `as` is already
`TokenType.AS`, used for casts) and `ARROW` (`->` in `connect`, already lexed
for return types).

### 0.3 Lowering target

Everything lowers to plain C via the existing `c_generator.py` (structs →
`typedef struct` at `c_generator.py:285/420`; functions → C functions). A flow
never requires a runtime scheduler in v1: it compiles to a struct plus a family
of step functions the embedder (or a generated `main`) calls in a loop. This
keeps the embedded story honest from day one.

---

## 1. `flow Name { ... }` — the flow declaration

### 1.1 Syntax

```
flow_decl      := "flow" IDENT "{" flow_item* "}"
flow_item      := state_decl | input_decl | output_decl | param_decl
                | evolves_stmt | every_block | when_block
                | always_block | never_block | connect_block
                | represent_block | solver_block
state_decl     := "state" IDENT ":" type ("=" expression)?
input_decl     := "input" IDENT ":" type
output_decl    := "output" IDENT ":" type ("=" expression)?   # expr = output map
param_decl     := "param" IDENT ":" type ("=" expression)? constraint?
constraint     := ("<" | "<=" | ">" | ">=") expression         # e.g. param damping : f64 > 0.0
```

Recognition: in the top-level dispatch (`parser.py:parse()`, line ~950, the
`else: raise SyntaxError("Unexpected declaration")` arm), before erroring,
check `current == IDENT("flow") and peek == IDENT and peek2 == LBRACE`. That
triple-lookahead makes `flow` unambiguous with any expression or declaration
start. Same pattern for `unit` (§6).

### 1.2 Relationship to `struct` — decision

**A `flow` is a struct plus dynamics metadata.** `FlowDecl` is a new AST node
*wrapping* a synthesized `StructDecl` whose fields are the flow's `state`,
`input`, `output`, and `param` declarations (in that order), plus compiler-added
bookkeeping fields (`every` accumulators §4.4, previous-step guard values §5.3).
It is *not* sugar that disappears at parse time: the type checker and codegen
need the dynamics sections. But every existing struct facility (field access,
struct literals, passing by pointer) applies to a flow instance for free, and
`Robot { motor : Motor }` composition (§8) is just a struct field of flow type.

Rejected alternative: `flow` as an entirely parallel top-level namespace with
its own instance semantics — needless duplication of the checker's struct
handling (`type_checker.py:407` collect phase) and `monomorphize.py`.

### 1.3 Semantics of the sections

- `state` — persistent, owned by the flow instance, integrated/updated by
  dynamics. Initializer required at `Name_init` time (either in the decl or in
  the init call; decl-initializer wins as default).
- `input` — read-only within the flow each step; written by the embedder or by
  `connect` (§8) before the step.
- `output` — computed each step *after* integration from states/inputs/params.
  `output torque : f64 = k * current` declares the output map inline. An output
  with no `=` must be assigned in exactly one `every`/`when` body, else
  compile error.
- `param` — constant per instance after init. `param damping : f64 > 0.0`
  installs a runtime init-time check in v1 (same trap machinery as §5.4);
  static proving is future work.

### 1.4 Lowering

For `flow Pendulum` codegen emits:

```c
typedef struct {
    double angle;      /* state  */
    double velocity;   /* state  */
    double length;     /* param  */
    /* + hidden fields: every-accumulators, prev guard values */
} Pendulum;

void Pendulum_init(Pendulum* self /*, params & state overrides */);
void Pendulum_derivs(const Pendulum* self, Pendulum_derivs_t* d); /* §2 */
void Pendulum_step(Pendulum* self, double dt);                     /* §2, §4, §5 */
void Pendulum_outputs(Pendulum* self);                             /* §1.3 */
int  Pendulum_check(const Pendulum* self);                         /* §5.4, 0 = ok */
```

`Pendulum_step(self, dt)` is the single entry point per tick and performs, in
order: (1) continuous integration §2.4, (2) `every` blocks due this tick §4.4,
(3) event detection + resets §5.3, (4) output map, (5) invariant checks §5.4.
This ordering is normative.

---

## 2. `x evolves as expr` — continuous dynamics

### 2.1 Syntax

```
evolves_stmt := IDENT "evolves" "as" expression
```

Only legal directly inside a `flow` body, and `IDENT` must name a `state` of
that flow (checker error otherwise; also an error to give one state two
`evolves` statements, or both `evolves` and a `becomes` targeting it from an
`every` block — a state is continuous or discrete, not both. `when` resets §5
*are* allowed on continuous states: that is what "hybrid" means).

Parsing: inside the flow-body loop, a statement starting with `IDENT` whose
next token is `IDENT("evolves")` takes this path; `evolves` is consumed as an
identifier, then `expect(TokenType.AS)` — the existing `as` token. No conflict
with cast expressions: casts are `expr as type` and we consume `evolves` before
`as`, so the cast grammar never sees it. The RHS is an ordinary
`parse_expression()` over states, inputs, params, literals, and pure functions
(`sin`, `cos`, user functions). Multi-line RHS works because the expression
grammar is already newline-tolerant inside a statement.

**Dimension rule (once units land, §6):** `dim(rhs) = dim(x) / Second`.
Until units land, both sides are `f64`/`f32` and only numeric-type agreement is
checked.

### 2.2 Semantics — simultaneous derivative evaluation

All `evolves` right-hand sides in a flow are evaluated against the **pre-step
state**, then all states advance together. This is the mathematical ODE
semantics `x' = f(x, u)`; declaration order of `evolves` statements is
irrelevant and must stay irrelevant. (Tradeoff recorded: sequential/Gauss-Seidel
update can be more stable for some systems but makes program meaning depend on
statement order — rejected.)

### 2.3 Where `dt` comes from — decision

`dt` is **caller-supplied to `Name_step`**, in seconds as `double`. Sources, in
priority order:

1. **Embedding:** user C/Flow code calls `Pendulum_step(&p, dt)` with whatever
   the hardware timer measured. This is the only mode that never lies.
2. **`solver` block** (optional, inside the flow):

   ```
   solver { dt 1 ms  method euler }        # method: euler | rk4 (rk4 later)
   ```

   This sets the *default* fixed step used by generated simulation drivers and
   by `./flow run`, and pins the integration method. It does not change the
   signature of `Name_step`.
3. **Fallback default** for simulation drivers when no `solver` block exists:
   `1 ms`, emitted as a `#define NAME_DEFAULT_DT 1e-3` with a compile-note.

There is deliberately **no global implicit time** — VISION.md's "time is
explicit" principle. A flow that uses `every`/`reaches` but has no `solver`
block and is never given a dt cannot silently run.

### 2.4 Lowering — explicit Euler first, RK4 second

v1 (card `evolves-syntax`) generates explicit Euler with simultaneous update:

```c
void Pendulum_derivs(const Pendulum* s, double* d_angle, double* d_velocity) {
    *d_angle    = s->velocity;
    *d_velocity = -(s->gravity / s->length) * sin(s->angle);
}
void Pendulum_step(Pendulum* s, double dt) {
    double d_angle, d_velocity;
    Pendulum_derivs(s, &d_angle, &d_velocity);
    s->angle    += d_angle * dt;
    s->velocity += d_velocity * dt;
    /* then: every-blocks, events, outputs, checks — §1.4 order */
}
```

The deriv function is generated separately (not inlined) precisely so that
`method rk4` is a pure codegen swap: four `Name_derivs` calls on temporary
state copies, weighted sum, no change to user source or to `Name_step`'s
signature. Stiff/implicit solvers are out of scope (§11).

RHS restrictions enforced by the checker inside `evolves` expressions: no
assignments, no effects/handlers, no calls to functions that are not
provably pure (v1 approximation: stdlib math + user functions without effect
annotations and without `extern`). Tradeoff: this is an under-approximation of
purity; documented error message tells the user to lift impure work into an
`every` block.

---

## 3. `x becomes expr` — discrete update

### 3.1 Syntax

```
becomes_stmt := IDENT "becomes" expression
```

Legal only inside `every` blocks (§4) and `when` handlers (§5) — *not* at flow
top level (a bare top-level `becomes` has no time base) and not in ordinary
functions. Parsed contextually like `evolves` (IDENT + peek `becomes`).
Target must be a `state` or `output` of the enclosing flow.

### 3.2 Semantics — synchronous block update

Within one `every` or `when` body, **all `becomes` right-hand sides read the
pre-block values**; writes land together at block end (classic synchronous /
Lustre-style semantics). So `a becomes b; b becomes a` swaps.

Tradeoff recorded: sequential C-style semantics is what imperative programmers
expect, but it breaks the declarative reading ("this block *is* the transition
relation") and makes reordering statements change meaning. Synchronous wins;
the checker rejects two `becomes` targeting the same variable in one block.
Ordinary `let` bindings and calls inside the block execute sequentially as
normal statements — only `becomes` writes are deferred.

Lowering: snapshot the written-set into locals, evaluate RHSes against the
struct, assign at block end. Cost: one local per written state, zero heap.

---

## 4. `every <duration> { ... }` and time-typed literals

### 4.1 Duration literal syntax

```
duration := NUMBER unit_suffix
unit_suffix := "ns" | "us" | "ms" | "s" | "min"
```

Lexer change (this is the *only* lexer change in the first two cards): after
lexing a NUMBER, if the immediately following token is an identifier that is
exactly a unit suffix **and the parser is in a duration context** — the token
stream keeps them separate; the *parser* composes them. I.e. `every 10 ms`
parses as `every` NUMBER(10) IDENT(ms). `parse_duration()` accepts
NUMBER IDENT and validates the suffix. This avoids lexer statefulness and
keeps `let ms = 3` legal everywhere. `10ms` (no space) is also accepted:
the current NUMBER regex stops at `m`, producing NUMBER(10) IDENT(ms)
naturally.

**Representation decision:** durations canonicalize to **nanoseconds in
`i64`** at parse time (`DurationLiteral(ns: i64)`). Range: ±292 years — enough.
Fractional literals (`0.5 ms`) are exact iff they land on integer ns, else
compile error (no silent rounding of time).

Duration literals are, in v1, valid **only** where a duration is grammatically
expected: `every`, `solver dt`, and (future) `after`/`within`. A general
`Duration` value type is future work under the `units` card (§6.5).

### 4.2 `every` block syntax

```
every_block := "every" duration "{" statement* "}"
```

Flow-body only. Body statements: `becomes`, `let`, `if`/`match`, calls,
`emit` (future). No `evolves` inside `every`.

### 4.3 Semantics

`every P { B }` fires B once per elapsed period P of *simulated/integrated
time* (the accumulation of `dt` passed to `Name_step`) — **not** wall-clock
time. Phase: first firing at t ≥ P (not at t = 0); rationale: `counter becomes
counter + 1` should read 0 during the first period. Multiple `every` blocks
with different periods coexist; blocks due on the same tick fire in
declaration order (recorded decision — they are semantically independent
because of §3.2, but side-effecting calls need a defined order).

If `dt > P` the block fires multiple times per step (catch-up loop), so
slow-stepping a flow does not silently drop discrete ticks. Tradeoff: a huge
dt causes a burst of firings; cap = 1024 iterations then trap (defensive,
recorded).

### 4.4 Lowering

Per `every` block *k*, a hidden `int64_t __every_k_acc` field (ns) in the
struct, initialized 0:

```c
/* inside Name_step, after integration; dt_ns = (int64_t)(dt * 1e9) */
s->__every_0_acc += dt_ns;
while (s->__every_0_acc >= 10000000LL) {        /* 10 ms */
    s->__every_0_acc -= 10000000LL;
    /* block body with synchronous-write staging (§3.2) */
}
```

dt is converted to integer ns once per step; drift is bounded by the ns
truncation per step (documented; acceptable for v1, revisit with rational
accumulators if it bites).

---

## 5. Hybrid events — `when x reaches L { ... }`

### 5.1 Syntax

```
when_block  := "when" when_guard "{" statement* "}"
when_guard  := IDENT "reaches" expression            # zero-crossing form
             | expression                            # boolean edge form
```

Flow-body only. `reaches` is contextual (IDENT + peek `reaches`). In the
`reaches` form, IDENT must be a continuous (`evolves`) state and the level
expression must be constant over a step (params/literals only, v1). Body may
use `becomes` (including on the guarded state — that's the reset map) and
ordinary statements.

### 5.2 Semantics

- `x reaches L` fires when the sign of `g = x − L` at end-of-step differs from
  its sign at the previous step's end (or `g == 0` exactly). Both crossing
  directions fire in v1; directional forms (`reaches L from above`) are
  reserved syntax, not implemented (recorded).
- Boolean form `when cond { }` is **edge-triggered**: fires on false→true
  transitions only. (Level-triggered would re-fire every step and aliases
  `always`; recorded.)
- Resets apply with synchronous semantics (§3.2) *after* integration and
  `every` blocks, before outputs/invariants (§1.4 order). Multiple events
  firing on one step run in declaration order.

### 5.3 Accuracy — honest v1 statement

v1 detects the crossing **at step granularity**: the event handler runs at the
end of the step in which the sign changed, with the state slightly *past* the
surface (e.g. ball marginally below 0). This is the standard first
implementation and is wrong in the well-known ways: events inside a step are
located to O(dt); two crossings within one step are missed; chattering systems
(Zeno) burn the event every step. Mitigations staged in the `hybrid-events`
card as v1.1: linear back-interpolation of the crossing time
`τ = g_prev/(g_prev − g_now)`, re-integrating the sub-step before applying the
reset. Documented, not promised for v1.

Lowering: per `reaches` event *k*, hidden field `double __guard_k_prev`
(initialized from the init state), compared each step:

```c
double g = s->height - 0.0;
if ((g <= 0.0) != (s->__guard_0_prev <= 0.0) || g == 0.0) { /* reset body */ }
s->__guard_0_prev = g;
```

### 5.4 `always { }` / `never { }` — runtime-checked invariants

```
always_block := "always" "{" expression+ "}"     # each line: boolean expr
never_block  := "never"  "{" expression+ "}"
```

Flow-body only. Each expression must type to `bool`. Semantics: after every
completed step (post-events, post-outputs), every `always` expression must be
true and every `never` expression false. Lowering into `Name_check`, which
returns 0 or the 1-based index of the violated clause; `Name_step` calls it
and on violation calls `flow_panic("<flow>.<file>:<line>: invariant
violated: <source text>")` → `abort()`. Under the transpiler's existing
`--lenient` flag, downgrade to one stderr line per clause per run (first
violation only, to avoid log storms — recorded).

Static proving (connecting to the existing `theorem` / `proof_kernel.py`
machinery) is explicitly future work; the grammar carries no proof obligations
in v1. VISION.md's `never { valve.open  pump.off }` conjunction-of-states form
reads as `never { valve.open && pump.off }` — decision: `never` clauses are
each a full boolean expression, one per line; no implicit conjunction magic.

---

## 6. Units of measure — minimal viable version

### 6.1 What exists today

`distinct type Distance = f32` (`parser.py:1445`) gives *nominal* wrappers:
`Distance + Distance` is fine, `Distance + Speed` errors, but `Distance *
Speed` has no meaning and there is no dimensional algebra. The checker stores
them as `SemanticType(kind=DISTINCT, name, base_type)`
(`type_checker.py:441-449`).

### 6.2 Decision — dimension vectors on top of the distinct-type machinery

New contextual top-level declaration (same triple-lookahead trick as `flow`):

```
unit_decl := "unit" IDENT                          # new base dimension
           | "unit" IDENT "=" unit_expr            # derived unit
unit_expr := IDENT | unit_expr "*" unit_expr | unit_expr "/" unit_expr
           | unit_expr "^" INT | "1"               # "1" = dimensionless
```

```flow
unit Meter
unit Second
unit Velocity = Meter / Second
unit Accel    = Meter / Second^2
unit Radian                       # angles are their own base dim (decision)
```

Checker representation: extend `SemanticType` with `dims:
Optional[Tuple[int, ...]]` — an exponent vector over the *declared base units
of the program* (not hard-coded SI-7; a program declares only what it needs,
and stdlib ships an SI prelude). A `unit` decl behaves exactly like
`distinct type X = f64` **plus** a dims vector.

Checking rules (all in the existing binary-op checking path):

- `+`, `-`, comparisons, `becomes`/`evolves` agreement: dims must be equal
  (`Meter + Volt` → "dimensional error: Meter + Volt", satisfying VISION.md's
  `length + voltage` must-not-compile).
- `*`, `/`: dims add/subtract; result type is the canonical unit with that
  vector if one is declared, else an anonymous dimensioned type (printable as
  `Meter*Kilogram/Second^2`).
- Literals are dimensionless; `9.81 as Accel` (existing `AS` cast path) is the
  v1 way to give a literal a unit. **No general unit-suffixed literals in
  v1** (`9.81 m/s^2` needs expression-level grammar surgery; deferred,
  recorded). Duration literals in `every` (§4.1) are the one exception and are
  a closed special case.
- `sin/cos/exp/...` require dimensionless or `Radian` (Radian erases to
  dimensionless at these boundaries — decision; the alternative, forcing
  `angle / 1 rad`, is noise).
- `evolves as` once units exist: `dim(rhs) == dim(lhs) − dim(Second)` (§2.1).

### 6.3 Erasure

All unit types erase to their base numeric type (`f64` unless declared
otherwise) in `c_generator.py` — exactly how distinct types erase today. Zero
runtime cost, zero C-side representation. This is the whole point of the
minimal version: units are a checker-only feature touching lexer not at all,
parser for two small productions, and codegen for nothing.

### 6.4 Explicitly out of scope (recorded)

Unit *inference* through generics (`function integrate<T>(x: T, ...)` over
dimensioned T), rational exponents (`Second^-1/2` shows up in noise densities),
affine units (Celsius vs Kelvin — VISION.md's `temperature > 100 C` reads as
Kelvin-offset; v1 says use `kelvin` or a dimensionless threshold), and
unit-aware printing. Each is listed in §11.

### 6.5 Duration ↔ units bridge

When the `units` card lands, `every`'s duration literals retroactively type as
`Second`-dimensioned constants and `solver dt` unifies with them. Until then
durations are the closed grammar of §4.1. The two cards are deliberately
independent — neither blocks the other.

---

## 7. Where each core feature slots into the compiler

| Feature | Lexer | `parser.py` | `type_checker.py` | `c_generator.py` |
|---|---|---|---|---|
| `flow` decl | — | new arm in `parse()` else-branch (~line 1078); new `FlowDecl` node wrapping `StructDecl` | register struct in collect phase (~line 407); new flow-section checks | struct emission (reuse ~line 285) + generated `_init/_derivs/_step/_outputs/_check` |
| `evolves as` | — | flow-body statement path (IDENT + peek) | state-target check, purity check, (later) dim check | `_derivs` + Euler in `_step` |
| `becomes` | — | flow-body/every/when statement path | target class check, one-writer check | staged synchronous writes |
| durations | — (NUMBER+IDENT composed in parser) | `parse_duration()` | ns range check | `int64_t` constants |
| `every` | — | `parse_every()` | body statement restrictions | accumulator field + catch-up loop |
| `when`/`reaches` | — | `parse_when()` | guard state continuous-check | prev-guard field + sign-change test |
| `always`/`never` | — | `parse_always()` | bool checks | `_check` + `flow_panic` |
| `unit` | — | `parse_unit()` (top-level, contextual) | dims vector algebra on `SemanticType` | erasure (nothing) |
| `connect` | — | `parse_connect()` inside flow body | port existence/direction/type, cycle check | topo-ordered child stepping |

Known grammar conflicts, decided:

- `as` after `evolves` vs cast operator — resolved by consumption order (§2.1).
- `analyze` — collides with the *existing* dsys `analyze plant ga k1 k2 over
  rollout -> report` (`dynamics_dsl.py` docstring, `has_dynamics_dsl` regex
  `^\s*analyze\s+\w+`). Resolution in §9.4.
- `flow`/`unit` as variable names remain legal everywhere (contextual
  recognition requires the `NAME {` / decl shape).
- `every`, `when`, `always`, `never` appear only inside `flow` bodies, so they
  cannot collide with expression statements in functions at all.

---

## 8. `connect { a.out -> b.in }` — composition

### 8.1 Syntax

```
connect_block := "connect" "{" connection* "}"
connection    := IDENT "." IDENT "->" IDENT "." IDENT
```

Flow-body only, in a flow whose fields include flow-typed members:

```flow
flow Robot {
    plant : Motor
    controller : PID

    connect {
        controller.output -> plant.input
        plant.speed -> controller.feedback
    }
}
```

`member : FlowType` inside a flow body is the existing struct-field grammar —
no new parsing; the checker learns that a field whose type is a `flow` makes
this a *composite* flow.

### 8.2 Checking

- LHS must be an `output` (or `state`, explicitly allowed — reading a state as
  a signal is physical) of the named member; RHS must be an `input`.
- Types (and dims, post-units) must match exactly. No implicit scaling.
- Each `input` may have at most one incoming connection; unconnected inputs
  of members must be driven by the parent (parent `every`/`becomes` writing
  `member.input`) or the parent must re-export them as its own `input` —
  otherwise compile error "unconnected input".
- **Algebraic loops:** build the graph whose edges are connections where the
  source is an `output` computed *combinationally from inputs* (an output map
  referencing an input). A cycle through such edges is a compile error in v1.
  Cycles broken by state (motor speed is a state; PID reading `plant.speed`
  is fine) are legal and are the normal case. Recorded tradeoff: true
  algebraic-loop solving (Modelica-style) needs a nonlinear solver at codegen
  time — out of scope.

### 8.3 Lowering

`Robot_step(self, dt)`:

1. Topologically order members by combinational connection edges (state-broken
   edges don't constrain order; ties broken by declaration order —
   deterministic builds).
2. For each member in order: copy each connected source signal into the
   member's input field, then call `Member_step(&self->member, dt)`.
3. Parent-level dynamics (a composite may have its own `state`/`evolves`
   too) integrate before the children by the §1.4 ordering.
4. `Robot_check` = own invariants + `&&` over children's checks.

All members step with the parent's `dt`. Multi-rate composition falls out of
`every` inside the children (a PID with `every 1 ms` composed into a plant
stepped at 100 µs just fires every 10th step). This is a deliberately simple
single-clock model; distributed/multi-clock scheduling (VISION.md `task`
blocks) is not designed here (§11).

---

## 9. `represent linear` / `analyze` — bridging to the existing dsys machinery

### 9.1 What exists today (SHIPPED, the seed)

`dynamics_dsl.py` expands, *pre-parse* (hooked at `module_resolver.py:93`),
these blocks into calls against `lib/stdlib/dynamics/` (`core.flow`,
`state_space.flow`, `gramian.flow`, `attractor.flow`, `ga.flow`,
`ga_analysis.flow`) injected at the top of `main()`
(`inject_dynamics_setup`):

```
dsys plant { discrete  dt 0.1  n 2 m 1 p 1  A 1.0 0.1 0.0 1.0  B 0.0 0.1  C 1.0 0.0 }
horizon rollout finite 50
sense on plant { controllable -> plant_ok  spectral -> rho_open  gramian finite rollout trace -> wc_fin }
ga evolve on plant over rollout -> k1 k2 { population 12 generations 30 mutation 0.3 }
closed plant with k1 k2 { spectral -> rho_cl  stable -> stable_cl }
analyze plant ga k1 k2 over rollout -> report { full }
```

(Working examples: `examples/dynamics/ga_dsys_syntax.flow`,
`ga_full_analysis.flow`.) The seed is *linear systems with explicit matrices*.
The north-star flows of §1–2 are nonlinear and matrix-free. `represent linear`
is the bridge.

### 9.2 `represent linear` — syntax and semantics

Inside a flow body:

```flow
flow Pendulum {
    state angle : f64 = 0.0
    state velocity : f64 = 0.0
    param gravity : f64 = 9.81
    param length : f64 = 1.0

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle)

    represent linear {
        at (angle: 0.0, velocity: 0.0)      # equilibrium / operating point
        inputs ()                            # optional; which inputs enter B
        outputs (angle)                      # which signals form C
    }
}
```

Semantics: linearize `x' = f(x, u)` at the given point: `A = ∂f/∂x`,
`B = ∂f/∂u`, `C` selects the listed outputs. **v1 computes the Jacobians
numerically** (central differences, h = 1e-6·max(1,|x_i|)) at *expansion
time* — the expander evaluates the `evolves` RHS as Python arithmetic (the
RHS grammar of §2.4 is deliberately pure and closed, so a small evaluator over
params + math functions suffices). Symbolic differentiation via the SHIPPED
autodiff is the natural v2 and changes no surface syntax. Requirement:
`at` must bind every state, and params must have values (decl defaults) —
else expansion error.

Lowering: the expander emits a synthesized

```
dsys Pendulum_lin { continuous  dt <solver dt or 0.001>  n 2 m 0 p 1  A <computed...>  C 1.0 0.0 }
```

after which **`sense on Pendulum_lin { ... }` and the whole existing pipeline
work unchanged.** `represent nonlinear` is a recognized no-op (the flow itself
*is* the nonlinear representation); `koopman` / `transfer_function` /
`frequency` are reserved words in the block, rejected with "not yet
implemented" (recorded — no design here).

Note `dsys` today is `discrete`-mode in the examples; the expander's
`DsysDecl.mode` already carries `continuous`. Card `represent-linear` must
verify the stdlib `state_space.flow` handles continuous-mode analysis
(discretize at `dt` via forward Euler `A_d = I + A·dt` as the v1 fallback —
recorded, honest about the approximation).

### 9.3 `analyze Name { ... }` — syntax and desugaring

```
analyze Pendulum {
    poles            # -> eigenvalues of A (spectral data)
    stability        # -> spectral radius < 1 (discrete) / Re λ < 0 (continuous)
    controllability  # -> rank test, needs B ≠ 0
    observability    # -> rank test on (A, C)
}
```

Top-level (like `dsys`), handled by the same pre-parse expander. Desugars to a
`sense on Pendulum_lin { spectral -> Pendulum_poles_rho  controllable ->
Pendulum_ctrb ... }` block plus a generated `Pendulum_analysis` report struct,
reusing `sense`'s existing lowering verbatim. Requires the flow to carry a
`represent linear` block — error otherwise ("analyze needs a linear
representation; add `represent linear { at (...) }`").
`observability` needs a small stdlib addition (gramian.flow has the
controllability machinery; observability is its dual — noted in the card).

### 9.4 The `analyze` grammar collision — decision

`has_dynamics_dsl` already matches `^\s*analyze\s+\w+` for the GA form
`analyze plant ga k1 k2 over rollout -> report { full }`. Disambiguation is
one token of lookahead after the name: **`{` ⇒ vision form; `ga` ⇒ legacy GA
form.** Both remain supported; the expander's `analyze` parser branches on
that token. No deprecation of the GA form (it has passing examples and tests).
Recorded as permanent grammar debt: two meanings of `analyze`, distinguishable
in LL(2), documented in `dynamics_dsl.py`'s docstring when implemented.

---

## 10. Staged implementation plan (Helm epic "Vision: Evolution")

Dependency DAG over the epic's cards:

```
north-star (this document)
    ├── evolves-syntax          # flow decl, state/input/output/param,
    │       │                   #   evolves as, Euler _step/_derivs, solver block
    │       ├── time-blocks     # duration literals, every, becomes, accumulators
    │       │       └── connect         # composition; wants every for multi-rate demos
    │       ├── hybrid-events   # when/reaches, boolean edge form, resets
    │       ├── constraints     # always/never, _check, flow_panic, --lenient demotion
    │       └── represent-linear  # expansion-time Jacobian -> synthesized dsys
    │               └── analyze-block # analyze Name {...} -> sense on <flow>_lin
    └── units                   # unit decls, dims on SemanticType, erasure
                                #   (independent; when landed, retro-types durations §6.5)
```

- **`evolves-syntax`** and **`time-blocks`** are fully decided by this spec
  (§1–4): grammar productions, AST shapes, checker rules, exact generated-C
  shapes, dt sourcing, ordering semantics. No open question blocks them.
  `evolves-syntax` is SHIPPED (see the card status table at the top).
- `hybrid-events` and `constraints` depend only on `evolves-syntax` and can
  proceed in parallel after it.
- `connect` needs `evolves-syntax` + `time-blocks` (multi-rate story).
- `represent-linear` needs `evolves-syntax` (it evaluates `evolves` RHSes);
  `analyze-block` needs `represent-linear`.
- `units` is independent of all of the above and touches disjoint compiler
  code (checker) — good parallel track.

Definition of done for each card includes: examples under `examples/`
(compiling, so they *raise* STATUS.md, never lower it), tier2 green, and
moving the corresponding program from `docs/vision/examples/` into
`examples/` once it compiles.

---

## 11. Open questions (deliberately not decided here)

- **Zero-crossing accuracy / Zeno:** §5.3's step-granular detection is
  O(dt)-wrong; interpolation is sketched but event *chattering* (bouncing ball
  as restitution → 0) has no v1 answer beyond the iteration cap.
- **Stiff systems:** explicit Euler/RK4 only. Implicit solvers need Jacobians
  at runtime (autodiff makes this plausible later) and a linear solver in the
  C runtime.
- **dt jitter vs real time:** `Name_step(dt)` trusts the caller; nothing
  checks deadline overruns. VISION.md's `realtime` / `deploy` / `task`
  scheduling blocks are not designed here.
- **Units:** inference through generics, rational exponents, affine units
  (Celsius), unit-suffixed literals in general expressions (§6.4).
- **Temporal guarantees:** `after disturbance ... within 200 ms` needs a
  monitor-automaton lowering; `within` is reserved but undesigned.
- **`control` / `guarantee` / Koopman / transfer-function representations:**
  vision constructs with no v1 mapping; `ga evolve` remains the only synthesis
  path for now.
- **Emit/events as values:** `emit Overheated` implies an event type and an
  observer; undesigned.

---

## Appendix A — the three north-star programs

Aspirational (do **not** compile today); maintained as files in
[`docs/vision/examples/`](examples/) and inlined here so this spec is
self-contained. Grammar exactly as specified above.

### A.1 Pendulum — continuous + units + analysis

```flow
# docs/vision/examples/pendulum.flow
unit Radian
unit Second
unit RadPerSec = Radian / Second

flow Pendulum {
    state angle    : Radian    = 0.5 as Radian
    state velocity : RadPerSec = 0.0 as RadPerSec
    param gravity  : f64 = 9.81
    param length   : f64 = 1.0

    solver { dt 1 ms  method euler }

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle)

    always {
        angle < 3.15 as Radian
        angle > -3.15 as Radian
    }

    represent linear {
        at (angle: 0.0, velocity: 0.0)
        outputs (angle)
    }
}

analyze Pendulum {
    poles
    stability
    controllability
}
```

### A.2 Ball — hybrid bounce

```flow
# docs/vision/examples/ball.flow
flow Ball {
    state height   : f64 = 10.0
    state velocity : f64 = 0.0
    param gravity  : f64 = 9.81
    param restitution : f64 = 0.8

    solver { dt 500 us }

    height evolves as velocity
    velocity evolves as -gravity

    when height reaches 0.0 {
        velocity becomes -restitution * velocity
        height becomes 0.0
    }

    never {
        height < -0.01
    }
}
```

### A.3 Robot — PID + motor + connect

```flow
# docs/vision/examples/robot.flow
flow Motor {
    state speed   : f64 = 0.0
    state current : f64 = 0.0
    input voltage : f64
    output speed_out : f64 = speed
    param resistance : f64 = 1.2
    param inductance : f64 = 0.05
    param k_emf : f64 = 0.6
    param k_torque : f64 = 0.6
    param inertia : f64 = 0.02
    param damping : f64 > 0.0 = 0.1

    current evolves as (voltage - resistance * current - k_emf * speed) / inductance
    speed   evolves as (k_torque * current - damping * speed) / inertia
}

flow PID {
    state integral : f64 = 0.0
    state prev_err : f64 = 0.0
    input setpoint : f64
    input feedback : f64
    output command : f64
    param kp : f64 = 2.0
    param ki : f64 = 0.5
    param kd : f64 = 0.05

    every 1 ms {
        let err = setpoint - feedback
        integral becomes integral + err * 0.001
        prev_err becomes err
        command becomes kp * err + ki * integral + kd * (err - prev_err) / 0.001
    }
}

flow Robot {
    plant : Motor
    controller : PID
    input target : f64

    connect {
        controller.command -> plant.voltage
        plant.speed_out   -> controller.feedback
    }

    every 10 ms {
        controller.setpoint becomes target
    }

    always {
        plant.current <= 40.0
    }
}
```
