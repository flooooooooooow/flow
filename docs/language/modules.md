# Flow Module System

> **Status:** Phase 1 implemented, dot-path imports, `[paths]`, `export` lists, `export import` re-export. String imports deprecated.  
> **Problem today:** `import "../../../../lib/verify/nat.flow"` breaks when you move a file.  
> `stdlib/` vs `lib/stdlib/` vs `../../`, three dialects, zero confidence.

Flow already has `flow.toml`, domain-prefixed theorems (`nat_add_zero`), and an effect/capability system.
The module system should extend those ideas, not bolt on a second import dialect.

---

## Core Rule

**Imports name modules, not files.**

```flow
import verify.Nat/+ { zero-left, succ-right }
import verify.Nat/+.commutes
import std.math.sin
```

Never:

```flow
import "../../../../lib/verify/nat.flow"   # forbidden
import "../../vulkan_abi/renderer.flow"     # forbidden
```

File paths are the compiler's job. Humans name ideas.

---

## How Resolution Works

```
import verify.nat { nat_zero_add }
        │      │            │
        │      │            └── symbol (must be exported)
        │      └── module path (maps to one file)
        └── package root (from flow.toml or built-in)
```

Resolution order:

1. **Built-in `std`**, ships with the compiler (`lib/stdlib/` today)
2. **Current package roots**, declared in `flow.toml [paths]`
3. **Dependencies**, declared in `flow.toml [dependencies]`
4. **Relative sibling**, `import .sibling` or `import .derived.nat_add_zero` *within the same package only*

No `..` ever. If you need a parent's module, that's a package dependency, say so in `flow.toml`.

---

## `flow.toml` Is the Map

```toml
[package]
name = "flow"
version = "0.7.0"
entry = "examples/verify/math/derived/nat_add_commutes.flow"

[paths]
verify = "lib/verify"          # import verify.nat → lib/verify/nat.flow
examples = "examples"          # import examples.basics.gcd → examples/basics/gcd.flow

[dependencies]
# future: remote packages resolve the same way as local roots
# audio_dsp = { git = "https://github.com/flow-lang/audio-dsp", tag = "v0.3" }
```

| Import | Resolves to |
|--------|-------------|
| `std.math` | `lib/stdlib/math.flow` |
| `std.audio.filters` | `lib/stdlib/audio/filters.flow` |
| `verify.nat` | `lib/verify/nat.flow` |
| `.derived.nat_add_zero` | sibling file in same directory |
| `audio_dsp.reverb` | dependency package (future) |

**Module path = dot-separated logical name.**  
**File path = directory layout underneath a `[paths]` root.**  
They stay in sync by convention, not by counting `../`.

---

## Import Syntax

Five forms. Same keywords as the rest of Flow, explicit, no sigils.

```flow
# 1. Single symbol
import verify.nat.nat_zero_add

# 2. Multiple symbols from one module (preferred)
import verify.nat { nat_zero_add, nat_add_succ }

# 3. Qualified namespace (whole module, use sparingly)
import verify.nat as nat
# later: nat.nat_zero_add

# 4. Sibling within same package
import .derived.nat_add_zero

# 5. Re-export: forward another module's exports as your own
export import .derived.nat_add_zero
```

No `import *`. If you need more than a handful of symbols, your module is too big, split it.

### Aliasing (when domain prefix is noisy locally)

```flow
import verify.derived.nat_add_commutes as nat_add_commutes
```

---

## Export Syntax

Private by default. One export line per file, not `export` on every declaration.

```flow
# lib/verify/nat.flow

# @module verify.nat
# @means  Peano definitions for natural number addition
# @from   https://en.wikipedia.org/wiki/Peano_axioms
# @tier   definitions-only

theorem nat_zero_add(m: Nat) { ... }
theorem nat_add_succ(n: Nat, m: Nat) { ... }

export nat_zero_add, nat_add_succ
```

