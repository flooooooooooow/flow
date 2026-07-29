# Audio Basics

> Sample math and simple DSP-shaped loops (no device I/O).


## Part 1: Samples

### 1.1 Gain

```flow
function main() -> i32 {
    let mut s: [i32; 4] = [10, 20, 30, 40]
    let gain: i32 = 2
    for i in 0 to 4 {
        s[i] = s[i] * gain
        printf("%d ", s[i])
    }
    printf("\n")
    return 0
}
```
### 1.2 Clamp sample

```flow
function clamp16(x: i32) -> i32 {
    if x > 32767 { return 32767 }
    if x < -32768 { return -32768 }
    return x
}

function main() -> i32 {
    printf("%d %d\n", clamp16(40000), clamp16(-40000))
    return 0
}
```

## Part 2: Oscillators

### 2.1 Saw phase

```flow
function main() -> i32 {
    let mut phase: i32 = 0
    let incr: i32 = 20
    for n in 0 to 8 {
        printf("%d ", phase)
        phase = phase + incr
        if phase >= 100 {
            phase = phase - 100
        }
    }
    printf("\n")
    return 0
}
```
### 2.2 Mix two buffers

```flow
function main() -> i32 {
    let a: [i32; 4] = [10, 10, 10, 10]
    let b: [i32; 4] = [1, 2, 3, 4]
    for i in 0 to 4 {
        printf("%d ", (a[i] + b[i]) / 2)
    }
    printf("\n")
    return 0
}
```

## Part 3: Envelope

### 3.1 Linear fade in

```flow
function main() -> i32 {
    let mut x: i32 = 100
    for i in 0 to 5 {
        let env: i32 = i * 20
        printf("%d ", x * env / 100)
    }
    printf("\n")
    return 0
}
```
### 3.2 RMS-ish energy

```flow
function main() -> i32 {
    let xs: [i32; 4] = [3, 4, 0, 0]
    let mut acc: i32 = 0
    for i in 0 to 4 {
        acc = acc + xs[i] * xs[i]
    }
    printf("energy=%d\n", acc)
    return 0
}
```
