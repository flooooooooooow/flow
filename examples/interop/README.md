# Interop Examples

## Python Embedding

Flow calls Python through `lib/stdlib/python_embed.flow`: libpython natively,
Pyodide in the browser. The Python modules those programs import live in
`examples/interop/python/`, the one directory of Python subject files:

- `simple_interop.py`, imported by `python_embed.flow` here and by
  `tests/runtime/interop/python_embed.flow`
- `flow_demo.py`, imported by `examples/wasm/python_embed.flow`: natively
  from `examples/wasm` (sys.path entry `../interop/python`) and, copied by
  `./flow tool wasm_crossings python`, in the browser

```bash
./flow run examples/interop/python_embed.flow
```

## Runtime Tests

```bash
./flow test-interop
```
