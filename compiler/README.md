# flowc — Flow compiler written in Flow

`flowc` is the **self-hosting bootstrap** for Flow: a compiler front-end
implemented in Flow itself, run today by the production Python→C host under
[`src/flow/`](../src/flow/).

Stage-A `flowc` is the **default host** for `./flow run` and `./flow compile`
(`FLOW_HOST=flowc`). Use `FLOW_HOST=python` for the full Python language surface
(tests, MLIR, gfx, DSLs). Drivers live under `compiler/build/`; if none exist,
`compiler/scripts/ensure_flowc.sh` bootstraps Gen0 via Phase-A roundtrip.

## How to run

From the repo root (default host = flowc for Stage-A programs):

```bash
./flow run examples/basics/hello_world.flow
FLOW_HOST=python ./flow run compiler/src/main.flow
```

Expected exit: `flowc: PASS` (lexer smoke + in-memory parse tests + disk
fixture parse). **cwd must be the repository root** — the fixture test opens
`compiler/fixtures/hello_subset.flow` relative to cwd (same as `./flow run`).

### Stage-A emit mode (`FLOWC_IN` / `FLOWC_OUT`)

When `FLOWC_IN` is set to a non-empty path, `main` skips self-tests and instead:

1. Reads that `.flow` source
2. Parses (+ Stage-A `flowc_typecheck` **on by default**)
3. Stage-A emit: `flowc_cgen_emit` by default; `FLOWC_BACKEND=js` → `flowc_jsgen_emit`; `FLOWC_BACKEND=fmt` → `flowc_fmt_emit`
4. Writes output to `FLOWC_OUT` if set, otherwise prints the buffer to stdout

Typecheck is **on by default** for fixture/app emits (`driver.flow`, C
`stage_a_driver`, and this emit path). Opt out for frontend modules that still
use unresolved imports/extern the subset checker cannot fully resolve:

- `FLOWC_TYPECHECK=0`
- `FLOWC_NO_TYPECHECK=1`

`FLOWC_TYPECHECK=1` remains an explicit on (redundant with the default).
Roundtrip `compile_module` / self-emit dogfood paths pass `FLOWC_TYPECHECK=0`.

### Multi-file bundle (`FLOWC_BUNDLE=1`)

When `FLOWC_BUNDLE=1`, emit resolves relative imports (`import .sibling` /
`import "path.flow"`) under `FLOWC_DIR` (default: dirname of the input) and
concatenates Stage-A C for deps then entry into one translation unit.
With typecheck on (default), `flowc_bundle_typecheck` checks each module
deps-first with a growing seed of dependency exports (`FLOWC_TYPECHECK=0` opts out).
`flowc_cgen_emit_ex(..., flags)` with `flags&1` skips duplicate `#include`
preambles after the first module. Dotted `import pkg.mod` is skipped for now.
Bundle can also emit a real frontend pair (`lexer.flow` → `token.flow` +
`lexer.flow` in one TU) so `cc -c` needs no `flowc_c_to_hdr.py` `-include`.

```bash
FLOWC_BUNDLE=1 FLOWC_DIR=compiler/fixtures \
FLOWC_IN=compiler/fixtures/bundle_main.flow \
FLOWC_OUT=compiler/build/bundle_main.c \
  ./flow run compiler/src/main.flow
cc -O0 -o compiler/build/bundle_main compiler/build/bundle_main.c
./compiler/build/bundle_main   # expect exit 42

# Frontend dogfood (no -include): token then lexer in one C file.
FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src FLOWC_TYPECHECK=0 \
FLOWC_IN=compiler/src/lexer.flow FLOWC_OUT=compiler/build/bundle_lexer.c \
  ./flow run compiler/src/main.flow
cc -O0 -c compiler/build/bundle_lexer.c -o compiler/build/bundle_lexer.o
```

```bash
FLOWC_IN=compiler/fixtures/stage_a_sum.flow \
FLOWC_OUT=compiler/build/stage_a_sum.c \
  ./flow run compiler/src/main.flow
```

