# Independent Tutorial: Building a tiny DSP program in Flow

Author: community
Date: November 2026

This is an independent community tutorial covering a small Digital Signal Processing concept in Flow.

```flow
import "stdlib/math.flow"

function run_dsp() -> i32 {
    let mut val: f32 = 0.0
    for i in 0..10 {
        val = sin(val + 0.1)
    }
    return 0
}

function main() -> i32 {
    return run_dsp()
}
```
