# WebAssembly (WASM) target

Honest status of shipping Flow programs to the browser. This is **not** a
self-hosted Flow-in-WASM compiler.

## The gallery

118 examples are compiled and playable at
[the WebAssembly gallery](../demos/wasm.md), including every game and every
morphogenesis field simulation. That page is the fastest way to see what the
target can do today.

```bash
./flow wasm examples/games/snake_gfx.flow --out build/wasm/snake
python3 scripts/build_wasm_gallery.py        # all of them, into site/wasm/
```

`./flow wasm` writes a `.wasm`, its `.js` loader and a runnable `index.html`.
Graphics programs get a canvas page with keyboard wiring and a click-to-start
button; everything else prints into a `<pre>`.

CPU backend defaults to C (`--backend=c`). MLIR is available for the same
page shape:

```bash
./flow wasm examples/games/snake_gfx.flow --backend=mlir --out build/wasm/snake-mlir
```

The MLIR wasm path always passes `--wasm32` to the transpiler so libc
`size_t` / `long` lower as `i32` (ILP32). Without that, emcc links but
`malloc`/`memcpy`/… get signature-mismatch warnings and real programs
(doom-flow) misbehave. Raw `python3 -m flow.transpiler … --mlir --llvm`
for wasm must include `--wasm32` yourself.

Pack a host file into the virtual FS and link extra runtime C (both backends):

```bash
./flow wasm examples/wasm/hello_wasm.flow --backend=mlir \
  --preload examples/wasm/data@/data \
  --link runtime/flow_rt_support.c \
  --out build/wasm/hello-preload
```

`--preload` maps to `emcc --preload-file` and turns on `FORCE_FILESYSTEM`
(emits a `.data` blob next to the `.js`). `--link` passes extra `.c` files to
emcc; Cocoa `.m` / `.mm` are skipped. Doom-scale knobs on the page builder:
`--initial-memory=64MB`, `--asyncify-stack-size=65536`, and `--emcc-flag`
(passthrough). `--fs` / `--threads` crossings remain C-only for now and error
clearly under `--backend=mlir`.

## Status matrix

Two rows are verified in a browser. The rest name the mechanism that would
cross them and state that it is not built yet. None of them is a permanent
limit.

| Capability | State | Route |
|---|---|---|
| Pure computation | **Runs today** | Arithmetic, arrays, structs, strings, printf. Flow → C → wasm32 with nothing else linked in. |
| gfx graphics and keyboard | **Runs today** | `runtime/gfx_wasm.c` blits the framebuffer to a canvas; DOM key events map to the macOS keycodes the programs already use. |
| Threads and channels | In progress | Emscripten `-pthread` over SharedArrayBuffer and Web Workers. Needs cross-origin isolation, obtainable on GitHub Pages with a service-worker shim. |
| Sockets and HTTP | In progress | Emscripten's WebSocket-backed POSIX socket bridge (`-lwebsocket.js`, `PROXY_POSIX_SOCKETS`). |
| GPU kernels | In progress | WebGPU, with WGSL generated from the same `@gpu` AST that already emits Metal. |
| Embedded CPython | In progress | Pyodide, CPython compiled to WebAssembly. |
| File I/O | In progress | Emscripten MEMFS and IDBFS. |
| Audio | Not attempted | miniaudio and the Metal audio path have no browser counterpart yet; WebAudio is the route. |

## The browser gfx backend

`runtime/gfx_wasm.c` is the fourth backend behind `lib/stdlib/gfx.flow`, after
`gfx_macos.m` (Cocoa), `gfx_linux.c` (SDL) and `gfx_record.c` (headless PPM).
It exports the same `flow_gfx_*` symbols, keeps an RGBA framebuffer, and on
`flow_gfx_present` copies it into a canvas with one `putImageData`.

Flow games put their loop inside `main`, which would freeze a tab. The pages
are built with `-sASYNCIFY` so `flow_gfx_present` can await one
`requestAnimationFrame` before returning: the Flow source keeps its plain
while-loop and the browser gets its event loop back once per frame, paced to
60 Hz with a MessageChannel fallback for hidden tabs.

Two flags matter beyond that. `-sSTACK_SIZE=16MB`, because Flow puts
fixed-size arrays on the stack and a 128×128 field simulation holds several
grids of doubles at once, well past the 64 KB wasm32 default.
`-sINVOKE_RUN=0`, so `main` starts on a user gesture rather than at load.

## Near-term path (supported story)

```text
Flow source  →  C or MLIR (--wasm32)  →  emcc (Emscripten)  →  .wasm + JS glue
```

| Stage | Tool | Notes |
|-------|------|-------|
| Flow → C | `./flow compile <file.flow>` | Portable C backend (default) |
| Flow → LLVM IR | `python3 -m flow.transpiler … --mlir --llvm --wasm32` | Same ABI as C→emcc; required for doom-scale MLIR |
| → WASM | `emcc` from [Emscripten](https://emscripten.org/) | Optional local install; **not** required for CI |
| Browser | `.wasm` + generated JS | Serve over HTTP (module loading needs a server) |

### doom-flow (MLIR)

[doom-flow](https://github.com/godofecht/doom-flow) builds with
`BACKEND=c` (default) or `BACKEND=mlir`. The MLIR path needs Flow tip with
`#247` (`--wasm32`), `#249` (null ptr statics), and `#250` (struct static
inits, unsigned ops, `u8` zero-extend, `&module_global` addressof) — epic
`#230`. With those, `FLOW_DIR=… BACKEND=mlir ./scripts/build_wasm.sh --doom-only`
produces a playable in-browser IWAD boot (title / menu).

Playground (local compile API):

```bash
./flow playground
# UI buttons: Run (WASM local) → POST /compile {"target":"wasm"}
#             Browser transpile → http://127.0.0.1:8765/pyodide  (Pyodide Flow→C)
```

Smoke test (skips cleanly if `emcc` is missing; CI-safe, exit 0):

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
`wasm/flow_wasm.py` / `wasm/wasm_examples/`: those are the browser gallery;
`build_wasm_hello.sh` is the documented minimal path for issue #121.

## What works today

- ✅ C backend output is valid input for `emcc` for small programs (`main` returning `i32`, stdio)
- ✅ Checked-in harness + optional script for a hello artifact (`wasm/hello_harness.c`)
- ✅ Playground **Run (native local)**: loopback API that runs real Flow→C on the machine ([#132](https://github.com/flooooooooooow/flow/issues/132))
- ✅ Playground **Run (WASM local)**: same API with `target: "wasm"` (needs `emcc` + `node`)
- ✅ **Browser transpile**: Pyodide loads `flow.parser` / `flow.c_generator` from `/flow-src/` (`docs/playground/pyodide.html`)
- ⚠️ Larger programs (effects handlers, graphics, heavy libc) may need extra `emcc` flags / stubs
- ❌ No clang/emcc compiled into the browser tab (Pyodide is transpile-only)

## Deferred (not this slice)

| Goal | Why deferred |
|------|----------------|
| Full clang-in-browser execution | Needs WASI toolchain in-tab; Pyodide covers Flow→C only |
| Direct WASM emission (skip C) | No IR→WASM backend planned near-term |

Roadmap row: [ROADMAP.md](../../ROADMAP.md). **WASM target** is partial ✅ via C→Emscripten + playground WASM/Pyodide.

## Related docs

- Language Spec §9.3 WebAssembly: [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md)
- Wiki Phase 3 playground row: [wiki-roadmap.md](../wiki-roadmap.md)
- Playground UI: [playground/index.html](../playground/index.html)