Round-trip (emit → `cc` → run; `stage_a_sum` / `stage_a_for_sum` exit `45`, `stage_a_const` exit `12`, `stage_a_struct` exit `42`, `stage_a_token_consts` dogfood exit `29`, `stage_a_ptr` / `stage_a_cast` / `stage_a_index_assign` / `stage_a_array_else` / `stage_a_float` exit `42`). Also compile-object dogfood for real modules [`src/token.flow`](src/token.flow), [`src/ast.flow`](src/ast.flow), [`src/lexer.flow`](src/lexer.flow), [`src/fileio.flow`](src/fileio.flow), [`src/parser.flow`](src/parser.flow), [`src/cgen.flow`](src/cgen.flow), [`src/typecheck.flow`](src/typecheck.flow), and [`src/resolve.flow`](src/resolve.flow) plus separate [`src/jsgen.flow`](src/jsgen.flow) / [`src/fmt.flow`](src/fmt.flow) dogfood (`compile_module` + `flowc_jsgen_fmt.o`; `FLOWC_BACKEND=js|fmt` fixture smokes — kept out of `flowc_frontend.o` fixed-point); plus two-file link smoke [`fixtures/pkg_add/`](fixtures/pkg_add/) (`import .math` skipped at emit → link `math.o`+`main.o` → exit `42`); plus `FLOWC_BUNDLE=1` smoke [`fixtures/bundle_main.flow`](fixtures/bundle_main.flow) + [`bundle_lib.flow`](fixtures/bundle_lib.flow) → exit `42` (default bundle typecheck); [`bundle_tc_ok.flow`](fixtures/bundle_tc_ok.flow) / [`bundle_tc_bad.flow`](fixtures/bundle_tc_bad.flow); plus typecheck fixtures (`typecheck_ok` → exit `42`, `typecheck_undef` rejected without opt-out):

```bash
./compiler/scripts/roundtrip.sh
# After editing compiler/src/*.flow: FLOWC_FORCE_HOST=1 ./compiler/scripts/roundtrip.sh
```

### Two-file link smoke (`pkg_add`)

First slice of import-aware Stage-A: emit sibling modules separately (imports skipped in the body, as today), keep `export function` as a non-static C symbol, then `cc` link:

```bash
./compiler/scripts/stage_a_link_two.sh
# or with sibling-path resolve check:
FLOWC_RESOLVE_IMPORTS=1 ./compiler/scripts/stage_a_link_two.sh
```

Expect `pkg_add exit=42` (`add(40, 2)`). Fixture: [`fixtures/pkg_add/math.flow`](fixtures/pkg_add/math.flow) + [`fixtures/pkg_add/main.flow`](fixtures/pkg_add/main.flow).

Stage-A dogfoods `token` + `ast` + `lexer` + `fileio` + `parser` + `cgen` + `typecheck` + `resolve` as C objects (`lexer`/`parser`/`cgen`/`typecheck`/`resolve` compile with headers derived via `scripts/flowc_c_to_hdr.py`; `extern` blocks get `#include <stdio.h>` + `#include <string.h>`). Ends with a relocatable link smoke (`cc -r` → `compiler/build/flowc_frontend.o`) so cross-module symbols resolve, then builds both Stage-A drivers (C host + Flow-written `driver.flow` with CLI argv) and smokes `stage_a_sum` → exit `45`. Roundtrip finishes with a mini self-host (`scripts/stage_a_self_emit.sh`): prefers Flow `stage_a_driver_flow` CLI (C driver fallback) to re-emit those eight frontend sources → `cc -c` → `flowc_frontend_self.o`, then emits `driver.flow` → `self_driver.o` and links **Stage-A Flow driver + self frontend** (`stage_a_driver_flow_self`) — smoke `stage_a_sum` → exit `45`. Gen2 (`scripts/stage_a_self_emit_g2.sh`): `self.o` drives another emit → `flowc_frontend_g2.o`, then `cmp` fixed-point (`self.o` == `g2.o`), C `stage_a_driver_g2` + Flow `stage_a_driver_flow_g2` smokes (`stage_a_sum` → exit `45`), and a gen3 token emit that must match `self_token.c` / `g2_token.c`.

### Stage-A driver (`flowc` frontend `.o` + tiny C main)

First binary that links Stage-A-emitted frontend objects with a hand-written C host (CLI argv fallback):

```bash
# After roundtrip (or scripts/stage_a_driver.sh once .o + headers exist):
./compiler/build/stage_a_driver \
  compiler/fixtures/stage_a_sum.flow \
  compiler/build/driven_sum.c
cc -O0 -o compiler/build/driven_sum compiler/build/driven_sum.c
./compiler/build/driven_sum   # expect exit 45
```

Host sources: [`host/stage_a_driver.c`](host/stage_a_driver.c), ABI header [`host/flowc_frontend.h`](host/flowc_frontend.h) (includes generated `compiler/build/*_flowc.h`). The driver does libc file I/O; parse + cgen come from `flowc_frontend.o`.

### Flow Stage-A driver (`driver.flow` + `flowc_frontend.o`)

Flow-written driver module ([`src/driver.flow`](src/driver.flow)): Stage-A-emitted alone (imports skipped → no duplicate parser/cgen bodies), then linked with `flowc_frontend.o`. Prefers CLI argv; getenv kept for compatibility:

