# Concurrency Patterns

> Educational concurrency shapes that **run in the browser** via `printf`.
> Parts 1-3 simulate mutexes and channels with arrays, no real threads.
>
> **Real concurrency (shipped):** `lib/stdlib/concurrent.flow` (pthread channels,
> WaitGroup, mutexes), `lib/stdlib/async.flow` (`FiberAsync` / `ThreadedAsync` /
> `NetpollAsyncIO`), OpenMP `parallel for`, and runnable demos under
> `examples/concurrency/`. Design + Go comparison:
> [concurrency-vs-go.md](../language/concurrency-vs-go.md).

## Part 1: Mutex-shaped counters

### 1.1 Locked counter increment

A mutex is modeled as `locked: 0|1`. Only increment while holding the lock.

```flow
struct MutexCounter {
    value: i32,
    locked: i32
}

function mutex_lock(m: ptr<MutexCounter>) -> void {
    if m[0].locked == 1 {
        printf("wait: already locked\n")
    }
    m[0].locked = 1
}

function mutex_unlock(m: ptr<MutexCounter>) -> void {
    m[0].locked = 0
}

function counter_inc(m: ptr<MutexCounter>) -> void {
    mutex_lock(m)
    m[0].value = m[0].value + 1
    printf("inc -> %d\n", m[0].value)
    mutex_unlock(m)
}

function main() -> i32 {
    let mut c: MutexCounter = MutexCounter { value: 0, locked: 0 }
    counter_inc(&c)
    counter_inc(&c)
    counter_inc(&c)
    printf("final=%d\n", c.value)
    return 0
}
```

### 1.2 Simulated workers under one lock

Two "workers" take turns incrementing; the lock serializes updates.

```flow
struct MutexCounter {
    value: i32,
    locked: i32
}

function with_lock_add(c: ptr<MutexCounter>, worker: i32, delta: i32) -> void {
    c[0].locked = 1
    c[0].value = c[0].value + delta
    printf("worker %d added %d -> %d\n", worker, delta, c[0].value)
    c[0].locked = 0
}

function main() -> i32 {
    let mut c: MutexCounter = MutexCounter { value: 0, locked: 0 }
    for step in 0 to 4 {
        let worker: i32 = step % 2
        with_lock_add(&c, worker, 1)
    }
    printf("shared=%d\n", c.value)
    return 0
}
```

### 1.3 Try-lock skip when busy

If the lock is held, skip the update instead of waiting.

```flow
struct MutexCounter {
    value: i32,
    locked: i32
}

function try_inc(c: ptr<MutexCounter>) -> i32 {
    if c[0].locked == 1 {
        printf("busy: skip\n")
        return 0
    }
    c[0].locked = 1
    c[0].value = c[0].value + 1
    c[0].locked = 0
    printf("ok -> %d\n", c[0].value)
    return 1
}

function main() -> i32 {
    let mut c: MutexCounter = MutexCounter { value: 0, locked: 0 }
    try_inc(&c)
    c.locked = 1
    try_inc(&c)
    c.locked = 0
    try_inc(&c)
    printf("final=%d\n", c.value)
    return 0
}
```

## Part 2: Channel-shaped queues

### 2.1 Bounded channel send/recv

A fixed array + head/tail/count is a channel-shaped queue (FIFO).

```flow
struct Chan {
    data: [i32; 4],
    head: i32,
    tail: i32,
    count: i32
}

function chan_send(ch: ptr<Chan>, v: i32) -> i32 {
    if ch[0].count >= 4 {
        printf("full: drop %d\n", v)
        return 0
    }
    ch[0].data[ch[0].tail] = v
    ch[0].tail = (ch[0].tail + 1) % 4
    ch[0].count = ch[0].count + 1
    printf("send %d (count=%d)\n", v, ch[0].count)
    return 1
}

function chan_recv(ch: ptr<Chan>) -> i32 {
    if ch[0].count == 0 {
        printf("empty\n")
        return -1
    }
    let v: i32 = ch[0].data[ch[0].head]
    ch[0].head = (ch[0].head + 1) % 4
    ch[0].count = ch[0].count - 1
    printf("recv %d (count=%d)\n", v, ch[0].count)
    return v
}

function main() -> i32 {
    let mut ch: Chan = Chan {
        data: [0, 0, 0, 0],
        head: 0,
        tail: 0,
        count: 0
    }
    chan_send(&ch, 10)
    chan_send(&ch, 20)
    chan_send(&ch, 30)
    printf("got %d\n", chan_recv(&ch))
    printf("got %d\n", chan_recv(&ch))
    return 0
}
```

### 2.2 Producer then consumer

Fill the channel, then drain it, a single-threaded producer/consumer sketch.

