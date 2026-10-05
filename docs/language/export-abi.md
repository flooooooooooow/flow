# C/WASM export ABI (#396)

Flow provides a stable export path so WASM and FFI consumers do not need to
know the compiler's overload-mangling scheme.

flowc emits the aliases (#1030). The retired Python C backend emitted the
same shape.

## Flags

```
./flow tool compiler/scripts/flowc_emit.flow --export foo --export bar prog.flow prog.c
FLOWC_EXPORT="foo,bar" FLOWC_IN=prog.flow FLOWC_OUT=prog.c flowc
```

- `--export NAME` (repeatable, or a comma list; `FLOWC_EXPORT`): emit a
  visible alias `flow_export_<name>` for each named function. The alias
  forwards to the C symbol. A name no module defines gets a
  `/* --export NAME: not found in this TU */` comment.
- `--library` (`FLOWC_LIBRARY=1`): emit a unit to link next to a program.
  It has no runtime checks and no fault handler, keeps plain C names with
  external linkage, needs no `main`, and never moves `main` onto a fiber.
- `--module-name NAME`: accepted for older command lines. It does not change
  the C.

## Generated aliases

flowc keeps the plain name of a function that is not overloaded and mangles
overloads by parameter type (`pick(a: i32)` becomes `pick_i32`). With
`--export add --export pick`, the generated C ends with:

```c
/* Flow export aliases (#396) */
__attribute__((visibility("default"))) int32_t flow_export_add(int32_t a, int32_t b) { return add(a, b); }
__attribute__((visibility("default"))) int32_t flow_export_pick(int32_t a) { return pick_i32(a); }
```

An overloaded name aliases its first definition. A `void` function's alias
calls it without `return`. In a bundle, each module aliases the names it
defines.

The consumer links against `flow_export_add`, which is stable across
overload-resolution changes.

## Emscripten usage

```
./flow tool compiler/scripts/flowc_emit.flow --library --export add prog.flow build/prog.c
emcc build/prog.c -o build/prog.js \
  -sEXPORTED_FUNCTIONS=_flow_export_add \
  -sEXPORTED_RUNTIME_METHODS=ccall,cwrap
```

In JavaScript:

```js
const Module = await Module();
const add = Module.cwrap("flow_export_add", "number", ["number", "number"]);
console.log(add(1, 2));  // 3
```

## ABI versioning

The export prefix `flow_export_` is version 1 of the ABI. Future breaking
changes will use a new prefix (e.g. `flow_export2_`). The `--module-name`
flag does not affect the prefix; it is reserved for Emscripten MODULARIZE
and Python package naming.

Buffer arguments that are already contiguous should use the
[zero-copy FFI buffer ABI](ffi-buffer.md) rather than copying into a packed
scratch buffer.
