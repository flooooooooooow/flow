# Flow vs Go — Concurrency Microbenchmarks

**Machine:** Apple Silicon arm64 (Darwin)  
**Date:** 2026-08-04  
**Flow:** `FLOW_CFLAGS='-O2'` · **Go:** `go run`

Re-run: `benchmarks/concurrency/run.sh`  
Strategy: [docs/language/replace-go.md](../../docs/language/replace-go.md)

## Results

| Bench | N | Flow | Go | Winner |
|-------|---|------|-----|--------|
| Buffered channel throughput | 200k | **~2× faster** | — | Flow |
| Fiber channel ping-pong (asm M:1) | 1M, buf=64 | **~8–14 ms** | ~21–26 ms | **Flow (~2×)** |
| Fiber fan-out sum (M:N, 256 fibers) | 50M | **~1–7 ms** | ~10 ms | **Flow** |
| Parallel fill | 8M | ~tie | ~tie | noise |
| HTTP server (loopback GET) | 2k | ~11.6k rps | ~13.7k rps | Go (thin accept loop vs `net/http`) |

### Ping-pong progression (Flow)

| Runtime | ms |
|---------|-----|
| pthread | ~80 |
| ucontext fibers | ~39 |
| asm M:1 fibers | **~9** |
| Go goroutines | ~22 |

## How to read this

- Default `FiberAsync` is **M:N** (per-worker deques + work-stealing; workers =
  `FLOW_MAXPROCS` / CPU count). See `examples/concurrency/work_steal.flow`.
- The **ping-pong** number forces `maxprocs=1` (M:1) for a fair context-switch
  microbench against Go.
- **Fan-out** uses default maxprocs (true M:N; steals show up under load).
- Fiber channels used by these benches live in `runtime/flow_fiber.c` and are
  **not** yet a Flow stdlib API — pthread `channel_i32_*` is the public surface.
- HTTP routed server: `/`, `/api`, `/health`, 404 + `X-Request-Id` middleware
  (`examples/concurrency/http_middleware.flow`).
- HTTPS accept-loop (OpenSSL PEM + ALPN http/1.1): `examples/concurrency/http_tls.flow`.

## Runtime features (Go replacement)

| Feature | Flow |
|---------|------|
| GOMAXPROCS | `FLOW_MAXPROCS` / `async_set_maxprocs` (`< 1` clamps to 1) |
| Goroutines | `FiberAsync` M:N + work-stealing deques |
| Netpoller | `NetpollAsyncIO` (kqueue/epoll; fiber-parked poll) |
| select | `select2` / `select4` (+ try/default) |
| Race hooks | `FLOW_RACE=1` lock-order (`runtime/flow_race.c`) |
| Channels | `concurrent.flow` (pthread); fiber chans = C runtime / benches |
| HTTP | routed + request-id middleware (`flow_http_*`) |
