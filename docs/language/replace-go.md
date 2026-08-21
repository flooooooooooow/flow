# Replacing Go with Flow

> Goal: Flow is a drop-in *better* choice for the jobs people pick Go for —
> network services, CLIs, concurrent pipelines — with **effects**, **no GC**,
> and **faster** cores where measured.

Companion: [concurrency-vs-go.md](concurrency-vs-go.md) ·
[benchmarks/concurrency/RESULTS.md](../../benchmarks/concurrency/RESULTS.md)

## Scorecard (2026-08-04, arm64 Darwin)

| Go strength | Flow answer | Status |
|-------------|-------------|--------|
| Goroutines | Asm M:N fibers (`FiberAsync`, `FLOW_MAXPROCS`) | ✅ Ship — ping-pong **~2× faster** than Go |
| Channels | `Chan<T>` (mono) + `Channel_i32`/`i64` + `select2`/`select4` | ✅ Ship |
| `GOMAXPROCS` | `flow_fiber_set_maxprocs` / `FLOW_MAXPROCS` / `async_set_maxprocs` | ✅ Ship |
| Netpoller | `NetpollAsyncIO` — kqueue/epoll; **fiber-park** on poll | ✅ Ship |
| `select` | `select2` + `select4` (+ `_try` = default) | ✅ Ship (up to 4) |
| Fast numerics | C backend ≈ C; `parallel for` | ✅ Often beats Go |
| Stdlib HTTP/net | Routed HTTP selftest + TCP helpers + microbench | ✅ Growing |
| Race detector | `FLOW_RACE=1` lock-order + shadow; `FLOW_TSAN=1` | ✅ Basic |
| Module ecosystem | Local registry index + git/path deps | 🔶 Early |
| Mid-function suspend | FiberAsync runs `main` on a fiber; park suspends Flow frames | ✅ Ship |
| Delimited continuations | `flow_cont` scaffold (+ shift/resume demo) | 🔶 Scaffold |

## How to write “Go-shaped” Flow

```flow-pseudocode
import "stdlib/async.flow"
import "stdlib/concurrent.flow"

function main() -> i32 {
    async_set_maxprocs(2)
    handle Async with FiberAsync {
        async_spawn(1)
        async_spawn(2)
        let a: i32 = async_join(1)
        let b: i32 = async_join(2)
        printf("%d\n", a + b)
    }
    handle AsyncIO with NetpollAsyncIO {
        async_sleep_ms(1)
        # async_poll_read(fd, timeout_ms) — parks fiber when on one
    }
    return 0
}
```

## Why Flow can replace Go (not just copy it)

1. **Effects** — swap `FiberAsync` / `ThreadedAsync` / `SimulatedAsync` without
   rewriting call sites. Go hard-codes its runtime.
2. **No GC** — latency-sensitive paths (`@rt_safe` audio) stay predictable.
3. **Same binary story as C** — deploy anywhere clang goes; FFI is natural.
4. **Measured speed** — fiber ping-pong and buffered channel throughput beat Go
   on current benches; see RESULTS.md.

## Remaining gaps

- Full compiler multi-shot `shift`/`reset` rewrite (C `resume_multi` / `clone` + stack-blob ship; true stack-frame restore still open)
- Full HTTP/2 (HPACK dynamic table, multiplexing, server push) — minimal h2 preface/HEADERS/DATA selftest ships

## Runtime map

| Piece | Path |
|-------|------|
| Asm context switch | `runtime/flow_fctx_*.S` |
| M:N fibers + steal | `runtime/flow_fiber.c` (`work_steal.flow`) |
| Netpoller | `runtime/flow_netpoll.c` + `flow_netpoll_fiber.c` |
| HTTP microbench | `runtime/flow_http_bench.c` |
| Race hooks | `runtime/flow_race.c` (`FLOW_RACE=1`); `FLOW_TSAN=1` → `-fsanitize=thread` |
| Cont scaffold | `Cont.shift` M:N-safe; `resume_multi` + `clone`/stack-blob (`cont_stackcopy.flow`) |
| HTTP routed + mw | request-id + Bearer auth; fiber-per-conn (`http_fiber.flow`) |
| HTTPS accept-loop | OpenSSL PEM + ALPN `http/1.1` + minimal `h2` (`http_tls.flow`) |
| HTTP hello | `flow_http_serve_hello` / `examples/concurrency/http_hello.flow` |
| HTTP client (curl) | `registry/packages/http` (GET/POST over HTTPS) |
| POSIX sync + channels | `lib/stdlib/concurrent.flow` |
| Effects surface | `lib/stdlib/async.flow` |

**CI:** GitHub Actions workflows are disabled (`.github/workflows/*.yml.disabled`).
