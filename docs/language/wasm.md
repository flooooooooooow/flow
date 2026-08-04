# WebAssembly (WASM) target

Honest status of shipping Flow programs to the browser. This is **not** a
self-hosted Flow-in-WASM compiler.

## Near-term path (supported story)

```text
Flow source  →  Flow C backend  →  emcc (Emscripten)  →  .wasm + JS glue
```

| Stage | Tool | Notes |
|-------|------|-------|
| Flow → C | `./flow compile <file.flow>` | Portable C backend (same as native) |
| C → WASM | `emcc` from [Emscripten](https://emscripten.org/) | Optional local install; **not** required for CI |
| Browser | `.wasm` + generated JS | Serve over HTTP (module loading needs a server) |

Smoke test (skips cleanly if `emcc` is missing — CI-safe, exit 0):

```bash
./scripts/build_wasm_hello.sh
```

With a working Emscripten on `PATH` (prefer official emsdk; needs Python ≥ 3.10):

```bash
source ~/emsdk/emsdk_env.sh   # or your emsdk path
./scripts/build_wasm_hello.sh
python3 -m http.server 8765 --directory build/wasm_hello
# open http://localhost:8765/hello.html
```

Optional: compile Flow-transpiled C instead of the harness:

```bash
FLOW_WASM_FROM_FLOW=1 ./scripts/build_wasm_hello.sh
```

Manual end-to-end without the script:

```bash
./flow compile examples/basics/hello_world.flow
emcc build/hello_world.c -o build/wasm_hello/hello.js \
  -s WASM=1 -s EXPORTED_FUNCTIONS="['_main']" \
  -s EXPORTED_RUNTIME_METHODS="['ccall','cwrap']"
```

See also older helpers under `scripts/build_wasm.sh`, `wasm/flow_to_wasm.py`, and
`demos/wasm/` — those are experiments; `build_wasm_hello.sh` is the documented
minimal path for issue #121.

## What works today

- ✅ C backend output is valid input for `emcc` for small programs (`main` returning `i32`, stdio)
- ✅ Checked-in harness + optional script for a hello artifact (`wasm/hello_harness.c`)
- ✅ Playground **Run (native local)** — loopback API that runs real Flow→C on the machine ([#132](https://github.com/flooooooooooow/flow/issues/132))
- ⚠️ Larger programs (effects handlers, graphics, heavy libc) may need extra `emcc` flags / stubs
- ❌ No first-class `flow wasm` product target with stable flags in CI
- ❌ No Flow compiler binary compiled to WASM (self-host / in-browser toolchain)

## Deferred (not this slice)

| Goal | Why deferred |
|------|----------------|
| Native Flow-in-WASM compiler | Heavy: Python toolchain + deps → WASM, or a rewritten subset |
| Playground “compile in browser” via emscripten artifact of the full compiler | Same; next incremental step is serving a **hello** WASM artifact, not the compiler |
| Direct WASM emission (skip C) | No IR→WASM backend planned near-term |

Roadmap row: [ROADMAP.md](../../ROADMAP.md) — **WASM target** is partial ✅ via C→Emscripten.

Playground / wiki: native-local compile API exists (#132). Next playground step is an
emscripten hello artifact; full in-browser Flow compile remains under #121.

## Related docs

- Language Spec §9.3 WebAssembly — [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md)
- Wiki Phase 3 playground row — [wiki-roadmap.md](../wiki-roadmap.md)
- Playground UI — [playground/index.html](../playground/index.html)
