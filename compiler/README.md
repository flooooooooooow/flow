# flowc — Flow compiler written in Flow

`flowc` is the **self-hosting bootstrap** for Flow: a compiler front-end
implemented in Flow itself, run today by the production Python→C host under
[`src/flow/`](../src/flow/).

It is **not** a drop-in replacement for `./flow`. A Stage-A C emitter may be
present (`src/cgen.flow`); `flowc` still cannot compile itself end-to-end.

## How to run

From the repo root:

```bash
./flow run compiler/src/main.flow
```

Expected exit: `flowc: PASS` (lexer smoke + in-memory parse tests + disk
fixture parse). **cwd must be the repository root** — the fixture test opens
`compiler/fixtures/hello_subset.flow` relative to cwd (same as `./flow run`).

### Stage-A emit mode (`FLOWC_IN` / `FLOWC_OUT`)

When `FLOWC_IN` is set to a non-empty path, `main` skips self-tests and instead:

1. Reads that `.flow` source
2. Parses + Stage-A `flowc_cgen_emit`
3. Writes C to `FLOWC_OUT` if set, otherwise prints the buffer to stdout

```bash
FLOWC_IN=compiler/fixtures/stage_a_sum.flow \
FLOWC_OUT=compiler/build/stage_a_sum.c \
  ./flow run compiler/src/main.flow
```

Round-trip (emit → `cc` → run; `stage_a_sum` / `stage_a_for_sum` exit `45`, `stage_a_const` exit `12`, `stage_a_struct` exit `42`, `stage_a_token_consts` dogfood exit `29`, `stage_a_ptr` / `stage_a_cast` / `stage_a_index_assign` exit `42`). Also compile-object dogfood for real modules [`src/token.flow`](src/token.flow), [`src/ast.flow`](src/ast.flow), [`src/lexer.flow`](src/lexer.flow), [`src/fileio.flow`](src/fileio.flow), [`src/parser.flow`](src/parser.flow), and [`src/cgen.flow`](src/cgen.flow):

```bash
./compiler/scripts/roundtrip.sh
```

Stage-A dogfoods `token` + `ast` + `lexer` + `fileio` + `parser` + `cgen` as C objects (`lexer`/`parser`/`cgen` compile with headers derived via `scripts/flowc_c_to_hdr.py`; `extern` blocks get `#include <stdio.h>` + `#include <string.h>`). Ends with a relocatable link smoke (`cc -r` → `compiler/build/flowc_frontend.o`) so cross-module symbols resolve, then builds both Stage-A drivers (C host + Flow-written `driver.flow`) and smokes `stage_a_sum` → exit `45`. Roundtrip finishes with a mini self-host (`scripts/stage_a_self_emit.sh`): the C driver re-emits those six frontend sources → `cc -c` → `flowc_frontend_self.o`. Gen2 (`scripts/stage_a_self_emit_g2.sh`): `self.o` drives another emit → `flowc_frontend_g2.o`.

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

Flow-written driver module ([`src/driver.flow`](src/driver.flow)): Stage-A-emitted alone (imports skipped → no duplicate parser/cgen bodies), then linked with `flowc_frontend.o`. Paths via getenv (host Flow `main` has no argv; Stage-A same):

```bash
FLOWC_IN=compiler/fixtures/stage_a_sum.flow \
FLOWC_OUT=compiler/build/driven_sum_flow.c \
  ./compiler/build/stage_a_driver_flow
cc -O0 -o compiler/build/driven_sum_flow compiler/build/driven_sum_flow.c
./compiler/build/driven_sum_flow   # expect exit 45
```

Package metadata: [`flow.toml`](flow.toml) (`name = "flowc"`, entry
`src/main.flow`).

## Module map

| Module | File | Role |
|--------|------|------|
| `token` | [`src/token.flow`](src/token.flow) | Token kinds, keywords, `Token` / `Lexer` structs |
| `lexer` | [`src/lexer.flow`](src/lexer.flow) | Streaming lexer (`flowc_lexer_new` / `flowc_lexer_next`) |
| `ast` | [`src/ast.flow`](src/ast.flow) | Tagged AST arena (index-based children / sibling chains) |
| `parser` | [`src/parser.flow`](src/parser.flow) | Recursive-descent parser for a core subset |
| `fileio` | [`src/fileio.flow`](src/fileio.flow) | libc `fopen`/`fread`/`fwrite` helpers (`flowc_read_file`, `flowc_write_file`) |
| `cgen` | [`src/cgen.flow`](src/cgen.flow) | Stage-A AST→C buffer emitter (`flowc_cgen_emit`; self-tested) |
| (tests / emit) | [`src/main.flow`](src/main.flow) | Smoke tests; env-gated Stage-A emit (`FLOWC_IN` / `FLOWC_OUT`) |
| `driver` | [`src/driver.flow`](src/driver.flow) | Flow Stage-A driver (`main` + getenv); emit alone, link `flowc_frontend.o` |
| Stage-A host | [`host/stage_a_driver.c`](host/stage_a_driver.c) | Tiny C `main` linking `flowc_frontend.o` (CLI argv fallback) |

