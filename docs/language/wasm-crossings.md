# WASM crossings

Five things people assume a systems language cannot take to WebAssembly: OS
threads, the GPU, sockets, files, and an embedded CPython. Flow does all five
in runtime C or in its own codegen, so each one is a concrete question with a
concrete answer.

Each section below gives the mechanism, the constraint that made people think
it was impossible, the workaround, and a number measured in a real browser.

Demo pages live under `site/wasm-crossings/<name>/`. Serve them and open them:

```
python3 -m http.server -d site 8000
open http://127.0.0.1:8000/wasm-crossings/threads/
```

| crossing | status | headline number |
| --- | --- | --- |
| 1. OS threads | proven in Chrome | 7.78x on 8 workers, identical results |
| 2. GPU via WebGPU | proven in Chrome | 1,048,576 / 1,048,576 elements bit-identical |
| 3. Sockets | proven in Chrome | 8 / 8 round trips, best rtt 2.20 ms |
| 5. Filesystem | proven in Chrome | GIF byte-identical to native; counter survives reload |

Measurements below were taken in Chrome 141 on an Apple M-series laptop
(`navigator.hardwareConcurrency` = 14: 10 performance cores, 4 efficiency
cores), served by `python3 -m http.server` with no special headers.

---

## 1. OS threads

### Mechanism

Flow's concurrency runtime is pthreads. `parallel for` and
`flow_parallel_for_i32` (`lib/runtime/concurrency_parallel.flow`) split a range
into chunks and hand each chunk to `flow_rt_par_spawn`, which is a
`pthread_create` in `runtime/flow_rt_parallel.c`. Nothing above that layer
knows or cares what a thread is.

Emscripten implements pthreads for real: `pthread_create` starts a Web Worker,
and every worker instantiates the same `WebAssembly.Module` over the same
`WebAssembly.Memory`, which is backed by a `SharedArrayBuffer`. Atomics and
futexes map onto `Atomics.wait` / `Atomics.notify`. The Flow source and the
Flow runtime are unchanged; only the link line differs.

Build it with:

```
./flow wasm examples/wasm/parallel_sum.flow --threads --workers 8
```

which is `wasm/flow_wasm_threads.py`. It compiles the program twice from one
source: once with `-pthread`, once without, and writes both plus the page into
`site/wasm-crossings/threads/`.

### The constraint people trip over

**SharedArrayBuffer is gated behind cross-origin isolation.** After Spectre,
browsers only expose `SharedArrayBuffer` to a page whose *server* sends

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

GitHub Pages will not send those headers, and neither will
`python3 -m http.server`. Without them `crossOriginIsolated` is `false`,
`SharedArrayBuffer` is undefined, and the threaded module refuses to
instantiate. This is the reason "you can't ship threaded WASM on a static
host" is folklore.

**The browser main thread must not block.** Flow's parallel-for joins its
workers. `pthread_join` on the browser main thread would deadlock the event
loop that the workers need in order to start.

### The workaround

*Isolation:* a service worker. A service worker sits between the page and the
network and can rewrite responses, so it adds the two headers the server
refused to. `wasm/crossing_assets/coi-serviceworker.js` is ~40 lines: in page
context it registers itself and reloads once; in worker context it re-fetches
every request and returns a copy carrying COOP, COEP and CORP. On the second
load `crossOriginIsolated` flips to `true`. It needs a secure context, which
both GitHub Pages (https) and a local server on 127.0.0.1 satisfy. The reload
is guarded by `sessionStorage` so a browser that refuses to install the worker
degrades to "threads unavailable" rather than looping.

*Blocking:* `-sPROXY_TO_PTHREAD`. `main()` runs on a worker instead of the
browser main thread, so it is allowed to block in `pthread_join`, and the
browser main thread stays free to service worker startup and `postMessage`.
`-sPTHREAD_POOL_SIZE=N+1` prewarms one worker per shard plus one for the
proxied `main()`, so `pthread_create` never has to spin a worker up from cold
in the middle of a measurement.

Full link line for the threaded build:

```
emcc -O2 -pthread -sPROXY_TO_PTHREAD -sPTHREAD_POOL_SIZE=9 \
     -sMODULARIZE=1 -sEXIT_RUNTIME=1 -sINITIAL_MEMORY=134217728 \
     -DFLOW_PAR_WORKERS=8 ...
```

The control build is the same command with `-pthread` and the two pthread
flags removed. There `pthread_create` fails, and Flow's parallel-for already
handles that: `flow_rt_par_spawn` returns -1 and the chunk runs inline. The
program stays correct and simply stops going faster, which is exactly what a
control should do.

### Measured, in Chrome

`examples/wasm/parallel_sum.flow`: 8 disjoint shards, 12,000,000 iterations
each, summed per shard into its own slot, then reduced serially in fixed shard
order. Best of 4 passes per configuration.

| build | serial pass | threaded pass | speedup | sum |
| --- | --- | --- | --- | --- |
| threaded (`-pthread`) | 78.57 ms | 10.10 ms | **7.78x** | 19594.457638786 |
| single-thread control | 77.89 ms | 78.14 ms | 1.00x | 19594.457638786 |

Page state at the time: `crossOriginIsolated: true`, `SharedArrayBuffer:
available`, served over plain HTTP by `python3 -m http.server`. Console clean.

Three things worth reading off that table:

* 7.78x on 8 workers is near-linear. The threads are real OS threads on real
  cores, not a scheduler trick.
* Both builds agree on the serial pass (78.57 vs 77.89 ms), so the threaded
  build costs nothing per-thread once V8 has tiered up.
* All four passes produce a bit-identical sum. Shards touch disjoint memory
  and the reduction order is fixed, so threading changes the schedule and
  nothing else.

An empty `parallel_for` over 8 shards, measured on the same page, costs
**0.155 ms** for 8 spawn-and-join round trips, so about 19 microseconds per
Emscripten thread out of a prewarmed pool.

### The grain caveat

That 19 microseconds is roughly 20x what a native `pthread_create` costs, and
it is the whole story for fine-grained work. `examples/ml/digits_mlp_parallel.flow`
splits every minibatch across 8 shards, which is 5,760 spawn-join round trips
over a full run. Compiled to WASM with the identical flags and run under
Node 25:

```
  serial:   grad+update ms  93.59   test_acc 99.00%
  parallel: grad+update ms 204.40   test_acc 99.00%
  speedup: 0.46x
```

Natively the same program gets 4.16x. The parallel build is still *correct*
under WASM (the two runs agree to the last bit), it is just slower, because a
shard is worth ~16 microseconds of work and costs ~19 microseconds to
dispatch. Nothing about the browser is broken here; the grain is simply below
the threshold. Coarsen the shards and the speedup comes back, which is what
`parallel_sum.flow` demonstrates.

### First-run numbers lie

V8 compiles WASM at a fast baseline tier first and re-optimises in the
background. On the first pass the threaded build measured 187 ms serial
against the control's 79 ms, which looks like a 2.4x penalty for `-pthread`
and is not. After warm-up both builds land at 78 ms. The demo takes the best
of 4 passes for this reason; a benchmark that runs a WASM workload once is
measuring the baseline compiler.

---

## 2. The GPU, via WebGPU

### Mechanism

Flow owns its shader codegen. `src/flow/metal_codegen.py` walks an `@gpu`
function's AST and prints Metal Shading Language. `src/flow/wgsl_codegen.py`
is its sibling: same AST, same walk, WGSL out. There is no LLVM, no SPIR-V and
no vendor compiler in between, so adding a shading language costs one file.

```
./flow gpu lib/stdlib/gpu_kernels.flow           # Metal, as before
./flow gpu lib/stdlib/gpu_kernels.flow --wgsl    # WGSL, same AST
```

`wasm/flow_wasm_gpu.py` builds the demo. It takes one Flow file and produces
two things from it:

* a `.wgsl` per `@gpu` function, plus a small JSON reflection (binding indices,
  storage access modes, uniform layout, workgroup size) so the JavaScript host
  never has to re-parse Flow;