What this prevents:

- Accidental re-export of internal helpers
- Symbol creep (if it's not exported, it doesn't exist outside)
- Naming debacles (the exported set *is* the public API, review it like a changelog)

For theorems: **if it's not exported, no other package can `assume` it**, forces intentional API surfaces.

---

## Re-export

A package usually wants one name that stands for the whole thing. `export
import` forwards another module's exports as exports of this file.

```flow
# registry/packages/flowlm/src/lib.flow

export import .util
export import .corpus
export import .tokenizer
export import .model
export import .train
export import .gradcheck

export function flm_version() -> i32 {
    return 100
}
```

Consumers name the aggregator and get the whole surface:

```flow
import flowlm.lib { flm_model_init, flm_forward, flm_train_step }
```

Two forms:

| Form | Forwards |
|------|----------|
| `export import .model` | everything `.model` exports |
| `export import .train { flm_train_step, flm_sample }` | only those two symbols |

The brace list is checked the same way an ordinary import's is: each name must
exist in the named module and be exported there.

### The spelling

`export` is already a prefix on declarations (`export function`, `export
struct`) and `import` is already a declaration. `export import` composes two
productions that exist, and it adds no token and no sigil. The parser had an
explicit error reserving that position; it now means re-export.

### What it does not do

- **No copies.** Forwarding binds the declaring module's symbol. Whatever the
  path, each declaration is emitted once. Two modules forwarding the same
  symbol is fine, because it is one symbol.
- **No alias.** `export import verify.nat as nat` is rejected. Re-export
  forwards names; use a plain `import ... as` when you want a local alias.
- **No private leak.** A symbol the source module does not export cannot be
  forwarded.

Re-exports chain. Forwarding a module forwards what that module forwarded.

### Collisions

Forwarding two declarations under one name is an error, and the message names
both source modules:

```
Re-export collision in .../agg.flow: forwarding '.dup_b' brings in a name
that is already exported elsewhere — Symbol 'dup_fn' collision between
.../dup_b.flow and .../dup_a.flow
```

Declaring a name locally that is also forwarded is the same error from the
other side:

```
Re-export collision on symbol 'alpha_one' in .../agg_shadow.flow: re-exported
from .../alpha.flow and also declared locally in .../agg_shadow.flow
```

Both are `SymbolCollisionError`, a `ValueError` subclass.

The self-hosted `flowc` parser does not accept `export import` yet.

---

## `module` Blocks Are Not Namespaces

`module X { ... }` is parsed and then flattened. The name is discarded and the
inner declarations become globals, so the block groups source text and nothing
more. Two blocks in one file declaring the same function name produce duplicate
definitions in the emitted C, and the only error comes from the C compiler.

Namespacing is the file, addressed by its dot path. See
[modules-namespacing.md](modules-namespacing.md) for the exact behavior today,
reproductions of what breaks, and the cost of making blocks real namespaces.

---

## Module Headers (learn in the moment)

Every module file starts with a header, same spirit as theorem headers in [verification.md](verification.md):

```flow
# @module verify.nat
# @means  The two Peano recursion clauses that define addition on naturals.
# @from   https://en.wikipedia.org/wiki/Peano_axioms
# @tier   definitions-only
# @docs   https://flow-lang.org/verify/nat
```

`flow doc verify.nat` renders the header + exported symbols + literature links.
You learn what a module *is* without opening every theorem.

---

## Package Layout Convention

```
flow/
├── flow.toml
├── lib/
│   ├── verify/
│   │   ├── nat.flow              → verify.nat
│   │   └── bool.flow             → verify.bool
│   └── stdlib/                   → std.*  (built-in root)
│       ├── math.flow             → std.math
│       └── audio/
│           └── filters.flow      → std.audio.filters
├── examples/
│   └── verify/
│       └── math/
│           └── derived/
│               ├── nat_add_zero.flow    → examples.verify.math.derived.nat_add_zero
│               └── nat_add_commutes.flow
```

