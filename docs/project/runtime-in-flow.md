# Runtime-in-Flow

> Status: Phases 0–2 + follow-on (async, parallel, benches, tape, cont/http/tcp,
> sysinfo, crypto, audio stub, live stubs, threads/race wrappers) landed.

Flow moves **logic** into always-linked modules under [`lib/runtime/`](../../lib/runtime/),
keeping **kernels** (asm, OS, Metal/Cocoa/SDL, miniaudio device, CPython) native.

## Boundary

| Stay native forever | Why |
|---|---|
| `flow_fctx_*.S`, `flow_fctx_init.c` | ns fiber swap ABI |
| Fiber `run_one` / worker loop / stacks / fchan (`flow_fiber.c`) | calls asm; TLS park/handoff |
| `flow_thread_*` kernels, atomics (`flow_concurrency.c`) | pthread + `__atomic_*` |
| Race TLS tables (`flow_race.c` hooks) | must stay off hot path |
| Cont park/shift/reset (`flow_cont.c`) | fiber + TLS frames |
| Channel/sum **hot loops** in `flow_rt_cchan.c` | Must stay tight C |
| Parallel-for **worker loop** in `flow_rt_parallel.c` | fn-pointer invoke |
| HTTP/TCP sockets + parse/snprintf | BSD sockets |
| `flow_netpoll*.c`, Metal/Cocoa/SDL, miniaudio device, Python embed | platform |

| Flow runtime modules | Replaces / owns |
|---|---|
| `time.flow` | `jit_time` |
| `audio_simd.flow` / `audio_spsc.flow` | interleaved f32 + RT ring |
| `audio_device_stub.flow` | no-backend `flow_audio_*` (skipped when miniaudio linked) |
| `gpu_memory_stub.flow` | non-Darwin GPU ABI |
| `sysinfo_probes.flow` / `sysinfo_print.flow` | host probes + print |
| `concurrency_async.flow` / `fiber_async.flow` | ThreadedAsync / FiberAsync |
| `fiber_benches.flow` / `fiber_netpoll.flow` | fiber bench + netpoll demo |
| `concurrency_parallel.flow` / `concurrency_benches.flow` | parallel-for + chan benches |
| `netpoll_bench.flow` | netpoll sleep timing |
| `tcp.flow` / `http_routed.flow` / `http_bench.flow` | TCP API + HTTP harness |
| `tape.flow` / `cont.flow` | AD tape + cont probe/demo/arm |
| `crypto.flow` | `flow_sha256` / `flow_random_bytes` |
| `threads.flow` / `race.flow` | thread + race probe wrappers |
| `live_stubs.flow` | live host/plugin placeholders |
| `shader_host.flow` | shader CLI (not always-linked) |

Thin forever C: `flow_rt_support.c`, `flow_rt_task_store.c`, `flow_rt_fiber_async.c`,
`flow_rt_parallel.c`, `flow_rt_cchan.c`, `flow_rt_tape_store.c`, `flow_rt_sysinfo.c`,
`flow_rt_crypto.c`.

## Build

`./flow` transpiles `lib/runtime/*.flow` with `--c --library --lenient` and links them
into every binary. `FLOW_SKIP_AUDIO_STUB=1` when `./flow audio` links miniaudio.

## Phase 3 — push the boundary (planned)

Rewrite order, respecting the stay-native table above. Each step keeps the
gates below green and preserves observable behavior.

| Wave | Move to Flow | How |
|---|---|---|
| 1 | `flow_rt_crypto.c` SHA-256 core | Pure computation; port transform/init/update/final to `crypto.flow`; keep `flow_rt_random_bytes` as a 10-line C shim over `getentropy`/`arc4random` |
| 1 | `gfx_record.c` recorder logic | PPM writing, env parsing, key script via `fopen`/`getenv` externs; C keeps nothing but the gfx ABI symbol table |
| 1 | `flow_http_bench.c` harness | Finish the port into `http_bench.flow` |
| 1 | `flow_rt_sysinfo.c` probes | `sysconf`/`sysctlbyname` via externs into `sysinfo_probes.flow` |
| 2 | `flow_tls.c` session logic | HTTP/2 framing, HPACK literals, read/write retry loops, and selftest orchestration in `tls.flow`; OpenSSL calls become guarded 3-line C shims |
| 3 | Thin-shim shrink | Reduce `flow_rt_support/task_store/tape_store` to the fn-pointer trampolines only; everything else in Flow |

Findings from wave 1 (2026-08-05): `flow_rt_sysinfo.c` is irreducible platform
glue (`#if` per-OS branches, per-OS `_SC_*` constants) and stays as-is.
`flow_tcp.c` socket setup stays native because `sockaddr_in` layout differs per
OS (`sin_len` on BSD/macOS). `flow_cont.c` demo bodies must run as C callbacks
on fiber stacks, so the demo surface is already at the boundary. Done in wave 1:
SHA-256 core (`crypto.flow`, bit-exact vs hashlib) and the HTTP bench serve +
client loops (`http_bench.flow`); C keeps the CSPRNG and the threaded
accept-loop server.

Progress (2026-08-05, evening): all planned waves have landed.
- TLS/HTTP2 protocol logic in `tls.flow` (576 lines Flow; `flow_tls.c` 702 to
  478, OpenSSL shims + cert machinery only). Selftest output byte-identical.
- HTTP response formatting and route parsing in `http_routed.flow` (pure Flow
  byte assembly; `flow_tcp.c` 338 to 275). Remaining C: middleware globals
  needing atomics, sockets, thread/fiber harnesses.
- Recorder logic in `gfx_record.flow` (env contract, key scripts, PPM writing;
  `gfx_record.c` 237 to 186, ABI table + framebuffer only). Frames
  byte-identical to the C recorder.
- Module statics landed as a language feature (LANGUAGE_SPEC 3.3.1), unlocking:
  tape store fully in Flow (`flow_rt_tape_store.c` deleted) and the task store
  shrunk to its pthread trampoline (109 to 68 lines). Shared mutable state
  stays mutex-guarded exactly as before; function-pointer tables and pthread_t
  arrays stay in C.

Stays native regardless: fctx asm + init, fiber worker loop, pthread/atomic
kernels, race TLS tables, cchan and parallel-for hot loops, netpoll kqueue/epoll,
Metal/Cocoa/SDL, miniaudio device, CPython embed.

## Gates

```bash
./flow test-runtime tests/runtime/test_{threaded_async,fiber_async,parallel_for,concurrent_channels}.flow
./flow run examples/concurrency/{cont_demo,http_routed,fiber_netpoll,http_hello}.flow
./flow run examples/crypto/runtime_sha256.flow
./flow run examples/ml/tape_mul.flow
FLOW_CFLAGS='-O2' ./flow run benchmarks/concurrency/chan_pingpong_fiber.flow
```
