# Independent Tutorial: Trying Flow as a C/C++ programmer

Author: community
Date: November 2026

This is an independent community tutorial introducing Flow to C/C++ developers.

```flow
function cpp_programmer_example() -> i32 {
    let mut sum: i32 = 0
    for i in 0..10 {
        sum = sum + i
    }
    return sum
}

function main() -> i32 {
    if cpp_programmer_example() == 45 {
        return 0
    }
    return 1
}
```
