# WASM crossings

Four things people assume a systems language cannot take to WebAssembly:
OS threads, the GPU, sockets, and an embedded CPython. Flow does all four in
runtime C or in its own codegen, so each one is a concrete question with a
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