* the same file through `src/flow/c_generator.py` into WASM, where the kernel
  bodies become ordinary C.

The CPU reference is not a re-implementation. Flow's C generator already emits
a `gpu_thread_id()` stub, so `wasm/crossing_assets/gpu_thread_id_shim.c`
replaces it with one backed by a variable, and a Flow driver loop advances that
variable and calls the kernel once per element. Both columns of the comparison
come from the same AST.

### Where WGSL forced a different structure from Metal

Two things in `wgsl_codegen.py` are not a transliteration of the Metal backend:

* **Buffers carry an access mode.** Metal binds everything as `device T*`.
  WGSL needs `var<storage, read>` or `var<storage, read_write>` declared up
  front. The generator decides per parameter by walking the body for
  assignments through that name, rather than guessing from whether the
  identifier contains "out".
* **Scalars cannot be loose bindings.** Metal takes
  `constant int& n [[buffer(k)]]`. WGSL wants a uniform block, so every scalar
  parameter is packed into one `Params` struct, padded to a multiple of 16
  bytes, and referenced as `params.<name>`.

Two smaller ones: WGSL has a long reserved-word list, so Flow identifiers that
collide get a trailing underscore; and WGSL has no `f64`, so a kernel using it
is rejected with a clear message instead of emitting something that will not
compile. The generator also keeps `elif` chains, which the Metal backend
silently drops.

`gpu_vector_add` comes out as:

```wgsl
@group(0) @binding(0) var<storage, read> a: array<f32>;
@group(0) @binding(1) var<storage, read> b: array<f32>;
@group(0) @binding(2) var<storage, read_write> out: array<f32>;

struct Params { n: i32, _pad0: u32, _pad1: u32, _pad2: u32, };
@group(0) @binding(3) var<uniform> params: Params;

@compute @workgroup_size(64)
fn gpu_vector_add(@builtin(global_invocation_id) global_id: vec3<u32>, ...) {
    let tid: i32 = i32(global_id.x);
    let i: i32 = tid;
    if ((i < params.n)) {
        out[i] = (a[i] + b[i]);
    }
}
```

### Measured, in Chrome

Adapter reported by WebGPU: `apple metal-3`. 1,048,576 f32 elements per buffer,
inputs generated inside the WASM heap so the GPU and the CPU reference are
handed exactly the same bytes. Each side is run twice and the second run is
reported.

| kernel | GPU (WGSL) | CPU (WASM) | exact matches | max abs diff | verdict |
| --- | --- | --- | --- | --- | --- |
| `gpu_vector_add` | 2.80 ms | 2.30 ms | 1048576 / 1048576 | 0 | bit-identical |
| `gpu_elementwise_mul` | 2.60 ms | 2.00 ms | 1048576 / 1048576 | 0 | bit-identical |
| `gpu_saxpy` | 3.10 ms | 1.80 ms | 1048576 / 1048576 | 0 | bit-identical |
| `gpu_heavy_mix` | 2.80 ms | 201.50 ms | 199007 / 1048576 | 1.3e-3 | 9.0e-7 relative |

The milestone is the first row: a Flow `@gpu` kernel, compiled by Flow to WGSL,
dispatched on a real GPU from a browser, agreeing with the CPU on every one of
a million elements. Console clean.

The GPU timings include buffer upload, dispatch and readback. The first three
kernels are memory-bound at one arithmetic operation per element, so the GPU
loses to a straight-line WASM loop; that is what those rows are for. First
dispatch of a kernel costs an extra 3 to 34 ms for shader compilation and
pipeline creation, reported separately on the page.

`gpu_heavy_mix` does 128 square roots per element and the GPU wins by **72x**.
It is checked to a tolerance rather than for bit equality, because WGSL only
promises `sqrt` to within 1 ulp. The measured disagreement is 9.0e-7 relative,
which is the ulp noise of summing 128 terms.

### A negative result worth keeping

