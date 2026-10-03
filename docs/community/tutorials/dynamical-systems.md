# Independent Tutorial: Writing a dynamical system directly in Flow

Author: community
Date: October 2026

This is an independent community tutorial explaining how to write a simple dynamical system in Flow.

```flow
import "stdlib/math.flow"

function run_dynamical_system() -> i32 {
    let mut x: f32 = 1.0
    for i in 0..10 {
        x = x * 1.5
    }
    return 0
}

function main() -> i32 {
    return run_dynamical_system()
}
```