```bash
./compiler/build/stage_a_driver_flow \
  compiler/fixtures/stage_a_sum.flow \
  compiler/build/driven_sum_flow.c
# or: FLOWC_IN=... FLOWC_OUT=... ./compiler/build/stage_a_driver_flow
cc -O0 -o compiler/build/driven_sum_flow compiler/build/driven_sum_flow.c
./compiler/build/driven_sum_flow   # expect exit 45
```

### Stage-A Flow driver + self frontend

After `stage_a_self_emit.sh`, both the driver and the frontend are Stage-A-emitted Flow (only libc + `cc` remain outside). Emit `driver.flow` → `self_driver.c` (imports skipped), compile with `self_*.h`, link against `flowc_frontend_self.o`:

```bash
./compiler/build/stage_a_driver_flow_self \
  compiler/fixtures/stage_a_sum.flow \
  compiler/build/driven_sum_flow_self.c
cc -O0 -o compiler/build/driven_sum_flow_self compiler/build/driven_sum_flow_self.c
./compiler/build/driven_sum_flow_self   # expect exit 45
```

Gen2 links the same `self_driver.o` against `flowc_frontend_g2.o` → `stage_a_driver_flow_g2` (same smoke). The hand-written C host ([`host/stage_a_driver.c`](host/stage_a_driver.c)) remains as a fallback.

Package metadata: [`flow.toml`](flow.toml) (`name = "flowc"`, entry
`src/main.flow`).

## Python ports

- [`src/claim_address.flow`](src/claim_address.flow) — Claim Coordinates (`flowc_claim_*`); demo: `./flow run examples/compilers/claim_address_demo.flow`

## Module map

| Module | File | Role |
|--------|------|------|
| `token` | [`src/token.flow`](src/token.flow) | Token kinds, keywords, `Token` / `Lexer` structs |
| `lexer` | [`src/lexer.flow`](src/lexer.flow) | Streaming lexer (`flowc_lexer_new` / `flowc_lexer_next`) |
| `ast` | [`src/ast.flow`](src/ast.flow) | Tagged AST arena (index-based children / sibling chains) |
| `parser` | [`src/parser.flow`](src/parser.flow) | Recursive-descent parser for a core subset |
| `fileio` | [`src/fileio.flow`](src/fileio.flow) | libc `fopen`/`fread`/`fwrite` helpers (`flowc_read_file`, `flowc_write_file`) |
| `cgen` | [`src/cgen.flow`](src/cgen.flow) | Stage-A AST→C buffer emitter (`flowc_cgen_emit` / `flowc_cgen_emit_ex`; self-tested) |
| `jsgen` | [`src/jsgen.flow`](src/jsgen.flow) | Stage-A AST→JS buffer emitter (`flowc_jsgen_emit`; self-tested) |
| `typecheck` | [`src/typecheck.flow`](src/typecheck.flow) | Stage-A name resolution / lightweight checks (`flowc_typecheck`, `flowc_tc_seed_export`; self-tested) |
| `resolve` | [`src/resolve.flow`](src/resolve.flow) | Multi-file import resolve + `flowc_bundle_emit` / `flowc_bundle_typecheck` |
| `fmt` | [`src/fmt.flow`](src/fmt.flow) | Stage-A AST→Flow pretty-printer (`flowc_fmt_emit`; self-tested) |
| (tests / emit) | [`src/main.flow`](src/main.flow) | Smoke tests; env-gated Stage-A emit (`FLOWC_IN` / `FLOWC_OUT` / `FLOWC_BUNDLE`); `FLOWC_BACKEND=js|fmt` (else C); typecheck default on (`FLOWC_TYPECHECK=0` / `FLOWC_NO_TYPECHECK=1` opt-out) |
| `driver` | [`src/driver.flow`](src/driver.flow) | Flow Stage-A driver (CLI argv + getenv + optional `FLOWC_BUNDLE`); emit alone, link `flowc_frontend.o` / `_self.o` / `_g2.o` |
| `claim_address` | [`src/claim_address.flow`](src/claim_address.flow) | Claim Coordinates (`flowc_claim_*`; Python port; `./flow run` demo) |
| Stage-A host | [`host/stage_a_driver.c`](host/stage_a_driver.c) | Tiny C `main` linking `flowc_frontend.o` (CLI argv fallback; kept) |

Parse tests use in-memory byte fixtures plus disk fixture
`fixtures/hello_subset.flow`.

## Supported syntax (parser)

What `flowc_parse_program` actually accepts:

