# Real-time Audio Safety

`@rt_safe` marks callbacks that must not allocate, take locks, or call into
non-RT code. The typechecker rejects transitive `malloc` / arena use under
`--strict`.

Prerequisites: [audio-basics.md](audio-basics.md), [memory.md](memory.md).

## Part 1: What `@rt_safe` allows

Stack locals, fixed-bound loops, pure math: yes. Heap: no.

```flow
@rt_safe
function process_sample(x: f32, gain: f32) -> f32 {
    return x * gain
}

@rt_safe
function process_block(n: i32, gain: f32) -> f32 {
    let mut acc: f32 = 0.0
    let mut i: i32 = 0
    while i < n {
        let s: f32 = 0.1 * (i as f32)
        acc = acc + process_sample(s, gain)
        i = i + 1
    }
    return acc
}
```

```bash
./flow run examples/audio/rt_safe_callback.flow
```

### 1.1 Gain + clamp sketch (browser)

Interactive cousin of the RT callback, same math, no attribute (the browser
does not enforce `@rt_safe`):

```flow
function process_sample(x: f64, gain: f64) -> f64 {
    let y: f64 = x * gain
    if y > 1.0 { return 1.0 }
    if y < -1.0 { return -1.0 }
    return y
}

function main() -> i32 {
    let mut acc: f64 = 0.0
    for i in 0 to 8 {
        let s: f64 = 0.1 * (i as f64)
        acc = acc + process_sample(s, 0.5)
    }
    printf("acc=%f\n", acc)
    return 0
}
```

### 1.2 Soft clip (browser)

```flow
function soft_clip(x: f64) -> f64 {
    if x > 1.0 { return 1.0 }
    if x < -1.0 { return -1.0 }
    return x - (x * x * x) / 3.0
}

function main() -> i32 {
    printf("%f %f\n", soft_clip(0.5), soft_clip(1.5))
    return 0
}
```

### 1.3 One-pole lowpass (browser)

```flow
function main() -> i32 {
    let a: f64 = 0.2
    let mut y: f64 = 0.0
    let x: f64 = 1.0
    for n in 0 to 20 {
        y = y + a * (x - y)
    }
    printf("y=%f\n", y)
    return 0
}
```

### 1.4 Fixed ring buffer (browser)

Preallocated delay line, legal on an RT path:

```flow
function main() -> i32 {
    let mut buf: array<f64, 8> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    let mut w: i32 = 0
    for n in 0 to 10 {
        let x: f64 = (n as f64) * 0.1
        let r: i32 = (w + 4) % 8
        let y: f64 = buf[r]
        buf[w] = x
        w = (w + 1) % 8
        if n == 9 {
            printf("delayed=%f\n", y)
        }
    }
    return 0
}
```

### 1.5 Block energy (browser)

```flow
function main() -> i32 {
    let mut e: f64 = 0.0
    for i in 0 to 16 {
        let s: f64 = 0.05 * (i as f64)
        e = e + s * s
    }
    printf("energy=%f\n", e)
    return 0
}
```

### 1.6 Dry/wet mix (browser)

```flow
function main() -> i32 {
    let dry: f64 = 0.8
    let wet: f64 = 0.3
    let mix: f64 = 0.25
    let out: f64 = dry * (1.0 - mix) + wet * mix
    printf("out=%f\n", out)
    return 0
}
```

## Part 2: What gets rejected

```flow
# Illegal under --strict @rt_safe checking:
# extern { function malloc(size: i64) -> ptr<void> }
# @rt_safe
# function bad() -> void {
#     let p: ptr<void> = malloc(16)
# }
```

Preallocate buffers in the non-RT setup path; only touch them from the
callback.

### 2.1 Setup vs callback split (browser)

```flow
function main() -> i32 {
    # "setup" — would allocate natively; here a fixed buffer
    let capacity: i32 = 8
    let mut buf: array<f64, 8> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    # "callback" — only touches preallocated storage
    let mut i: i32 = 0
    while i < capacity {
        buf[i] = 0.0
        i = i + 1
    }
    printf("cleared=%d\n", capacity)
    return 0
}
```

## Part 3: Next

- [audio-basics.md](audio-basics.md), oscillators, mix, RMS sketches
- [RT safety guide](../library/rt-safety.md)
- [`examples/audio/lattice_allpass_phase_engine.flow`](../../examples/audio/lattice_allpass_phase_engine.flow)

## Reference

- [docs/library/rt-safety.md](../library/rt-safety.md)
- [`lib/stdlib/audio.flow`](../../lib/stdlib/audio.flow)