Dots mirror directories. Predictable forever.

---

## Effects & Capabilities Fit Naturally

Effects are symbols. Capabilities are symbols. Same import rules.

```flow
import std.io { effect Log }
import my_app.handlers { capability ConsoleLogger }

handle Log with ConsoleLogger {
    Log.emit("verified and running")
}
```

No special-case import path. The effect system was already capability-based, modules just deliver capabilities from named packages.

---

## Verification Integration

Theorem tiers and module exports work together:

| Module `@tier` | What you can import |
|----------------|---------------------|
| `definitions-only` | Only `definition` tier theorems |
| `derived` | Theorems that list `needs` from imported modules |
| `axioms` | Logical foundations |

```flow
# examples/verify/math/derived/nat_add_zero.flow

# @module examples.verify.math.derived.nat_add_zero
# @means  n + 0 = n, derived by induction
# @tier   derived

import verify.nat { nat_zero_add, nat_add_succ }

theorem nat_add_zero(n: Nat) { ... }

export nat_add_zero
```

```flow
# examples/verify/math/derived/nat_add_commutes.flow

import verify.nat { nat_zero_add, nat_add_succ }
import .nat_add_zero { nat_add_zero }    # sibling — no path arithmetic

theorem nat_add_commutes(a: Nat, b: Nat) { ... }

export nat_add_commutes
```

---

## Migration from String Imports

| Old (jank) | New |
|------------|-----|
| `import "stdlib/math.flow"` | `import std.math { ... }` |
| `import "stdlib/audio/filters.flow"` | `import std.audio.filters { ... }` |
| `import "../../../../lib/verify/nat.flow"` | `import verify.nat { ... }` |
| `import "../../vulkan_abi/renderer.flow"` | Add to `flow.toml [dependencies]`, then `import vulkan_abi.renderer` |
| `import "memory_working.flow"` | `import .memory_working` (sibling) or proper package root |

Compiler accepts old syntax with deprecation warning during transition. CI fails on string imports in `lib/` and `examples/verify/`.

---

## What Makes This Future-Proof

| Concern | How it's handled |
|---------|------------------|
| Move files around | Imports unchanged, logical names, not paths |
| Remote packages | `[dependencies]` in `flow.toml`, same `import foo.bar` syntax |
| Version pinning | Lock file next to `flow.toml` (like Cargo/npm) |
| Symbol collisions | Package name is first segment: `my_pkg.foo` vs `their_pkg.foo` |
| Function creep | Unexported = invisible; `export` line is the API review point |
| LLM codegen | Dots are regular; no string path guessing |
| IDE / LSP | `import verify.nat` → jump to definition, autocomplete exported symbols only |
| Proof libraries | `verify.*` packages publish exactly like any other package |

---

## Built on What Flow Already Has

| Existing innovation | Module system extends it |
|--------------------|--------------------------|
| `flow.toml` packages | Becomes the resolution root, already there, just wired up |
| Effect / capability system | Imports deliver capabilities from named modules |
| Domain-prefixed theorems (`nat_add_zero`) | Module path + symbol name = unique global identity |
| Theorem headers (`means`, `from`, `tier`) | Module headers at file level |
| Explicit keywords (`let`, `theorem`, `has property`) | `import`, `export`, same style, no sigils |

---

## Implementation Phases

| Phase | Ships |
|-------|-------|
| **1** | `[paths]` in `flow.toml`, dot-path resolver, `export` line |
| **2** | New import syntax in parser; deprecation warning on strings |
| **3** | `import .sibling`, `export import` re-export, LSP autocomplete on exports |
| **4** | `[dependencies]` remote resolution + lock file |
| **5** | `flow doc <module>`, orphan-export CI lint |

---

## One Sentence

**Name modules with dots, declare roots in `flow.toml`, export only what you mean, file paths never appear in source again.**