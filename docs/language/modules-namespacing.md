# `module` blocks and namespacing

> **Status:** `module X { ... }` is parsed and flattened. It is not a namespace.
> This note records exactly what happens today, what breaks, and what a real
> implementation would cost. Nothing here is implemented yet.

Related: [modules.md](modules.md) for the file-level module system, which does
work and is where the `import` / `export` / `export import` story lives.

---

## What happens today

`parse_module` in `src/flow/parser.py` reads `module NAME { ... }` into a
`ModuleDecl` carrying a name and a list of inner declarations. That name is
then thrown away:

```python
def flatten_module_declarations(declarations):
    """Expand module { ... } blocks into top-level declarations."""
    flat = []
    for decl in declarations:
        if isinstance(decl, ModuleDecl):
            flat.extend(flatten_module_declarations(decl.declarations))
        else:
            flat.append(decl)
    return flat
```

`resolve_modules` calls it on every resolution, so no backend ever sees a
`ModuleDecl`. The inner declarations arrive at the C generator as ordinary
top-level declarations with their original, unqualified names.

`ModuleDecl` appears in exactly two files outside the parser:
`src/flow/module_resolver.py` (the flatten above, plus the `ModuleDecl`
import) and nowhere in any backend. One file in the repository uses the
keyword: `tests/core/test_production_features.flow`, which declares
`module inner { function helper() -> i32 { return 42 } }` and never calls
`helper`.

---

## What breaks

### 1. Two modules cannot declare the same name

```flow expect-error
# collide.flow
module audio {
    function gain() -> i32 { return 1 }
}

module video {
    function gain() -> i32 { return 2 }
}

function main() -> i32 {
    return gain()
}
```

```
$ python3 -m flow.transpiler collide.flow --c --strict -o collide.c
Resolving modules...
Parsed 3 functions, 0 structs, 0 effects, 0 capabilities
Generated C written to collide.c
```

The compiler accepts it in strict mode. The generated C contains two
prototypes and two definitions of `gain`, and the error only surfaces at
`clang`:

```
collide.c:35:9: error: redefinition of 'gain'
   35 | int32_t gain(void) {
      |         ^
collide.c:31:9: note: previous definition is here
```

The overload resolver in `src/flow/overload.py` cannot rescue this. It mangles
on parameter types (`_mangle_name` returns `name` unchanged when the parameter
list is empty), so two zero-argument functions with the same name are
indistinguishable to it whatever module they came from.

### 2. A symbol inside a `module` block is not importable, but is still emitted

```flow
# nsmod.flow
module inner {
    function helper() -> i32 { return 42 }
}

export inner
```

```
$ python3 -m flow.transpiler use.flow --c --strict -o use.c   # import .nsmod { helper }
Error resolving modules: Module .nsmod (nsmod.flow) has no symbol 'helper'
```

`_resolve_recursive` binds `getattr(decl, "name", None)`, and for a
`ModuleDecl` that is the module's own name. So `nsmod.flow` exports a symbol
called `inner` that refers to nothing callable, while `helper` is invisible to
the brace list. Import `inner` instead and it type-checks, and `helper` still
lands in the generated C as a global definition:

```
$ grep helper use.c
int32_t helper(void);
int32_t helper(void) {
```

A name that cannot be imported yet always occupies the global C namespace is
the worst of both arrangements.

### 3. `import` inside a `module` block is dead code

`parse_module` accepts `import`, so this parses:

```flow
module m {
    import .alpha

    function use_it() -> i32 {
        return alpha_one()
    }
}
```

`_resolve_recursive` collects imports from the top level of the parsed
declaration list only, and flattening happens afterwards in `resolve_modules`.
The nested `ImportDecl` is never resolved:

```
Type errors:
  ✗ Undefined function 'alpha_one'
  ✗ Function 'use_it' returns void but should return i32
```

### 4. Most declaration kinds are rejected inside a block

`parse_module` handles seven forms: `function`, `struct`, `const`, `enum`,
`import`, `trait`, `impl`. Everything else raises:

```
export inside module -> Unexpected declaration inside module 'm': TokenType.EXPORT
static inside module -> Unexpected declaration inside module 'm': TokenType.LET
nested module        -> Unexpected declaration inside module 'a': TokenType.MODULE
```

No `export`, no module statics, no `extern`, no `type` alias, no `distinct`,
no `effect`, no `capability`, no `theorem`, no `unit`, no nesting.

---

## Why qualified access has no free syntax

A namespace needs a way to say "the `gain` in `audio`". Both candidate
spellings are already taken.

**`X::name` is the effect-call operator.** `src/flow/parser.py` in
`parse_primary`:

```python
elif self.current_token.type == TokenType.DOUBLE_COLON:
    # Effect call: EffectName::operation(args)
    self.advance()
    operation = self.expect(TokenType.IDENTIFIER).value
    self.expect(TokenType.LPAREN)
    ...
    return EffectCall(name, operation, arguments)
```

