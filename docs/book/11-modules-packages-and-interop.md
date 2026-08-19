# 11. Modules, projects, packages, and interoperation

File modules define public interfaces. Projects add build metadata and
dependencies. Interoperation connects Flow declarations to C, Python, and
stable exported symbols.

## 11.1 Imports

Flow supports logical dot paths, selected names, aliases, and package-local
siblings:

```text
import std.math { sin, cos }
import verify.nat.nat_zero_add
import verify.nat as nat
import .filters.lowpass
```

Resolution proceeds through the built-in standard library, project `[paths]`,
declared dependencies, and then a leading-dot sibling inside the same package.
Older string-path imports remain common in the repository but are deprecated.

## 11.2 Exports and re-exports

Declarations are private to their module unless exported:

```flow
export function gain(x: f32, amount: f32) -> f32 {
    return x * amount
}

export struct FilterState {
    z1: f32
}

export gain, FilterState
```

An aggregator can re-export names from another module:

```text
export import .filters
export import .meters { rms, peak }
```

Re-export collisions are errors. The self-hosted compiler does not yet accept
`export import`; use the Python host for that form.

## 11.3 `module` blocks

```flow
module helpers {
    function twice(x: i32) -> i32 { return x * 2 }
}
```

At present, a `module` block groups declarations but does not create a
namespace. The compiler discards the block name and treats its declarations as
globals. Imports and several declaration forms do not work inside the block.
Use file modules for namespaces.

## 11.4 Project manifest

```toml
[package]
name = "meter"
version = "0.1.0"
entry = "src/main.flow"

[paths]
signal = "src/signal"

[dependencies]
mathkit = "^0.1"
local_dsp = { path = "../local_dsp" }
remote = { git = "https://example.org/remote.git", tag = "v1.0" }
```

Create and build a project:

```bash
./flow init meter
cd meter
../flow add mathkit@^0.1
../flow pkg install
../flow build
```

Dependencies install into `flow_packages/` and resolved Git revisions are
recorded in `flow.lock`.

## 11.5 Registry operations

```bash
./flow search matrix
./flow info mathkit
./flow add --path ../mathkit --name mathkit
./flow add --git https://example.org/dsp.git --tag v0.3 --name dsp
./flow publish --dry-run
```

The shipped registry is a versioned local JSON index with optional remote JSON
override. Publishing updates that index; there is no hosted account or package
upload service. Supported requirements include exact versions, `*`, caret
ranges, and lower bounds. Locking currently pins direct dependencies rather
than solving a complete transitive semver graph.

## 11.6 Extern functions

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
    function printf(format: string, ...) -> i32
}
```

An extern declaration supplies a Flow signature for a symbol linked from C or
the platform. Variadic declarations use `...`. Flow does not automatically
establish ownership, thread safety, lifetime, or real-time properties for an
extern call.

## 11.7 Importing C headers

The Python host supports header import and prototype generation:

```text
@cImport("math.h")
@cImport("my_api.h") as api
```

Include directories can be supplied to the transpiler. Opaque C types map to
pointer types, and supported structs/functions become available to checking and
code generation.

```bash
FLOW_HOST=python ./flow run tests/lang/test_c_import_auto.flow
```

Three related directives serve different purposes:

```text
@cInclude("my_api.h")
extern type OpaqueHandle

@cEmbed("static inline int helper(int x) { return x + 1; }")
```

`@cInclude` emits an include without generating Flow declarations.
`extern type` introduces an opaque name used through pointers. `@cEmbed`
places literal C in the generated translation unit; it is an explicit unsafe
escape and should be kept small and separately reviewed.

```bash
FLOW_HOST=python ./flow run tests/lang/test_extern_type.flow
FLOW_HOST=python ./flow run tests/lang/test_c_embed.flow
```

## 11.8 C function pointers

Flow closure types such as `(i32) -> i32` can carry an environment. A raw C
function pointer has the separate `cfn` type:

```text
let symbol: ptr<void> = dlsym(handle, "sqrt")
let sqrt_fn: cfn(f64) -> f64 = symbol as cfn(f64) -> f64
let result: f64 = sqrt_fn(9.0)
```

Use `cfn` for callbacks obtained from C, `dlsym`, and APIs such as `qsort`.
Use the ordinary function type for Flow closures.

```bash
FLOW_HOST=python ./flow run tests/lang/test_dlopen.flow
FLOW_HOST=python ./flow run tests/lang/test_qsort.flow
```

## 11.9 Stable C and WebAssembly exports

Flow normally mangles overloaded symbols. An exported ABI alias avoids exposing
that scheme:

```bash
./flow transpile library.flow --c \
    --export add scale \
    --module-name signal \
    -o build/library.c
```

The public alias is named `flow_export_add`, forwarding to the mangled
implementation. The `flow_export_` prefix is ABI version 1. `@flow_api` is the
source-level alternative for a deliberately stable plain C name.

## 11.10 Native project sources

A project manifest can name C, C++, Objective-C, libraries, include paths, and
frameworks under its native configuration. Use:

```bash
./flow build-native
./flow run-native
```

Use native project sources when a package wraps HTTP, SQLite, compression,
DNS, images, or another system library.

## 11.11 Python wheel target

```bash
./flow python mathlib.flow --name mathlib --version 0.1.0
```

The target compiles Flow through C into a CPython extension and wheel. Numeric,
Boolean, string, void, selected pointer, and struct signatures can cross the
boundary. Function pointers, complex nested generics, Python async mapping,
struct methods, and NumPy integration remain unsupported.

## Exercises

1. Split a two-function program into a library module and consumer.
2. Construct an aggregator that re-exports two noncolliding modules.
3. Declare and call one libc function not already used in this book.
4. Create a path dependency and confirm that `flow.lock` records it.

Next: [Effects and concurrency](12-effects-and-concurrency.md).