Parse tests use in-memory byte fixtures plus disk fixture
`fixtures/hello_subset.flow`.

## Supported syntax (parser)

What `flowc_parse_program` actually accepts:

**Top-level**
- [x] `function name(params) -> Type { ... }` / omit `-> Type` for void
- [x] `struct Name { field: Type, ... }` (Stage-A emit: `typedef struct Name { int32_t … } Name;`)
- [x] `extern { ... }` — **brace-matched skip only** (body not typed/parsed; Stage-A: `#include <stdio.h>` + `#include <string.h>` when present)
- [x] `import .sibling { a, b }` / `import pkg.mod { … }` / `import "path.flow"`
- [x] `export function` / `export struct` / bare `export a, b`
- [x] `const Name: Type = expr` / `export const Name: Type = expr` (Stage-A: non-export → `static const int32_t`; export → linkable `const int32_t`)
- [x] forward `function name(...) -> T` (no body) — Stage-A emits `ret name(...);` prototypes

**Statements**
- [x] `let name: Type = expr` / `let mut name: Type = expr` (Stage-A: typed emit — `int32_t` / `uint8_t` / `int64_t` / `T*` / struct name)
- [x] `return expr`
- [x] `if cond { ... }` / `if ... else { ... }`
- [x] `while cond { ... }`
- [x] `for name in lo to hi { ... }`
- [x] `name = expr` / `name.field = expr` / `name[i] = expr` / `name[i].field = expr` (AST_ASSIGN: a=lhs, b=rhs)
- [x] expression statements (e.g. calls)
- [x] `break` / `continue`

**Expressions**
- [x] integer literals, string literals `"…"`
- [x] `true` / `false` / `null` (Stage-A: `null` → `NULL`)
- [x] identifiers, calls `f(a, b)`, `(expr)`
- [x] unary `!` / `-` / `&` (address-of; Stage-A emit: `(&expr)`)
- [x] binary `||` `&&` / keyword `or` `and` / `==` `!=` `<` `<=` `>` `>=` `+` `-` `*` `/` `%` (precedence climbing; `%` same prec as `*` `/`)
- [x] postfix `expr.field` / `expr[i]` (Stage-A emit: `(expr).field` / `base[index]`)
- [x] `expr as Type` cast (AST_CAST=32; Stage-A emit: `(ctype)(expr)`)
- [x] struct literals `Type { field: expr, ... }` (lookahead requires `ident :` after `{` so `while i < n {` is not a lit; Stage-A emit: `(Name){ .f = e, … }`)

**Types**
- [x] bare type identifiers (`i32`, `string`→`const char*`, `void`, …; Stage-A emit: `void` return types)
- [x] `ptr<T>` / `array<T, N>` (via `AST_TYPE` child/`ival` tags; Stage-A emit: `ptr<i32>`→`int32_t*`, `ptr<u8>`→`uint8_t*`; `array<u8,N>` lets → `uint8_t name[N]`; ptr lets cast init)
- [x] array literals `[e1, e2, …]` (AST_ARRAY_LIT=33; Stage-A emit: `{ e1, e2, … }`)
- [x] omitted `-> Type` on functions → void; bare `return` in void bodies

**Also parsed (see self-tests):** `import` / `export` program items.
Lexer also tokenizes floats, string literals, brackets, `.`, etc.

## NOT YET

- Full type checking / semantic analysis
- Full language surface (effects, generics, and most of what production
  `src/flow/` uses); Stage-A `cgen` remains a subset buffer emitter
- Flow driver as the sole host (today: Python host still bootstraps the
  first emit; C `stage_a_driver` remains the CLI argv fallback; Flow
  `stage_a_driver_flow` is getenv-path MVP)
- Compiling production `src/flow` with `flowc`

**Self-host loop (frontend modules):** partial — exists via roundtrip +
`scripts/stage_a_self_emit.sh` (and a second generation when present) —
driver re-emits `token`/`ast`/`lexer`/`fileio`/`parser`/`cgen` →
`flowc_frontend_self.o`. Flow driver + frontend `.o` closes more of the
emit path, but that is not yet “`flowc` compiles all of Flow.”

## Related

- Design open question: [docs/project/Questions.md](../docs/project/Questions.md)
  (“Self-hosting bootstrap strategy”)
- Historical lexer seeds: `examples/compilers/flow_lexer.flow`,
  `flow_identifier_lexer.flow`
- Roadmap status: [ROADMAP.md](../ROADMAP.md)
