# 11. Modules, projects, packages, and interoperation

File modules define public interfaces. Projects add build metadata and dependencies. Interoperation connects Flow declarations to C, Python, and stable exported symbols. Every `flow` block in this chapter is compiler-checked in CI.

## 11.1 Imports

Flow supports logical dot paths, selected names, aliases, and package-local siblings. Because an import only compiles when its target module exists in the same project/search path, the book points to complete repository examples instead of presenting orphan import statements as runnable programs.

See [Modules](../language/modules.md) and the module tests under `tests/lang/` for checked import/re-export examples. Older string-path imports remain supported in existing code but logical module paths are the preferred direction.

## 11.2 Exports

Declarations are private unless exported:

```flow
export function gain(x: f32, amount: f32) -> f32 {
    return x * amount
}

export struct FilterState {
    z1: f32
}
```

Re-export syntax is documented on [Modules](../language/modules.md), where its multi-file context can be shown correctly.

## 11.3 `module` blocks

```flow
module helpers {
    function twice(x: i32) -> i32 {
        return x * 2
    }
}
```

A `module` block currently groups declarations but does not create a namespace; file modules are the namespace boundary.

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
```

Typical project operations are:

```bash
./flow init meter
cd meter
../flow pkg install
../flow build
```

Resolved dependencies are recorded in `flow.lock`.

## 11.5 Extern functions

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
    function printf(format: string, ...) -> i32
}
```

An extern declaration gives Flow a signature for a symbol supplied by C or the platform. It does not automatically establish ownership, thread-safety, lifetime, or RT-safety properties.

## 11.6 C headers and embedded C

The Python compiler host supports `@cImport(...)`, `@cInclude(...)`, `extern type`, and `@cEmbed(...)`. These features require real header/native context, so their authoritative executable examples are the tests rather than isolated fragments:

```bash
FLOW_HOST=python ./flow run tests/lang/test_c_import_auto.flow
FLOW_HOST=python ./flow run tests/lang/test_extern_type.flow
FLOW_HOST=python ./flow run tests/lang/test_c_embed.flow
```

`@cEmbed` is an explicit unsafe escape hatch and should remain small and separately reviewed.

## 11.7 C function pointers

Flow closures use ordinary function types such as `(i32) -> i32`. Raw C callbacks use `cfn(...) -> ...`. The dynamic-loading and `qsort` examples exercise the complete ABI context:

```bash
FLOW_HOST=python ./flow run tests/lang/test_dlopen.flow
FLOW_HOST=python ./flow run tests/lang/test_qsort.flow
```

## 11.8 Stable exports

`@flow_api` preserves a stable plain C-facing name:

```flow
@flow_api
function add_api(a: i32, b: i32) -> i32 {
    return a + b
}
```

The CLI can also emit ABI aliases when transpiling a library:

```bash
./flow transpile library.flow --c --export add scale --module-name signal -o build/library.c
```

## 11.9 Native project sources

A project manifest may name C, C++, Objective-C, libraries, include paths, and frameworks. Use `./flow build-native` and `./flow run-native` when a package wraps a native system library.

## 11.10 Python wheel target

```bash
./flow python mathlib.flow --name mathlib --version 0.1.0
```

The target compiles Flow through C into a CPython extension and wheel. Supported boundary types are intentionally narrower than the full language surface.

## Exercises

Split a program into library and consumer modules; build a re-exporting aggregator; declare one libc function; and create a path dependency whose resolution appears in `flow.lock`.

Next: [Effects and concurrency](12-effects-and-concurrency.md).
