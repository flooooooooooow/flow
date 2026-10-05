# C/WASM export ABI (#396)

Flow provides a stable export path so WASM and FFI consumers do not need to
know the compiler's overload-mangling scheme.

## CLI flags

```
flow transpile prog.flow --c --export foo bar --module-name mymod -o prog.c
```

- `--export NAME ...`: emit a visible alias `flow_export_<name>` for each
  named function. The alias forwards to the mangled C symbol.
- `--module-name NAME`: sets the module name (used by `flow wasm` for the
  Emscripten MODULARIZE name and as a prefix in future ABI versions).

## Generated aliases

For a Flow function `function add(a: i32, b: i32) -> i32`, the C backend
mangles the symbol to `add_i32_i32`. With `--export add`, the generated C
also contains:

```c
__attribute__((visibility("default")))
int32_t flow_export_add(int32_t a, int32_t b) { return add_i32_i32(a, b); }
```

The consumer links against `flow_export_add`, which is stable across
overload-resolution changes.

## Emscripten usage

```
flow transpile prog.flow --c --export add --module-name mymod -o build/prog.c
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