`Audio::gain()` and `Log::emit("x")` are the same token sequence. Telling them
apart requires knowing whether `Audio` is a module or an effect, which is a
name-resolution question the parser answers long before it has a symbol table.

**`X.name` is field access.** The same branch routes `DOT` to
`parse_field_access(name)`, and `audio.gain()` is a method call on a variable
named `audio`. Field access on a struct value and namespace access on a module
are again distinguishable only with a symbol table.

So qualified access needs one of:

- a third sigil, which contradicts the "explicit keywords, no sigils" line in
  [modules.md](modules.md);
- a pre-pass that collects module names before expression parsing, turning the
  single-pass parser into two passes over every file;
- resolution deferred to the type checker, with `FieldAccess` and `EffectCall`
  nodes rewritten into namespace access after the fact.

The third is the only one that keeps the surface syntax clean, and it is the
one that spreads across the most code.

---

## Implementation plan

Five steps, in dependency order.

**1. Parser completeness.** Rewrite `parse_module` to accept every top-level
declaration form, including `export`, module statics, `extern`, type aliases
and nested `module`. The cleanest version factors the top-level declaration
loop in `Parser.parse()` into a reusable `parse_declaration()` and calls it
from both places. That factoring is worth doing on its own.

**2. Keep the module name on the AST.** Stop flattening in
`resolve_modules`. Instead, walk `ModuleDecl` trees and stamp each inner
declaration with a `namespace` field holding the dotted module path
(`audio`, `audio.filters`). Declarations stay in one flat list, so no backend
needs to learn about tree structure.

**3. Mangle at emit, resolve on the unmangled name.** Give every namespaced
declaration a mangled C identifier, `audio__gain`, composed before overload
mangling so an overloaded namespaced function becomes `audio__gain_i32`. The
mangling has to be applied in every emitter that writes a function or type
name: `src/flow/c_generator.py` (3657 lines), `src/flow/mlir_generator.py`
(4325), `src/flow/js_generator.py`, `src/flow/python_generator.py`,
`src/flow/shader_codegen.py`, `src/flow/metal_codegen.py`, plus
`src/flow/monomorphize.py` (991) which synthesises new names for generic
instantiations, and `src/flow/overload.py` whose `_mangle_name` must compose
rather than compete with it. `src/flow/type_checker.py` (2763) keys its
function table on the plain name and needs the namespace as part of the key.

**4. Qualified access.** Parse `X.name` and `X::name` into a new
`QualifiedName` node when the head identifier is not a known local binding,
and resolve it in the type checker against the namespace table built in step
2. `EffectCall` construction moves behind the same resolution point, so
`Log::emit(...)` is decided by looking `Log` up rather than by its position in
`parse_primary`.

**5. Imports and exports.** Resolve `ImportDecl`s found inside `ModuleDecl`
bodies (currently dropped, see breakage 3) by collecting them during the same
walk as step 2. Decide and then implement one rule for the file/block
interaction: whether `export` inside a block exports through the file, and
whether `import pkg.mod { audio.gain }` is legal or whether the brace list
stays flat and namespaced symbols are reachable only as `mod.audio.gain`.
`export import` (see [modules.md](modules.md)) forwards file-level exports
today and would need to say what it does with namespaced ones.

The self-hosted compiler is a sixth step. `compiler/src/parser.flow` has no
`module` keyword at all, and `flowc_parse_program` handles `import`, `export`,
`function`, `struct`, `extern` and `const` and errors on everything else. Any
namespace design has to be implemented there too before the flowc path can
compile namespaced code.

---

## Migration risk

**Inside this repository: low.** One file uses the keyword and never calls
across the block boundary. Removing `module` entirely would cost one edit.

**Outside it: unbounded and silent.** Today `module audio { ... }` declares
global names. After namespacing, every call site outside the block breaks, and
the failure mode is a resolution error at the call rather than anything that
points at the block. Any program that relies on flattening, deliberately or
because it wrote `module` as a comment-with-braces, stops compiling.

**The mangling change is not source-compatible with linked C.** Flow functions
declared inside a `module` block currently have plain C names and can be called
from hand-written C, from `extern` declarations in other Flow files, and from
the FFI. `audio__gain` changes the ABI of every such symbol.

**Mitigation.** Introduce namespacing behind a per-file opt-in and leave the
existing behavior as the default. A file-level pragma or a distinct keyword
(`namespace X { ... }`, leaving `module` as the flattening form) both let new
code get namespaces without a flag day. Deprecate `module` once the corpus has
moved.

---

## Recommendation

Do not implement this piecemeal. The parser factoring in step 1 and the
resolution of nested imports in step 5 are both worth doing on their own and
neither requires the mangling work. The mangling in step 3 touches every
backend and the type checker, and the syntax question in step 4 has no answer
that is both clean and cheap. Land those together, behind an opt-in, or leave
`module` flattening as documented behavior.