An earlier draft of that kernel chained its 256 steps: `acc = sqrt(abs(acc *
scale + 0.5))`. Only 524,258 of 1,048,576 elements matched and the max relative
difference was 268. Nothing was wrong with the GPU or the codegen. The map is
chaotic, so a 1-ulp difference in one `sqrt` grows into a completely different
answer. Numerical agreement tests on a GPU need a kernel whose error does not
amplify, or they measure chaos instead of correctness.

---

## 3. Sockets

### Mechanism

`runtime/flow_tcp.c` is `socket()`, `connect()`, `send()`, `recv()`, `close()`
and nothing else, and `lib/runtime/tcp.flow` is a thin Flow surface over it.
The file compiles for wasm unmodified.

Emscripten's SOCKFS implements the BSD socket calls over WebSockets. A
`connect()` to `127.0.0.1:9505` opens `ws://127.0.0.1:9505/` with the `binary`
subprotocol, and every `send`/`recv` becomes a binary WebSocket frame. Flow's
`flow_rt_tcp_connect` already hard-codes loopback, which is exactly the shape
this maps onto.

```
python3 scripts/ws_echo_relay.py --port 9505 --tcp-port 9506
python3 wasm/flow_wasm_sockets.py
```

### The constraint people trip over

**A browser cannot open a raw TCP socket.** Not to localhost, not to anywhere.
There is no API for it and there will not be one, because a page that could
speak arbitrary TCP could port-scan your intranet. Whatever is on the far end
has to speak WebSocket. This is a browser security rule and it is not a Flow
limitation; the same wall stops every language.

`scripts/ws_echo_relay.py` is the far end, written against the Python standard
library so the demo has no dependencies: an HTTP upgrade handshake, a frame
codec, and an echo. It also serves plain TCP on a second port so the identical
Flow program can be run natively for comparison.

**Nothing may block.** Emscripten's `connect()` cannot wait for the handshake,
so it returns success immediately and finishes later; `recv()` reports EAGAIN
until the first frame lands. Both events arrive on the browser event loop, and
a WASM module spinning in a poll loop never lets that loop run.

### The workaround

`-sASYNCIFY`, and a poll loop that yields. `flow_net_yield` in
`wasm/crossing_assets/net_yield_shim.c` is `emscripten_sleep` under WASM and
`usleep` natively, so one Flow source runs in both places. ASYNCIFY unwinds
the WASM stack at the sleep, returns to the event loop, and resumes where it
left off, which is what lets a straight-line `send`-then-`recv` program work
inside a browser.

### Measured, in Chrome

Relay on `127.0.0.1:9505` (WebSocket) and `127.0.0.1:9506` (plain TCP).
`examples/wasm/tcp_echo.flow` sends 8 messages of 32 bytes, waits for each
echo, and compares the returned bytes to what it sent.

| build | transport | round trips | best rtt | mean rtt |
| --- | --- | --- | --- | --- |
| browser (WASM) | `ws://127.0.0.1:9505/` | **8 / 8** | 2.20 ms | 3.40 ms |
| native (clang) | TCP `127.0.0.1:9506` | 8 / 8 | 0.092 ms | 0.116 ms |

Both PASS: every echo matched byte for byte. The relay's own log confirms it
saw eight 32-byte binary frames and sent eight back. Console clean.

The browser is roughly 24x slower per round trip, and almost all of that is
the poll loop's own granularity: `emscripten_sleep` is a `setTimeout`, whose
floor in a foreground tab is about 4 ms. It is measuring the browser's timer,
not the network.

### Background tabs distort this badly

The first run of this demo reported a 748 ms mean round trip. The tab was not
foregrounded, and Chrome clamps `setTimeout` in a background tab to roughly
1 Hz. Every poll that had to yield waited a full second. Foregrounding the tab
took the mean from 748 ms to 3.4 ms with no code change. Any WASM benchmark
that sleeps needs a visible tab, or it is measuring throttling.

---

## 5. The filesystem

### Mechanism

`fopen`, `fread`, `fwrite`, `fclose`, `mkdir`. Emscripten answers all of them
out of a virtual filesystem, so a Flow program that writes a file writes a
file. Three backends matter:

| backend | what it is | lifetime |
| --- | --- | --- |
| MEMFS | a filesystem in the module's heap, the default | until the page unloads |
| IDBFS | a MEMFS image backed by an IndexedDB store | survives reloads, if synced |
| preload | `emcc --preload-file` packs a host directory into a `.data` blob | read-only, present before `main()` |

```
./flow wasm examples/wasm/fs_counter.flow --fs idbfs
./flow wasm examples/wasm/fs_preload.flow --fs memfs --preload examples/wasm/data@/data
python3 wasm/flow_wasm_fs.py          # builds all three demos and the page
```

### The constraints people trip over

**IDBFS does not persist on its own.** The mount is an in-memory image; the
IndexedDB store behind it is only touched when someone calls `FS.syncfs`.
Inbound (`syncfs(true)`) has to finish before the program starts, or it reads
an empty directory. Outbound (`syncfs(false)`) has to run after the program
finishes, or the write is lost when the tab closes. Both are async and the
Flow program is synchronous, so the host has to bracket the run.

**A Flow program cannot fetch its own inputs.** There is no blocking read from
the network inside WASM. Data an example needs has to be in the filesystem
before `main()` runs.

### The workaround

For IDBFS, mount in `preRun` and hold up startup with a run dependency:

```js
preRun: [function (mod) {
  mod.FS.mkdir("/persist");
  mod.FS.mount(mod.IDBFS, {}, "/persist");
  mod.addRunDependency("idbfs-in");
  mod.FS.syncfs(true, () => mod.removeRunDependency("idbfs-in"));
}]
```

then `-sINVOKE_RUN=0` so the page calls `callMain()` itself and can run
`syncfs(false)` afterwards. `IDBFS` lives inside the module closure, so it has
to be named in `EXPORTED_RUNTIME_METHODS` alongside `FS` before the page can
reach it. `-sFORCE_FILESYSTEM=1` keeps the filesystem when the linker cannot
see a use for it.

For inputs, `--preload-file DIR@/mount`. The loader fetches the `.data` blob
and unpacks it into MEMFS before `main()`, so a relative `fopen` just works.

### Measured, in Chrome

**Flow writes a GIF, the browser renders it.**
`examples/graphics/gif_writer.flow` is compiled for wasm unmodified. It draws
24 frames of a bouncing square and encodes them with the pure-Flow GIF89a
encoder in `lib/stdlib/gif.flow`, writing `build/gif_demo.gif` byte by byte
with `fwrite`. The page reads the bytes back out of MEMFS, walks the GIF block
structure, hashes them, and hands them to an `<img>`.

| | |
| --- | --- |
| path in MEMFS | `/build/gif_demo.gif` |
| bytes written | 51,303 |
| header | `GIF89a` 128x128 |
| frames parsed | 24, trailer present |
| sha256 | `9bbb1327b8f74b69dd87e50f65adafe7da7d2eaca963c646604ab2596844f59b` |
| same file as a native clang build | yes, byte for byte |
| browser decoded it | yes, 128x128, animating |

The file the Flow encoder produced inside WASM is the same file it produces
natively, to the byte, and Chrome's own GIF decoder renders it.

**IDBFS persistence.** `examples/wasm/fs_counter.flow` reads a counter, adds
one, writes it back, then reads it again to check. Observed across a real page
reload:

| | count before | count after | syncfs in / out | result |
| --- | --- | --- | --- | --- |
| first run, state wiped | 0 | 1 | true / true | PASS |
| second run, same page | 1 | 2 | true / true | PASS |
| after `location.reload()` | 2 | 3 | true / true | PASS |
| next run | 3 | 4 | true / true | PASS |

The 2 to 3 step is the one that matters: the module was torn down and rebuilt
from scratch, and the counter came back from IndexedDB.

**Preloaded input.** `examples/wasm/fs_preload.flow` opens
`data/fs_input.txt`, a path that only exists because `--preload-file` put it
there. Browser: 291 bytes, 5 lines, checksum 49099. Native run of the same
program against the real file on disk: 291 bytes, 5 lines, checksum 49099.

Console clean on all three.