**Trivia**
- [x] `#` line comments (lexer skip; including mid-line after statements)

**Top-level**
- [x] `function name(params) -> Type { ... }` / omit `-> Type` for void
- [x] `struct Name { field: Type, ... }` (Stage-A emit: `typedef struct Name { int32_t … } Name;`)
- [x] `extern { ... }` — **brace-matched skip only** (body not typed/parsed; Stage-A: `#include <stdio.h>` + `#include <string.h>` when present; no libc prototypes — would clash with headers)
- [x] `import .sibling { a, b }` / `import pkg.mod { … }` / `import "path.flow"`
- [x] `export function` / `export struct` / bare `export a, b`
- [x] `const Name: Type = expr` / `export const Name: Type = expr` (Stage-A: non-export → `static const int32_t`; export → linkable `const int32_t`)
- [x] forward `function name(...) -> T` (no body) — Stage-A emits `ret name(...);` prototypes

**Statements**
- [x] `let name: Type = expr` / `let mut name: Type = expr` (Stage-A: typed emit — `int32_t` / `uint8_t` / `int64_t` / `float`/`double` / `T*` / struct name)
- [x] `return expr`
- [x] `if cond { ... }` / `if ... else { ... }` (Stage-A: clean `} else {` brace chain)
- [x] `while cond { ... }`
- [x] `for name in lo to hi { ... }`
- [x] `name = expr` / `name.field = expr` / `name[i] = expr` / `name[i].field = expr` (AST_ASSIGN: a=lhs, b=rhs)
- [x] expression statements (e.g. calls)
- [x] `break` / `continue`

**Expressions**
- [x] integer literals, float literals `1.5` (AST_FLOAT=34; Stage-A: `1.5f` for f32 lets, `1.5` for f64), string literals `"…"` (Stage-A: copied as C string constants, e.g. `puts("ok")`)
- [x] `true` / `false` / `null` (Stage-A: `null` → `NULL`)
- [x] identifiers, calls `f(a, b)`, `(expr)`
- [x] unary `!` / `-` / `&` (address-of; Stage-A emit: `(&expr)`)
- [x] binary `||` `&&` / keyword `or` `and` / `==` `!=` `<` `<=` `>` `>=` `+` `-` `*` `/` `%` (precedence climbing; `%` same prec as `*` `/`; Stage-A emit: ` % `)
- [x] postfix `expr.field` / `expr[i]` (Stage-A emit: `(expr).field` / `base[index]`)
- [x] `expr as Type` cast (AST_CAST=32; Stage-A emit: `(ctype)(expr)`)
- [x] struct literals `Type { field: expr, ... }` (lookahead requires `ident :` after `{` so `while i < n {` is not a lit; Stage-A emit: `(Name){ .f = e, … }`)

**Types**
- [x] bare type identifiers (`i32`, `f32`→`float`, `f64`→`double`, `string`→`const char*`, `void`, …; Stage-A emit: `void` return types)
- [x] `ptr<T>` / `array<T, N>` (via `AST_TYPE` child/`ival` tags; Stage-A emit: `ptr<i32>`→`int32_t*`, `ptr<u8>`→`uint8_t*`; `array<T,N>` lets → `T name[N] = { … }`; ptr lets cast init)
- [x] array literals `[e1, e2, …]` (AST_ARRAY_LIT=33; Stage-A emit: `{ e1, e2, … }`)
- [x] omitted `-> Type` on functions → void; bare `return` in void bodies

**Also parsed (see self-tests):** `import` / `export` program items.
Lexer also tokenizes floats, string literals, brackets, `.`, etc.

## NOT YET

- Full type checking / semantic analysis — **partial:** lightweight name-resolution
  typecheck (subset) in [`src/typecheck.flow`](src/typecheck.flow) (`flowc_typecheck`:
  duplicate fns / `const` / `let` in same block, undef idents, assign to unknown
  name, unknown calls, call arity vs declared params, void vs value returns,
  obvious i32/string return mismatch, `break`/`continue` outside loop, unknown
  struct field on typed base / struct lit). Linked into `flowc_frontend.o` /
  self / g2. On by default on emit; opt out with `FLOWC_TYPECHECK=0` or
  `FLOWC_NO_TYPECHECK=1` so frontend dogfood still emits)
- Multi-file package resolve beyond Stage-A MVP — **partial:**
  [`src/resolve.flow`](src/resolve.flow) loads `import .sibling` / `import "path"`
  under `FLOWC_DIR` and `flowc_bundle_emit` concatenates C (deps then entry);
  dotted `pkg.mod` still skipped; `flowc_bundle_typecheck` seeds dep exports
  across modules (Stage-A; not full cross-file typing)
