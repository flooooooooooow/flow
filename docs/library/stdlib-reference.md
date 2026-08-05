# FLOW Standard Library Reference

Core API reference for commonly used standard library modules.
There are ~48 top-level modules under `lib/stdlib/` (plus audio/, ui/, …);
this page covers the subset below. See also [memory.md](memory.md),
[gpu-memory.md](gpu-memory.md), [autodiff.md](autodiff.md),
[rt-safety.md](rt-safety.md), and [async-effects.md](../language/async-effects.md).

## Table of Contents

1. [math.flow](#mathflow)
2. [string.flow](#stringflow)
3. [collections.flow](#collectionsflow)
4. [option.flow](#optionflow)
5. [result.flow](#resultflow)
6. [posix.flow](#posixflow)
7. [net.flow](#netflow)
8. [concurrent.flow](#concurrentflow)
9. [async.flow](#asyncflow)
10. [autodiff.flow](#autodiffflow)

---

## math.flow

Mathematical helpers in `lib/stdlib/math.flow` (mostly **`f32`**).
Bare C `math.h` names (`sin`, `cos`, `floor`, …) are also available via the
C backend as FFI/passthrough — those are **not** the same as the Flow exports
below.

### Arithmetic

| Function | Signature | Description |
|----------|-----------|-------------|
| `add` / `subtract` / `multiply` / `divide` | `(f32, f32) -> f32` | Basic ops |
| `power` | `(f32, f32) -> f32` | Integer-ish power via loop |
| `abs` / `fabs` | `(f32) -> f32` | Absolute value |

### Trig / exp / log / root

| Function | Signature | Description |
|----------|-----------|-------------|
| `sin` / `cos` / `tan` | `(f32) -> f32` | Trig (`sin`/`cos` are MLIR intrinsics / C-backed) |
| `sqrt` | `(f32) -> f32` | Square root |
| `log` | `(f32) -> f32` | Natural log (Newton) |
| `exp` | `(f32) -> f32` | e^x (Taylor) |

### Integer helpers

| Function | Signature | Description |
|----------|-----------|-------------|
| `fibonacci` | `(i32) -> i32` | Fibonacci |
| `gcd` / `lcm` | `(i32, i32) -> i32` | GCD / LCM |
| `is_prime` | `(i32) -> bool` | Primality |
| `factorial_big` | `(i32) -> i64` | Factorial |

### Constants

| Constant | Type | Description |
|----------|------|-------------|
| `PI` | `f32` | π |
| `E` | `f32` | Euler's number |
| `GOLDEN_RATIO` | `f32` | φ |

---

## string.flow

String manipulation.

### C String Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `strlen` | `(string) -> i32` | String length |
| `strcmp` | `(string, string) -> i32` | Compare strings |
| `strcpy` | `(ptr<i8>, string) -> ptr<i8>` | Copy string |
| `strcat` | `(ptr<i8>, string) -> ptr<i8>` | Concatenate |
| `strchr` | `(string, i32) -> ptr<i8>` | Find character |
| `strstr` | `(string, string) -> ptr<i8>` | Find substring |

### High-Level Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `str_equals` | `(string, string) -> bool` | Check equality |
| `str_less_than` | `(string, string) -> bool` | Lexicographic less |
| `str_len` | `(string) -> i32` | Get length |
| `str_is_empty` | `(string) -> bool` | Check if empty |

### Character Classification

| Function | Signature | Description |
|----------|-----------|-------------|
| `is_digit` | `(i32) -> bool` | Is 0-9 |
| `is_alpha` | `(i32) -> bool` | Is a-z or A-Z |
| `is_alnum` | `(i32) -> bool` | Is alphanumeric |
| `is_space` | `(i32) -> bool` | Is whitespace |
| `is_upper` | `(i32) -> bool` | Is uppercase |
| `is_lower` | `(i32) -> bool` | Is lowercase |
| `to_upper` | `(i32) -> i32` | Convert to uppercase |
| `to_lower` | `(i32) -> i32` | Convert to lowercase |

### Parsing

| Function | Signature | Description |
|----------|-----------|-------------|
| `parse_int` | `(string) -> i32` | Parse integer |
| `parse_long` | `(string) -> i64` | Parse long |
| `parse_float` | `(string) -> f64` | Parse float |

---

## collections.flow

Data structures.

### Vector_i32

Dynamic array of integers.

```flow
struct Vector_i32 {
    data: ptr<i32>,
    len: i32,
    capacity: i32
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `vector_i32_new` | `() -> Vector_i32` | Create empty vector |
| `vector_i32_len` | `(Vector_i32) -> i32` | Get length |
| `vector_i32_is_empty` | `(Vector_i32) -> bool` | Check if empty |

### Stack_i32

LIFO stack.

```flow
struct Stack_i32 {
    data: ptr<i32>,
    top: i32,
    capacity: i32
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `stack_i32_new` | `(i32) -> Stack_i32` | Create with capacity |
| `stack_i32_is_empty` | `(Stack_i32) -> bool` | Check if empty |
| `stack_i32_is_full` | `(Stack_i32) -> bool` | Check if full |

### Queue_i32

FIFO queue.

```flow
struct Queue_i32 {
    data: ptr<i32>,
    front: i32,
    rear: i32,
    size: i32,
    capacity: i32
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `queue_i32_new` | `(i32) -> Queue_i32` | Create with capacity |
| `queue_i32_is_empty` | `(Queue_i32) -> bool` | Check if empty |
| `queue_i32_is_full` | `(Queue_i32) -> bool` | Check if full |
| `queue_i32_len` | `(Queue_i32) -> i32` | Get size |

### HashMap_string_i32

Key-value store.

```flow
struct HashMap_string_i32 {
    buckets: ptr<HashEntry_string_i32>,
    size: i32,
    capacity: i32
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `hashmap_string_i32_new` | `(i32) -> HashMap_string_i32` | Create with capacity |
| `hashmap_string_i32_len` | `(HashMap_string_i32) -> i32` | Get size |
| `hashmap_string_i32_is_empty` | `(HashMap_string_i32) -> bool` | Check if empty |

### Set_i32

Set of unique integers.

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_i32_new` | `(i32) -> Set_i32` | Create with capacity |
| `set_i32_len` | `(Set_i32) -> i32` | Get size |
| `set_i32_is_empty` | `(Set_i32) -> bool` | Check if empty |

### LinkedList_i32

Doubly-linked list.

| Function | Signature | Description |
|----------|-----------|-------------|
| `linkedlist_i32_new` | `() -> LinkedList_i32` | Create empty list |
| `linkedlist_i32_len` | `(LinkedList_i32) -> i32` | Get length |
| `linkedlist_i32_is_empty` | `(LinkedList_i32) -> bool` | Check if empty |

### PriorityQueue_i32

Min-heap priority queue.

| Function | Signature | Description |
|----------|-----------|-------------|
| `pq_i32_new` | `(i32) -> PriorityQueue_i32` | Create with capacity |
| `pq_i32_is_empty` | `(PriorityQueue_i32) -> bool` | Check if empty |
| `pq_i32_len` | `(PriorityQueue_i32) -> i32` | Get size |

### Pair and Triple

```flow
struct Pair_i32_i32 { first: i32, second: i32 }
struct Triple_i32_i32_i32 { first: i32, second: i32, third: i32 }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `pair_i32_i32_new` | `(i32, i32) -> Pair_i32_i32` | Create pair |
| `triple_new` | `(i32, i32, i32) -> Triple_i32_i32_i32` | Create triple |

---

## option.flow

Optional values.

### Option_i32

```flow
struct Option_i32 {
    has_value: bool,
    value: i32
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `some_i32` | `(i32) -> Option_i32` | Create Some |
| `none_i32` | `() -> Option_i32` | Create None |
| `is_some_i32` | `(Option_i32) -> bool` | Check if Some |
| `is_none_i32` | `(Option_i32) -> bool` | Check if None |
| `unwrap_i32` | `(Option_i32) -> i32` | Get value (panics if None) |
| `unwrap_or_i32` | `(Option_i32, i32) -> i32` | Get value or default |

Also available: `Option_f32`, `Option_f64`, `Option_bool`

---

## result.flow

Error handling.

### Result_i32_string

```flow
struct Result_i32_string {
    is_ok: bool,
    value: i32,
    error: string
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `ok_i32_string` | `(i32) -> Result_i32_string` | Create Ok |
| `err_i32_string` | `(string) -> Result_i32_string` | Create Err |
| `is_ok_i32_string` | `(Result_i32_string) -> bool` | Check if Ok |
| `is_err_i32_string` | `(Result_i32_string) -> bool` | Check if Err |
| `unwrap_i32_string` | `(Result_i32_string) -> i32` | Get value |
| `unwrap_err_i32_string` | `(Result_i32_string) -> string` | Get error |

Also available: `Result_f32_string`, `Result_f64_string`

---

## posix.flow

POSIX system calls.

### File Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `open` | `(string, i32, i32) -> i32` | Open file |
| `close` | `(i32) -> i32` | Close file |
| `read` | `(i32, ptr<i8>, i32) -> i32` | Read from file |
| `write` | `(i32, ptr<i8>, i32) -> i32` | Write to file |
| `lseek` | `(i32, i64, i32) -> i64` | Seek in file |

### Constants

```flow
const O_RDONLY: i32 = 0
const O_WRONLY: i32 = 1
const O_RDWR: i32 = 2
const O_CREAT: i32 = 64
const O_TRUNC: i32 = 512
const O_APPEND: i32 = 1024

const SEEK_SET: i32 = 0
const SEEK_CUR: i32 = 1
const SEEK_END: i32 = 2
```

### Process Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `fork` | `() -> i32` | Fork process |
| `getpid` | `() -> i32` | Get process ID |
| `getppid` | `() -> i32` | Get parent PID |
| `exit` | `(i32) -> void` | Exit process |
| `kill` | `(i32, i32) -> i32` | Send signal |

### Environment

| Function | Signature | Description |
|----------|-----------|-------------|
| `getenv` | `(string) -> string` | Get env var |
| `setenv` | `(string, string, i32) -> i32` | Set env var |

### Directory Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `mkdir` | `(string, i32) -> i32` | Create directory |
| `rmdir` | `(string) -> i32` | Remove directory |
| `chdir` | `(string) -> i32` | Change directory |
| `unlink` | `(string) -> i32` | Delete file |

---

## net.flow

Networking.

### TCP

```flow
struct TcpListener { socket: Socket, port: i32 }
struct TcpStream { socket: Socket, connected: bool }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `tcp_listener_new` | `(i32) -> TcpListener` | Create listener |
| `tcp_stream_new` | `() -> TcpStream` | Create stream |
| `tcp_stream_is_connected` | `(TcpStream) -> bool` | Check connected |

### UDP

```flow
struct UdpSocket { socket: Socket, bound: bool }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `udp_socket_new` | `() -> UdpSocket` | Create socket |

### HTTP

```flow
struct HttpResponse { status_code: i32, body_length: i32, success: bool }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `http_get` | `(string) -> HttpResponse` | HTTP GET |
| `http_post` | `(string, string) -> HttpResponse` | HTTP POST |

### Constants

```flow
const AF_INET: i32 = 2
const AF_INET6: i32 = 10
const SOCK_STREAM: i32 = 1
const SOCK_DGRAM: i32 = 2
```

---

## concurrent.flow

POSIX-style concurrency primitives (`lib/stdlib/concurrent.flow`). See
[concurrency-vs-go.md](../language/concurrency-vs-go.md).

### Thread

```flow
struct Thread { id: i64, running: bool }
```

| Function | Description |
|----------|-------------|
| `thread_new` / `thread_spawn` / `thread_join` / `thread_is_running` | OS threads via `flow_thread_*` |

### Mutex / CondVar / RwLock

| Function | Description |
|----------|-------------|
| `mutex_new` / `bind` / `lock` / `unlock` / `trylock` / `destroy` | pthread mutex |
| `condvar_new` / `bind` / `wait` / `signal` / `broadcast` / `destroy` | condition variable |
| `rwlock_new` / `bind` / `rdlock` / `wrlock` / `unlock` / `destroy` | reader/writer lock |

### Channel_i32

Go-style buffered channel (pthread mutex + condvars). Fiber channels used by
benches live in `runtime/flow_fiber.c` and are **not** exported here.

| Function | Description |
|----------|-------------|
| `channel_i32_new` / `bind` | Create / lazy-bind |
| `channel_i32_send` / `try_send` / `recv` / `try_recv` | Blocking / non-blocking |
| `channel_i32_close` / `destroy` | Close / free buffer |
| `channel_i32_len` / `is_empty` / `is_full` / `is_closed` | Queries |
| `channel_i32_select2_try` / `channel_i32_select2` | Two-way select (0/1/-1) |

### Atomics

```flow
struct AtomicI32 { value: i32 }
struct AtomicI64 { value: i64 }
struct AtomicBool { value: bool }
```

| Function | Description |
|----------|-------------|
| `atomic_i32_new` / `load` / `store` (+ i64 / bool) | Create + ordered access |
| `MEMORY_ORDER_RELAXED` … `MEMORY_ORDER_SEQ_CST` | Order constants |

### Synchronization

| Function | Description |
|----------|-------------|
| `waitgroup_add` / `done` / `wait` / `count` | Go-style WaitGroup (condvar wait) |
| `once_new` / `bind` / `once_call_begin` / `once_call_end` / `once_is_done` | Run-once init |
| `spinlock_new` / `lock` / `unlock` / `is_locked` | Busy-wait lock |
| `semaphore_new` / `bind` / `wait` / `post` / `count` | Blocking semaphore |

---

## async.flow

Algebraic-effect async surface (`lib/stdlib/async.flow`). Full honesty notes:
[async-effects.md](../language/async-effects.md).

### Effects

| Effect | Ops |
|--------|-----|
| `Async` | `delay(ms)`, `spawn(task_id)`, `join(task_id) -> i32` |
| `AsyncIO` | `poll_read` / `poll_write` / `sleep_ms` |
| `TcpEffect` + `BlockingTcp` | `connect` / `send` / `recv` via `runtime/flow_tcp.c` |

### Capabilities

| Capability | Backend |
|------------|---------|
| `SimulatedAsync` | Deterministic sync stand-in (`join` → `id * 10`) |
| `ThreadedAsync` | OS threads (`runtime/flow_concurrency.c`) |
| `FiberAsync` | M:N cooperative fibers (`runtime/flow_fiber.c` + asm fctx) |
| `BlockingAsyncIO` | `usleep`; poll stubs return ready |
| `NetpollAsyncIO` | Real kqueue (Darwin) / epoll (Linux) |

### Helpers

| Function | Description |
|----------|-------------|
| `async_delay` / `async_spawn` / `async_join` | Thin `Async.*` wrappers |
| `async_sleep_ms` / `async_poll_read` | Thin `AsyncIO.*` wrappers |
| `async_set_maxprocs(n)` / `async_maxprocs()` | Fiber worker count (`FLOW_MAXPROCS`; `< 1` clamps to 1) |

---

## autodiff.flow

Automatic differentiation library (`lib/stdlib/autodiff.flow`).
**Library AD, not a compiler pass** — see [autodiff.md](autodiff.md).

### Dual Numbers

```flow
struct Dual { val: f32, grad: f32 }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `dual_var` | `(f32) -> Dual` | Variable (grad = 1) |
| `dual_const` / `d` | `(f32) -> Dual` | Constant (grad = 0) |
| `dx` | `(f32) -> Dual` | Alias of `dual_var` |
| `dual_add` / `sub` / `mul` / `div` | `(Dual, Dual) -> Dual` | Arithmetic |
| `dual_pow` / `dual_sq` / `dual_sqrt` | | Powers / roots |
| `dual_sin` / `cos` / `tan` / `exp` / `log` | `(Dual) -> Dual` | Elementary |
| `dual_relu` / `dual_sigmoid` / `dual_tanh` | `(Dual) -> Dual` | Activations |
| `dual_val` / `dual_grad` | `(Dual) -> f32` | Accessors |

Overloaded `add` / `sub` / `mul` / `neg` and helpers (`sigmoid`, `ln`, …)
are also exported — see the source for the full list. GPU elementwise
backward kernels: `lib/stdlib/gpu_gradients.flow`.