```flow
struct Chan {
    data: [i32; 8],
    head: i32,
    tail: i32,
    count: i32
}

function chan_send(ch: ptr<Chan>, v: i32) -> void {
    ch[0].data[ch[0].tail] = v
    ch[0].tail = (ch[0].tail + 1) % 8
    ch[0].count = ch[0].count + 1
}

function chan_recv(ch: ptr<Chan>) -> i32 {
    let v: i32 = ch[0].data[ch[0].head]
    ch[0].head = (ch[0].head + 1) % 8
    ch[0].count = ch[0].count - 1
    return v
}

function main() -> i32 {
    let mut ch: Chan = Chan {
        data: [0, 0, 0, 0, 0, 0, 0, 0],
        head: 0,
        tail: 0,
        count: 0
    }

    printf("produce:\n")
    for i in 0 to 5 {
        chan_send(&ch, (i + 1) * 10)
        printf("  %d\n", (i + 1) * 10)
    }

    printf("consume:\n")
    while ch.count > 0 {
        printf("  %d\n", chan_recv(&ch))
    }
    return 0
}
```

### 2.3 Channel full / empty edges

Exercise both capacity limits with printf feedback.

```flow
struct Chan {
    data: [i32; 2],
    head: i32,
    tail: i32,
    count: i32
}

function try_send(ch: ptr<Chan>, v: i32) -> i32 {
    if ch[0].count >= 2 {
        return 0
    }
    ch[0].data[ch[0].tail] = v
    ch[0].tail = (ch[0].tail + 1) % 2
    ch[0].count = ch[0].count + 1
    return 1
}

function try_recv(ch: ptr<Chan>) -> i32 {
    if ch[0].count == 0 {
        return -1
    }
    let v: i32 = ch[0].data[ch[0].head]
    ch[0].head = (ch[0].head + 1) % 2
    ch[0].count = ch[0].count - 1
    return v
}

function main() -> i32 {
    let mut ch: Chan = Chan { data: [0, 0], head: 0, tail: 0, count: 0 }
    printf("empty recv=%d\n", try_recv(&ch))
    printf("send1=%d\n", try_send(&ch, 1))
    printf("send2=%d\n", try_send(&ch, 2))
    printf("send3(full)=%d\n", try_send(&ch, 3))
    printf("recv=%d\n", try_recv(&ch))
    printf("recv=%d\n", try_recv(&ch))
    printf("recv(empty)=%d\n", try_recv(&ch))
    return 0
}
```

## Part 3: Combining shapes

### 3.1 Fan-in: two producers, one queue

Two producers enqueue into one channel; the consumer drains in order.

```flow
struct Chan {
    data: [i32; 8],
    head: i32,
    tail: i32,
    count: i32
}

function send(ch: ptr<Chan>, v: i32) -> void {
    ch[0].data[ch[0].tail] = v
    ch[0].tail = (ch[0].tail + 1) % 8
    ch[0].count = ch[0].count + 1
}

function recv(ch: ptr<Chan>) -> i32 {
    let v: i32 = ch[0].data[ch[0].head]
    ch[0].head = (ch[0].head + 1) % 8
    ch[0].count = ch[0].count - 1
    return v
}

function main() -> i32 {
    let mut ch: Chan = Chan {
        data: [0, 0, 0, 0, 0, 0, 0, 0],
        head: 0,
        tail: 0,
        count: 0
    }

    # Producer A
    send(&ch, 100)
    send(&ch, 101)
    # Producer B
    send(&ch, 200)
    send(&ch, 201)

    while ch.count > 0 {
        printf("fan-in %d\n", recv(&ch))
    }
    return 0
}
```

### 3.2 Work queue drain

Push jobs, then process until empty, a simple job-queue sketch.

```flow
struct WorkQ {
    jobs: [i32; 6],
    head: i32,
    tail: i32,
    count: i32
}

function enqueue(q: ptr<WorkQ>, job: i32) -> void {
    q[0].jobs[q[0].tail] = job
    q[0].tail = (q[0].tail + 1) % 6
    q[0].count = q[0].count + 1
}

function dequeue(q: ptr<WorkQ>) -> i32 {
    let job: i32 = q[0].jobs[q[0].head]
    q[0].head = (q[0].head + 1) % 6
    q[0].count = q[0].count - 1
    return job
}

function main() -> i32 {
    let mut q: WorkQ = WorkQ {
        jobs: [0, 0, 0, 0, 0, 0],
        head: 0,
        tail: 0,
        count: 0
    }
    enqueue(&q, 7)
    enqueue(&q, 8)
    enqueue(&q, 9)

    let mut done: i32 = 0
    while q.count > 0 {
        let job: i32 = dequeue(&q)
        done = done + job
        printf("work job=%d total=%d\n", job, done)
    }
    printf("queue empty total=%d\n", done)
    return 0
}
```

## Part 4: Native concurrency (next step)

The sketches above **simulate** mutexes and channels with arrays. On a real
binary:

```bash
./flow run examples/concurrency/channels.flow
./flow run examples/concurrency/select.flow
./flow run examples/concurrency/fiber_async.flow
./flow run examples/concurrency/parallel_for.flow
```

| Surface | Where |
|---------|--------|
| pthread channels / mutex / WaitGroup | `lib/stdlib/concurrent.flow` |
| Fibers / threaded async | `lib/stdlib/async.flow` |
| `parallel for` (OpenMP when available) | language + examples |
| Design vs Go | [concurrency-vs-go.md](../language/concurrency-vs-go.md) |

The browser will never run OS threads; use these commands when you leave the
tutorial app.