- Full language surface (effects, generics, and most of what production
  `src/flow/` uses); Stage-A `cgen` remains a subset buffer emitter
- Flow driver as the sole host (today: Python host still bootstraps the
  first emit; after self-emit, `stage_a_driver_flow_self` is fully
  Stage-A Flow driver + self frontend; C `stage_a_driver` remains a
  fallback)
- Compiling production `src/flow` with `flowc`
- Note: Stage-A already round-trips `examples/basics/fibonacci.flow` twin
  (`compiler/fixtures/stage_a_fib.flow` → exit 55) via `./compiler/scripts/roundtrip.sh`

### Stage-A vs `examples/basics`

Batch smoke (emit → `cc` → run) for Stage-A-clean basics (`fibonacci`,
`hello_world`, `factorial`, `gcd`, `palindrome`, `prime_numbers`, `loops`,
`power`, `bubble_sort`, `simple_search`):

```bash
./compiler/scripts/emit_basics.sh
# Under host pressure / Gatekeeper delays: FLOWC_EMIT_ONLY=1 ./compiler/scripts/emit_basics.sh
```

Expect `pass=10`. Power returns 1024 → process status `0`.

Python ports (Claim Coordinates / math prose / premise instantiate / know):
see [docs/project/python-in-flow.md](../docs/project/python-in-flow.md);
`./compiler/scripts/smoke_math_prose.sh` and `./compiler/scripts/smoke_know.sh`
check generated C string constants.

| Example | Stage-A clean? | Notes |
|---------|----------------|-------|
| [`hello_world.flow`](../examples/basics/hello_world.flow) | yes | `#` comments; exit 0 |
| [`fibonacci.flow`](../examples/basics/fibonacci.flow) | yes | recursive; exit 55 |
| [`factorial.flow`](../examples/basics/factorial.flow) | yes | exit 120 |
| [`gcd.flow`](../examples/basics/gcd.flow) | yes | `%` / while; exit 14 |
| [`power.flow`](../examples/basics/power.flow) | yes | exit 1024 → process status 0 |
| [`loops.flow`](../examples/basics/loops.flow) | yes | while; exit 50 (5170 mod 256) |
| [`prime_numbers.flow`](../examples/basics/prime_numbers.flow) | yes | `%` / `\|\|`; exit 10 |
| [`palindrome.flow`](../examples/basics/palindrome.flow) | yes | `/` `%`; exit 1 |
| [`bubble_sort.flow`](../examples/basics/bubble_sort.flow) | yes | while / locals; exit 2 |
| [`simple_search.flow`](../examples/basics/simple_search.flow) | yes | if-chain; exit 5 |
| `simple_for.flow` | partial | needs migration from legacy `0..n` to current `0 to n`, plus `printf` / extern I/O |
| `dot_product.flow` | no | `memref_f32` / legacy `0..n` |
| `declarative_sort.flow` | no | `\|\>` pipe, `println`, extern I/O |
| `type_safety_demo.flow` | no | `type` / `distinct type` / `println` |

`export function` + multi-file `import .math` link smoke: [`fixtures/pkg_add/`](fixtures/pkg_add/) via `stage_a_link_two.sh` (exit 42). Float literals: [`fixtures/stage_a_float.flow`](fixtures/stage_a_float.flow) (exit 42; `40.5f` / `1.5`).

**Self-host loop (frontend modules):** partial — exists via roundtrip +
`scripts/stage_a_self_emit.sh` / `stage_a_self_emit_g2.sh` — driver
re-emits `token`/`ast`/`lexer`/`fileio`/`parser`/`cgen`/`typecheck`/`resolve` →
`flowc_frontend_self.o` → `flowc_frontend_g2.o` (byte-identical fixed
point). Stage-A Flow driver + self frontend (`stage_a_driver_flow_self`)
and gen2 (`stage_a_driver_flow_g2`) close the driver+frontend emit path
(C host kept as fallback). `stage_a_driver_g2` + gen3 token cmp close
another turn of the loop. Not yet “`flowc` compiles all of Flow.”

## Related

- Python→Flow satellites: [docs/project/python-in-flow.md](../docs/project/python-in-flow.md)
  (`claim_address`, `claim_path`, `jsgen`, `fmt`, LSP ordering demo)
- Design open question: [docs/project/Questions.md](../docs/project/Questions.md)
  (“Self-hosting bootstrap strategy”)
- Historical lexer seeds: `examples/compilers/flow_lexer.flow`,
  `flow_identifier_lexer.flow`
- Roadmap status: [ROADMAP.md](../docs/project/ROADMAP.md)
