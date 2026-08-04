# WASM examples

Near-term path: **Flow → C → emcc (Emscripten) → .wasm + JS**.

`emcc` is optional. Flow→C always works; WASM linking needs Emscripten on `PATH`.

## hello_wasm.flow

```bash
# Native smoke (no emcc)
./flow run examples/wasm/hello_wasm.flow

# Flow→C (+ HTML; .wasm if emcc is available)
./flow wasm examples/wasm/hello_wasm.flow

# Documented CI-safe hello script (skips cleanly without emcc)
./scripts/build_wasm_hello.sh
# Optional: FLOW_WASM_FROM_FLOW=1 ./scripts/build_wasm_hello.sh
```

See [docs/language/wasm.md](../../docs/language/wasm.md) and `wasm/wasm_demo/`.
