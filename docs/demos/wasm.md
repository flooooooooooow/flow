# WebAssembly Gallery

158 Flow examples compiled to WebAssembly — every one of them runnable in a
browser. Every one is the unedited source from this repository, put through
Flow → C → `emcc`.

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
| [Games](../wasm/index.html) | 25 of 25 | 944 KB | Every `*_gfx.flow` in `examples/games/`, the same sources [the GIF gallery](games.md) records |
| [Morphogenesis](../wasm/index.html) | 40 of 40 | 2044 KB | Every field simulation in `examples/morphogenesis/`, see [the gallery](morphogenesis.md) |
| [Basics](../wasm/index.html) | 24 of 24 | 557 KB | `examples/basics/`, pure computation printing into the page (including the threaded `parallel_sum` and `parallel_scaling`) |
| [Language and compilers](../wasm/index.html) | 23 of 23 | 638 KB | Generics, traits, enums, effect rows, and Flow tools written in Flow |
| [Numerics and dynamics](../wasm/index.html) | 20 of 20 | 683 KB | Solvers, optimisers, linear algebra, control theory |
| [Learning](../wasm/index.html) | 12 of 12 | 455 KB | Small models and agents |
| [Systems and data](../wasm/index.html) | 14 of 14 | 524 KB | Allocators, hash tables, hashing, parsers, file formats |

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
| `tape_mul` | Computed `dz/dx = 4.000000`, `dz/dy = 3.000000` on the real Flow tape, `main returned 0` |
| `ga_flappy` | Neuroevolution ran to completion with `PASS: evolved policy clears >= 10 more pipes than random`, `main returned 0` |
| `blas_demo` | Benchmarked 256/512 gemms at 0.7/2.1 GFLOPS and 100/500 solves with `info=0`, `Done!`, `main returned 0` |
| `lu_decomposition` | `x = [1.000000, 1.000000, 1.000000]`, `max |Ax-b| = 0.00e+00`, `OK: solve + lu_factor via BLAS/LAPACK`, `main returned 0` |
| `async_primitives` | All three backends ran, and the FiberAsync section printed a strict round-robin trace (`T100:0 T101:0 T102:0 T100:1 …`) — three cooperative fibers suspending mid-body on `async_delay`, `join` summing to 3039, `main returned 0` |
| `runtime_sha256` | Flow's own SHA-256 implementation ran in the browser: `crypto runtime ok` against the known empty-string digest, exit 0; the card notes that random bytes come from WebCrypto's CSPRNG |
| `digits_mlp_metal` | The Metal API ran CPU-emulated (backend reports `cpu-emulated (wasm)`): the relu backward gate verified `GPU == CPU` on 8000 elements and all four elementwise benches matched the CPU reference, `PASS`, `main returned 0`; the card notes the timing rows are CPU loops, not GPU dispatches |

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
| Fibers | **Runs today** | `async_primitives` runs main and its tasks as stackful cooperative fibers (`runtime/fiber_wasm.c` over the Emscripten fiber API, which is Asyncify stack switching — the wasm analogue of the native `flow_fctx_*.S` asm context switch). M:1 on one JS thread, `flow_fiber_*` API intact: spawn/yield/park/unpark/run/run_until and fiber-aware `async_delay`. Pages build with `-sASYNCIFY`. |
| Sockets and HTTP | In progress | Emscripten's WebSocket-backed POSIX socket bridge (`-lwebsocket.js` / `PROXY_POSIX_SOCKETS`). |
| GPU kernels | In progress | WebGPU, with WGSL generated from the same `@gpu` AST that already emits Metal. |
| Embedded CPython | In progress | Pyodide, which is CPython itself compiled to WebAssembly. |
| File I/O | In progress | Emscripten's MEMFS and IDBFS filesystems. |
| Audio | Not attempted | The miniaudio and Metal audio backends have no browser counterpart yet; WebAudio is the route. |

## Every example builds

