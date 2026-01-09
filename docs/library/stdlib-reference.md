# FLOW Standard Library Reference

Complete API reference for all standard library modules.

## Table of Contents

1. [math.flow](#mathflow)
2. [string.flow](#stringflow)
3. [collections.flow](#collectionsflow)
4. [option.flow](#optionflow)
5. [result.flow](#resultflow)
6. [posix.flow](#posixflow)
7. [net.flow](#netflow)
8. [concurrent.flow](#concurrentflow)
9. [autodiff.flow](#autodiffflow)

---

## math.flow

Mathematical functions.

### Trigonometric

| Function | Signature | Description |
|----------|-----------|-------------|
| `sin` | `(f64) -> f64` | Sine |
| `cos` | `(f64) -> f64` | Cosine |
| `tan` | `(f64) -> f64` | Tangent |
| `asin` | `(f64) -> f64` | Arc sine |
| `acos` | `(f64) -> f64` | Arc cosine |
| `atan` | `(f64) -> f64` | Arc tangent |
| `atan2` | `(f64, f64) -> f64` | Two-argument arc tangent |

### Exponential & Logarithmic

| Function | Signature | Description |
|----------|-----------|-------------|
| `exp` | `(f64) -> f64` | e^x |
| `log` | `(f64) -> f64` | Natural logarithm |
| `log10` | `(f64) -> f64` | Base-10 logarithm |
| `log2` | `(f64) -> f64` | Base-2 logarithm |
| `pow` | `(f64, f64) -> f64` | Power (x^y) |

### Other

| Function | Signature | Description |
|----------|-----------|-------------|
| `sqrt` | `(f64) -> f64` | Square root |
| `abs` | `(f64) -> f64` | Absolute value |
| `floor` | `(f64) -> f64` | Floor |
| `ceil` | `(f64) -> f64` | Ceiling |
| `round` | `(f64) -> f64` | Round to nearest |
| `min` | `(f64, f64) -> f64` | Minimum |
| `max` | `(f64, f64) -> f64` | Maximum |

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `PI` | 3.14159... | π |
| `E` | 2.71828... | Euler's number |
| `TAU` | 6.28318... | 2π |

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

Concurrency primitives.

### Thread

```flow
struct Thread { id: i64, running: bool }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `thread_new` | `() -> Thread` | Create thread |
| `thread_is_running` | `(Thread) -> bool` | Check running |

### Mutex

```flow
struct Mutex { locked: bool, owner: i64 }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `mutex_new` | `() -> Mutex` | Create mutex |
| `mutex_is_locked` | `(Mutex) -> bool` | Check locked |

### Channel_i32

```flow
struct Channel_i32 {
    buffer: ptr<i32>,
    capacity: i32,
    size: i32,
    head: i32,
    tail: i32,
    closed: bool
}
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `channel_i32_new` | `(i32) -> Channel_i32` | Create channel |
| `channel_i32_is_empty` | `(Channel_i32) -> bool` | Check empty |
| `channel_i32_is_full` | `(Channel_i32) -> bool` | Check full |
| `channel_i32_is_closed` | `(Channel_i32) -> bool` | Check closed |

### Atomics

```flow
struct AtomicI32 { value: i32 }
struct AtomicI64 { value: i64 }
struct AtomicBool { value: bool }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `atomic_i32_new` | `(i32) -> AtomicI32` | Create atomic |
| `atomic_i64_new` | `(i64) -> AtomicI64` | Create atomic |
| `atomic_bool_new` | `(bool) -> AtomicBool` | Create atomic |

### Synchronization

```flow
struct WaitGroup { count: i32 }
struct SpinLock { locked: bool }
struct Once { done: bool }
```

---

## autodiff.flow

Automatic differentiation.

### Dual Numbers

```flow
struct Dual { val: f64, grad: f64 }
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `dual` | `(f64, f64) -> Dual` | Create dual number |
| `dual_add` | `(Dual, Dual) -> Dual` | Add |
| `dual_sub` | `(Dual, Dual) -> Dual` | Subtract |
| `dual_mul` | `(Dual, Dual) -> Dual` | Multiply |
| `dual_div` | `(Dual, Dual) -> Dual` | Divide |
| `dual_sin` | `(Dual) -> Dual` | Sine |
| `dual_cos` | `(Dual) -> Dual` | Cosine |
| `dual_exp` | `(Dual) -> Dual` | Exponential |
| `dual_log` | `(Dual) -> Dual` | Natural log |
| `dual_sigmoid` | `(Dual) -> Dual` | Sigmoid |
| `dual_tanh` | `(Dual) -> Dual` | Hyperbolic tangent |

### Helpers

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_val` | `(Dual) -> f64` | Get value |
| `get_grad` | `(Dual) -> f64` | Get gradient |
