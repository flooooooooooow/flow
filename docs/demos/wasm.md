# WebAssembly gallery

118 Flow examples compiled to WebAssembly and playable in a browser. Every one
is the unedited source from this repository, put through Flow → C → `emcc`.

**[Open the live gallery](../wasm/index.html)**. The pages below only run
there. This markdown page cannot host WebAssembly; the wiki renders it as
text, so the gallery is a separate static site under `/wasm/`.

The games and the field simulations link `runtime/gfx_wasm.c`, a canvas
backend for the same gfx API that drives the native window and the headless
GIF recorder. Nothing in any example was changed to make it run in a browser.

Build the whole thing:

```bash
python3 scripts/build_wasm_gallery.py
python3 -m http.server 8000 --directory site
# open http://localhost:8000/wasm/
```

Build one program:

```bash
./flow wasm examples/games/snake_gfx.flow --out build/wasm/snake
```

## What is in it

| Category | Running | Payload | What it is |
|---|---:|---:|---|
| [Games](../wasm/index.html) | 23 of 23 | 859 KB | Every `*_gfx.flow` in `examples/games/`, the same sources [the GIF gallery](games.md) records |
| [Morphogenesis](../wasm/index.html) | 20 of 20 | 763 KB | Every field simulation in `examples/morphogenesis/`, see [the gallery](morphogenesis.md) |
| [Basics](../wasm/index.html) | 22 of 22 | 443 KB | `examples/basics/`, pure computation printing into the page |
| [Language and compilers](../wasm/index.html) | 22 of 23 | 570 KB | Generics, traits, enums, effect rows, and Flow tools written in Flow |
| [Numerics and dynamics](../wasm/index.html) | 16 of 18 | 491 KB | Solvers, optimisers, linear algebra, control theory |
| [Learning](../wasm/index.html) | 7 of 12 | 259 KB | Small models and agents |
| [Systems and data](../wasm/index.html) | 8 of 13 | 268 KB | Allocators, hash tables, hashing, parsers, file formats |

Machine-readable index, including every failure and its reason:
[`manifest.json`](../wasm/manifest.json).

## Verified in a browser

These were loaded from a local server in Chrome and driven by hand. Everything
else in the gallery built and is listed as such, which is a weaker claim.

| Example | What happened |
|---|---|
| `snake_gfx` | Title screen drew, Space started the run, Up steered the snake into the top wall, game-over panel appeared |
| `2048_gfx` | Down merged two 2s into a 4, Right and Left slid the board, new tiles spawned |
| `tetris_gfx` | Board, ghost piece, next-piece preview and the SCORE / LEVEL / LINES readout all drew; Left moved the falling piece |
| `gray_scott` | Solitons formed from the seed; pressing `4` switched to the MAZE preset and the field reorganised into labyrinth stripes |
| `turing_spots` | Run from a gallery card into its iframe; pressing `1` switched the regime to SPARSE |
| `slime_mold` | 2200 Physarum agents depositing and following a trail map, step counter climbing |
| `calculator` | Printed the full expression-calculator transcript, operator precedence and all, exit 0 |
| `fibonacci` | Returned 55 |
| `prime_numbers` | Returned 10 |
| `lorenz_attractor` | Ran to completion, `main returned 0` |

No console errors on any of them.

## How the browser backend works

`runtime/gfx_wasm.c` is the fourth backend behind `lib/stdlib/gfx.flow`, after
the Cocoa window, the SDL one and the headless PPM recorder. It exports the
same eight `flow_gfx_*` symbols, keeps an RGBA framebuffer like the recorder
does, and on `flow_gfx_present` copies that buffer into a canvas with one
`putImageData` call.

The frame loop is the interesting part. Flow games are written as
`while gfx_frame_pump(g) { ... }` with the loop inside `main`, and a plain
while-loop in WebAssembly would freeze the tab. The pages are built with
`-sASYNCIFY`, so `flow_gfx_present` can await one `requestAnimationFrame`
before returning. The Flow program still reads as a straight loop; the browser
gets its event loop back once per presented frame, paced to 60 Hz.

Keyboard events are mapped to the same macOS `NSEvent` keycodes the games
already hardcode (`KEY_LEFT` 123, `KEY_SPACE` 49, and so on), so no game needed
a browser-specific input path. A key tapped between two polls is held until the
program has actually read it, which is what makes single keystrokes land at
60 fps.

## What runs, and what is still being crossed

Only the first two rows are verified in a browser. The rest name the mechanism
and say plainly that it is not built here.

| Capability | State | Route |
|---|---|---|
| Pure computation | **Runs today** | Arithmetic, arrays, structs, strings, printf. Flow → C → wasm32 with nothing else linked in. |
| gfx graphics and keyboard | **Runs today** | `runtime/gfx_wasm.c` paints the framebuffer onto a canvas and maps DOM key events to macOS keycodes. |
| Threads and channels | In progress | Emscripten `-pthread` over SharedArrayBuffer and Web Workers, which needs the page to be cross-origin isolated. |
| Sockets and HTTP | In progress | Emscripten's WebSocket-backed POSIX socket bridge (`-lwebsocket.js` / `PROXY_POSIX_SOCKETS`). |
| GPU kernels | In progress | WebGPU, with WGSL generated from the same `@gpu` AST that already emits Metal. |
| Embedded CPython | In progress | Pyodide, which is CPython itself compiled to WebAssembly. |
| File I/O | In progress | Emscripten's MEMFS and IDBFS filesystems. |
| Audio | Not attempted | The miniaudio and Metal audio backends have no browser counterpart yet; WebAudio is the route. |

## The thirteen that do not build

Each one stops at a named symbol. The gallery keeps their cards and prints the
reason on them.

| Example | Stops at | Why |
|---|---|---|
| `examples/effects/async_primitives.flow` | `flow_fiber_run_main` | Fiber runtime is a native C/assembly context switch |
| `examples/linalg/blas_demo.flow` | `cblas_dgemm` | Links a system BLAS |
| `examples/linalg/lu_decomposition.flow` | `cblas_dcopy` | Links a system BLAS |
| `examples/ml/digits_mlp.flow` | `flow_rt_monotonic_ns` | Runtime clock helper lives in the native runtime pack |
| `examples/ml/digits_mlp_parallel.flow` | `flow_rt_monotonic_ns` | Same, plus the thread pool |
| `examples/ml/digits_mlp_metal.flow` | `flow_gpu_alloc` | Metal GPU backend |
| `examples/ml/tape_mul.flow` | `flow_tape_reset` | Autodiff tape is a native runtime module |
| `examples/ai/ga_flappy.flow` | `fly` | Program references a symbol the transpiler does not emit |
| `examples/crypto/runtime_sha256.flow` | `flow_sha256` | Hashing helper lives in the native runtime pack |
| `examples/systems/system_info.flow` | `os_is_linux` | Asks the host which OS it is |
| `examples/graphics/graphics.flow` | `main` | Program has no `main`; it is a library-shaped example |
| `examples/systems/arena_frame.flow` | `redefinition of sizeof_i32` | Transpiler emits the helper twice; a C backend bug, not a wasm one |
| `examples/systems/manual_memory.flow` | `redefinition of sizeof_i32` | Same transpiler bug |

The last two are worth noting: they fail the same way under native `clang`,
so they are a Flow C-backend bug that the wasm build simply surfaced.

## Related

[Game Gallery](games.md) · [Morphogenesis Gallery](morphogenesis.md) ·
[WASM target notes](../language/wasm.md) ·
[recording demos](README.md) ·
[examples index](../../examples/README.md)