The last holdout was `digits_mlp_metal.flow`: its Metal API has no browser
counterpart, so `flow_gpu_*` are CPU-emulated on wasm (unified buffers become
plain `malloc`'d memory, `flow_gpu_mul_f32` an elementwise CPU loop). The
example's correctness gate still runs — the relu backward `dh = da · mask`
verifies `GPU == CPU` — and its card carries a `.degrade` note saying the
"gpu ms" rows measure a CPU loop, not a dispatch.

Nine examples used to fail and now build:

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
- `tape_mul.flow` runs the real reverse-mode AD tape: `lib/runtime/tape.flow`
  (pure Flow, replacing the deleted `runtime/flow_tape.c`) compiles in as a
  library TU via the new `extra_flow_runtime` build option — the wasm analogue
  of the native launcher's `flow_runtime_flow_sources()`. It was previously
  mislabelled a "native runtime module"; the fix is a module-resolution
  plumbing fix, not a stub, and the page computes `dz/dx = 4`, `dz/dy = 3`
  with zero console errors.
- `ga_flappy.flow` exposed a real compiler bug: its `fly()` call sites passed
  an int literal for a `u32` parameter plus an untyped constant, and the
  sole-overload fallback in `resolve_call` `break`-ed on the literal mismatch
  before discovering the unknown-typed argument, so the call was emitted
  unmangled while the definition was mangled (`undefined symbol fly`). The
  fallback now discovers unknown arg types up front; the example was broken
  natively too and now runs everywhere with its own PASS gate.
- `blas_demo.flow` and `lu_decomposition.flow` get `runtime/blas_wasm.c` — a
  plain, numerically correct shim for exactly the routines the stdlib calls
  (daxpy/dcopy/ddot/dnrm2/dscal/dgemv/dgemm + dgesv_/dgetrf_, linked via
  `extra_c`), matching Accelerate's semantics including column-major LAPACK.
  Both run fully in the browser: `lu_decomposition` reports
  `max |Ax-b| = 0.00e+00`, `blas_demo` benchmarks 0.7→2.1 GFLOPS gemms and
  natively-identical solves. These two were also broken under `./flow run`
  (the launcher never linked a BLAS).
- The `clock()` externs in `blas_demo.flow`, `falling_sand_gfx.flow`,
  `render3d.flow`, `fmm2d.flow` and `planet.flow` declared `-> i64`, but
  emscripten's `clock_t` is `i32`, so the import got a `signature_mismatch`
  stub that threw `unreachable` the first time a page timed something
  (blas_demo's first benchmark, falling_sand's FPS loop, ...). They now
  declare `-> i32` — µs-scale values fit i32 on both platforms.
- `parallel_scaling.flow` is the third threaded card: one build, one page, and
  the program itself times the same Monte Carlo pi work partitioned over 2, 4
  and 8 workers, each worker count timed against its own serial baseline
  (different shard counts are different random samples). The measured curve in
  Chrome is ~3.8× → ~7.5× → ~15× — roughly linear scaling, monotone by the
  example's own PASS gate.
- `async_primitives.flow` was the last "host-bound" failure that wasn't. The
  fiber runtime is pure Flow + portable C; only the context switch was native
  assembly. The wasm page gets `runtime/fiber_wasm.c` — the `flow_fiber_*`
  API on the Emscripten fiber API (Asyncify stack switching; wasm cannot
  hand-switch the stack pointer and plain `setjmp`/`longjmp` cannot move
  between stacks, so this is the supported setjmp/longjmp-family primitive) —
  plus `lib/runtime/fiber_async.flow` via `extra_flow_runtime` and
  `runtime/flow_rt_fiber_async.c`. The example grew a FiberAsync section that
  registers three Flow task bodies and proves real interleaving: a strict
  round-robin trace, `join(100..102) = 3039`, on M:1 at `async_set_maxprocs(1)`.
  Building it also surfaced a latent C-backend gap — skip-listed POSIX
  externs like `usleep` were never declared because the generated C did not
  include `<unistd.h>` — which the transpiler now does when such an extern is
  present (async_primitives was the first program to call one).
- `runtime_sha256.flow` was a stub candidate until it turned out that
  `lib/runtime/crypto.flow` is pure Flow — SHA-256 included, with no externs.
  The page links it as a library TU, so Flow's own hashing implementation runs
  in the browser and verifies the known empty-string digest. The only
  host-bound piece is the OS CSPRNG: `runtime/crypto_wasm.c` provides
  `flow_rt_random_bytes` via WebCrypto's synchronous `crypto.getRandomValues`
  (a real CSPRNG), and the card carries a `.degrade` note saying so. Gallery
  cards for built-but-different examples can now carry such a note via the
  `note` field in `PAGE_EXTRAS`.
- `digits_mlp_metal.flow` was the last non-builder. Its Metal runtime is
  genuinely Apple-only, so `flow_gpu_*` are CPU-emulated in `EXTERN_STUBS`:
  `flow_gpu_alloc` returns `malloc`'d memory (unified-buffer semantics),
  `flow_gpu_host_ptr` is the identity, `flow_gpu_mul_f32` runs the
  elementwise loop on the CPU, and the backend reports `cpu-emulated (wasm)`
  in the page's own output. The example was already written with a CPU
  reference on the other side of every check, so it runs the full
  correctness gate (`GPU == CPU`) and the four sizing benches to `PASS`, with
  the card's `.degrade` note flagging that nothing dispatches to a GPU.

## Related

[Game Gallery](games.md) · [Morphogenesis Gallery](morphogenesis.md) ·
[WASM target notes](../language/wasm.md) ·
[recording demos](README.md) ·
[examples index](../../examples/README.md)
