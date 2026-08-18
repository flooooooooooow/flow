# WebAssembly (WASM) target

Honest status of shipping Flow programs to the browser. This is **not** a
self-hosted Flow-in-WASM compiler.

There are two routes to a `.wasm`, and they are for different jobs. `./flow
wasm` goes through Emscripten and gives you a whole page: libc, a filesystem, a
canvas, JS glue. `python -m flow.wasm_compiler` goes through MLIR and LLVM
straight to a freestanding module with no libc and no glue, for embedding in a
host that already has its own runtime. The Emscripten route is the rest of this
page; the direct one is [its own section](#direct-wasm32-no-emscripten).

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
| Freestanding wasm32 modules | **Runs today** | Flow → MLIR → LLVM IR → `clang --target=wasm32-unknown-unknown`. No Emscripten, no libc. See below. |
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
Flow source  →  Flow C backend  →  emcc (Emscripten)  →  .wasm + JS glue
```

| Stage | Tool | Notes |
|-------|------|-------|
| Flow → C | `./flow compile <file.flow>` | Portable C backend (same as native) |
| C → WASM | `emcc` from [Emscripten](https://emscripten.org/) | Optional local install; **not** required for CI |
| Browser | `.wasm` + generated JS | Serve over HTTP (module loading needs a server) |

Playground (local compile API):

```bash
./flow playground
# UI buttons: Run (WASM local) → POST /compile {"target":"wasm"}
#             Browser transpile → http://127.0.0.1:8765/pyodide  (Pyodide Flow→C)
```

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
`wasm/flow_wasm.py` / `wasm/wasm_examples/` — those are the browser gallery;
`build_wasm_hello.sh` is the documented minimal path for issue #121.

## Direct wasm32 (no Emscripten)

`src/flow/wasm_compiler.py` compiles a Flow file to a freestanding wasm32
module without going near the C backend or Emscripten:

```text
Flow source  →  MLIR  →  LLVM IR (wasm32)  →  clang --target=wasm32-unknown-unknown  →  .wasm
```

```bash
PYTHONPATH=src python3 -m flow.wasm_compiler tests/fixtures/wasm/main_42.flow \
  -o build/main_42.wasm --export answer -O O2
```

| Flag | Meaning |
|------|---------|
| `-o`, `--output` | Output `.wasm` path. Required. |
| `--export NAME` | Export one LLVM symbol. Repeat for several. Omit and the module is built with `--export-all`. |
| `-O`, `--opt-level` | `O0`, `O1`, `O2`, `O3`, `Os`, `Oz`. Defaults to `O2`. |

Names passed to `--export` are checked against the symbols actually defined in
the generated LLVM IR before clang runs, so a typo fails with the list of
symbols that do exist rather than with a linker error.

The module is linked `-nostdlib --no-entry --allow-undefined --export-memory`.
Linear memory is exported, so a host reads and writes arguments through it:

```js
const {memory, sum_pair} = instance.exports;
const values = new Float32Array(memory.buffer, 4096, 2);
values[0] = 1.5;
values[1] = 2.25;
sum_pair(4096);   // 3.75
```

### The host supplies the allocator

`--allow-undefined` means anything Flow needs but the module does not define
becomes an import the host must provide. Today that is `env.malloc`, pulled in
by any Flow code that allocates:

```flow
export function alloc_sum() -> f32 {
    let mut values: array<f32> = array<f32>(2)
    values[0] = 1.5
    values[1] = 2.25
    return values[0] + values[1]
}
```

`runtime/wasm/flow_runtime.mjs` is a bump allocator that grows linear memory on
demand and is enough to run modules like that one:

```js
import {createFlowWasmRuntime} from './runtime/wasm/flow_runtime.mjs';

const runtime = createFlowWasmRuntime();
const instance = await WebAssembly.instantiate(module, runtime.imports);
runtime.attach(instance);        // must come before the first allocating call
instance.exports.alloc_sum();    // 3.75
```

It never frees. It is a test runtime, not a general-purpose heap, and a real
host should import its own `malloc`.

### Toolchain

The clang on `PATH` must have the WebAssembly target compiled in. Apple's
system clang does not, and fails with `No available targets are compatible with
triple "wasm32-unknown-unknown"`. Point `FLOW_WASM_CLANG` or `LLVM_PATH` at an
LLVM build that does, or install one (`brew install llvm`).

The MLIR step emits the triple `wasm32-unknown-emscripten` with an ILP32
datalayout; the linker step overrides it to `wasm32-unknown-unknown`, which is
where the `-Woverride-module` warning in the output comes from.

### What CI verifies

`.github/workflows/wasm32.yml` runs on every change to the compiler, the
runtime shim, or the fixtures, and each step executes the module rather than
just building it:

| Fixture | Checked |
|---|---|
| `main_42.flow` | Node instantiates the module and `answer()` returns 42 |
| `sum_pair.flow` | Two `f32` values written into exported linear memory sum to 3.75 |
| `alloc_sum.flow` | Imports exactly `env.malloc`; 32 calls each return 3.75 and linear memory grows |
| `alloc_sum.flow` | `tests/wasm/compare_native_wasm.py` compares the wasm result against the same function compiled natively through MLIR |

Unit coverage for the export validation and the clang command lives in
`tests/unit/test_wasm_compiler.py`.

## What works today

- ✅ Direct wasm32 modules with no Emscripten and no libc, executed under Node in CI (`python -m flow.wasm_compiler`)
- ✅ C backend output is valid input for `emcc` for small programs (`main` returning `i32`, stdio)
- ✅ Checked-in harness + optional script for a hello artifact (`wasm/hello_harness.c`)
- ✅ Playground **Run (native local)** — loopback API that runs real Flow→C on the machine ([#132](https://github.com/flooooooooooow/flow/issues/132))
- ✅ Playground **Run (WASM local)** — same API with `target: "wasm"` (needs `emcc` + `node`)
- ✅ **Browser transpile** — Pyodide loads `flow.parser` / `flow.c_generator` from `/flow-src/` (`docs/playground/pyodide.html`)
- ⚠️ Larger programs (effects handlers, graphics, heavy libc) may need extra `emcc` flags / stubs
- ❌ No clang/emcc compiled into the browser tab (Pyodide is transpile-only)

## Deferred (not this slice)

| Goal | Why deferred |
|------|----------------|
| Full clang-in-browser execution | Needs WASI toolchain in-tab; Pyodide covers Flow→C only |
| libc under direct wasm32 | The freestanding target links nothing; `printf` and friends need a WASI shim or Emscripten |

Roadmap row: [ROADMAP.md](../../ROADMAP.md) — **WASM target** is partial ✅ via C→Emscripten, direct MLIR→LLVM→wasm32, and playground WASM/Pyodide.

## Related docs

- Direct wasm32 CI — [`.github/workflows/wasm32.yml`](https://github.com/flooooooooooow/flow/blob/main/.github/workflows/wasm32.yml)
- Threads, GPU, sockets, files, CPython in the browser — [wasm-crossings.md](wasm-crossings.md)
- Language Spec §9.3 WebAssembly — [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md)
- Wiki Phase 3 playground row — [wiki-roadmap.md](../wiki-roadmap.md)
- Playground UI — [playground/index.html](../playground/index.html)
