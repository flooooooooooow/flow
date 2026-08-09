# WebAssembly Gallery

158 Flow examples compiled to WebAssembly, 151 of them runnable in a browser.
Every one is the unedited source from this repository, put through Flow → C →
`emcc`.

**[Open the live gallery](../wasm/index.html)** — the pages below only run
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
| [Games](../wasm/index.html) | 25 of 25 | 930 KB | Every `*_gfx.flow` in `examples/games/`, the same sources [the GIF gallery](games.md) records |
| [Morphogenesis](../wasm/index.html) | 40 of 40 | 2045 KB | Every field simulation in `examples/morphogenesis/`, see [the gallery](morphogenesis.md) |
| [Basics](../wasm/index.html) | 24 of 24 | 558 KB | `examples/basics/`, pure computation printing into the page (including the threaded `parallel_sum` and `parallel_scaling`) |
| [Language and compilers](../wasm/index.html) | 22 of 23 | 571 KB | Generics, traits, enums, effect rows, and Flow tools written in Flow |
| [Numerics and dynamics](../wasm/index.html) | 18 of 20 | 595 KB | Solvers, optimisers, linear algebra, control theory |
| [Learning](../wasm/index.html) | 9 of 12 | 360 KB | Small models and agents |
| [Systems and data](../wasm/index.html) | 13 of 14 | 503 KB | Allocators, hash tables, hashing, parsers, file formats |

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
| `digits_mlp_parallel` | Served cross-origin-isolated and run on real pthreads: 8 runtime workers, measured speedup 1.9× over the serial pass, serial == parallel accuracy check green, `main returned 0` |
| `parallel_sum` | Served cross-origin-isolated and run on real pthreads: 8 runtime workers, measured speedup 6.1–6.5× on the disjoint-shard reduction, serial sum == threaded sum, `main returned 0` |
| `parallel_scaling` | Served cross-origin-isolated and run on real pthreads: 8 runtime workers, one page timing the same Monte Carlo work at 2/4/8 workers; speedup curve ~3.8× → ~7.5× → ~15×, serial == threaded pi at every count, `main returned 0` |
| `arena_frame` | Ran its frame-arena allocator demo to exit 0 |
| `system_info` | Printed real browser values: `OS: macOS`, `Num Cores: 14`, with the unprobeable parts degraded honestly |
| `tiny_pointers` | Ran all phases to PASS, with the abstract-claim coverage card collapsed by default |

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
| Threads and channels | **Runs today** | `digits_mlp_parallel`, `parallel_sum` and `parallel_scaling` run on real Emscripten pthreads over SharedArrayBuffer and Web Workers. The browser blocks SAB unless the page is cross-origin isolated, so those pages ship a COI service worker: open the card in a tab and it reloads once, isolated. |
| Sockets and HTTP | In progress | Emscripten's WebSocket-backed POSIX socket bridge (`-lwebsocket.js` / `PROXY_POSIX_SOCKETS`). |
| GPU kernels | In progress | WebGPU, with WGSL generated from the same `@gpu` AST that already emits Metal. |
| Embedded CPython | In progress | Pyodide, which is CPython itself compiled to WebAssembly. |
| File I/O | In progress | Emscripten's MEMFS and IDBFS filesystems. |
| Audio | Not attempted | The miniaudio and Metal audio backends have no browser counterpart yet; WebAudio is the route. |

## The seven that do not build

Each one stops at a named symbol. The gallery keeps their cards and prints the
reason on them.

| Example | Stops at | Why |
|---|---|---|
| `examples/effects/async_primitives.flow` | `flow_fiber_run_main` | Fiber runtime is a native C/assembly context switch |
| `examples/linalg/blas_demo.flow` | `cblas_dgemm` | Links a system BLAS |
| `examples/linalg/lu_decomposition.flow` | `cblas_dcopy` | Links a system BLAS |
| `examples/ml/digits_mlp_metal.flow` | `flow_gpu_alloc` | Metal GPU backend |
| `examples/ml/tape_mul.flow` | `flow_tape_reset` | Autodiff tape is a native runtime module |
| `examples/ai/ga_flappy.flow` | `fly` | Program references a symbol the transpiler does not emit |
| `examples/crypto/runtime_sha256.flow` | `flow_sha256` | Hashing helper lives in the native runtime pack |

Six examples used to fail and now build:

- `arena_frame.flow` and `manual_memory.flow` hit a real C-backend bug — the
  monomorphizer synthesized a second `sizeof_i32` next to the stdlib's concrete
  one, so the generated C redefined the symbol. The monomorphizer now resolves
  a generic specialization to an existing concrete declaration instead of
  synthesizing a twin.
- `digits_mlp.flow` now links `runtime/flow_rt_support.c` for the monotonic
  clock, like `tiny_pointers` does.
- `system_info.flow` gets browser stubs for its host-only externs: the OS and
  core count are read from the browser tab itself (`navigator.platform` /
  `navigator.hardwareConcurrency`), CPU feature flags degrade to `false`, and
  `print_kv_*` map to `printf`.
- `graphics.flow` was library-shaped (no `main`); it now carries a demo entry
  point that exercises the constructors, conversions and clamps and gates its
  exit code on a self-check.
- `digits_mlp_parallel.flow` now builds on real pthreads: Flow's parallel-for
  orchestration (`lib/runtime/concurrency_parallel.flow`) compiles as a library
  and lands on `pthread_create` over SharedArrayBuffer and Web Workers
  (`-pthread -sPROXY_TO_PTHREAD`, one pre-spawned worker per shard plus one
  for the proxied `main`). The browser only allows SharedArrayBuffer on
  cross-origin-isolated pages, so the page ships a COI service worker and
  explains that it must be opened in a tab. Its batch size was raised 250 →
  1000 so each spawn carries enough work to beat the ~1 ms proxied spawn
  cost; the measured in-browser speedup is ~1.9×.
- `parallel_sum.flow` (previously only in the `wasm-crossings` build) joins the
  gallery as the second threaded card. Its 12,000,000-iteration shards are the
  textbook coarse grain, so it is the more dramatic of the two: ~6.1–6.5× in
  Chrome, with a measured ~0.4 ms floor for 8 empty spawn+join round trips.
- `parallel_scaling.flow` is the third threaded card: one build, one page, and
  the program itself times the same Monte Carlo pi work partitioned over 2, 4
  and 8 workers, each worker count timed against its own serial baseline
  (different shard counts are different random samples). The measured curve in
  Chrome is ~3.8× → ~7.5× → ~15× — roughly linear scaling, monotone by the
  example's own PASS gate.

## Related

[Game Gallery](games.md) · [Morphogenesis Gallery](morphogenesis.md) ·
[WASM target notes](../language/wasm.md) ·
[recording demos](README.md) ·
[examples index](../../examples/README.md)
