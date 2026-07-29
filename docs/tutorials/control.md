# Control Flow

> If, while, for, and early returns.


## Part 1: Branching

### 1.1 If / else

```flow
function main() -> i32 {
    let x: i32 = 7
    if x % 2 == 0 {
        printf("even\n")
    } else {
        printf("odd\n")
    }
    return 0
}
```
### 1.2 Elif ladder

```flow
function grade(score: i32) -> void {
    if score >= 90 {
        printf("A\n")
    } elif score >= 80 {
        printf("B\n")
    } elif score >= 70 {
        printf("C\n")
    } else {
        printf("below C\n")
    }
}

function main() -> i32 {
    grade(95)
    grade(82)
    grade(60)
    return 0
}
```

## Part 2: Loops

### 2.1 While countdown

```flow
function main() -> i32 {
    let mut n: i32 = 5
    while n > 0 {
        printf("%d\n", n)
        n = n - 1
    }
    printf("lift off\n")
    return 0
}
```
### 2.2 For range

```flow
function main() -> i32 {
    for i in 0 to 5 {
        printf("%d\n", i * i)
    }
    return 0
}
```
### 2.3 Nested loops

```flow
function main() -> i32 {
    for y in 0 to 3 {
        for x in 0 to 3 {
            printf("%d ", x + y)
        }
        printf("\n")
    }
    return 0
}
```

## Part 3: Returns

### 3.1 Early return

```flow
function first_neg(xs: ptr<i32>, n: i32) -> i32 {
    for i in 0 to n {
        if xs[i] < 0 {
            return xs[i]
        }
    }
    return 0
}

function main() -> i32 {
    let xs: [i32; 4] = [3, 1, -2, 5]
    printf("%d\n", first_neg(xs, 4))
    return 0
}
```
### 3.2 Clamp helper

```flow
function clamp(x: i32, lo: i32, hi: i32) -> i32 {
    if x < lo { return lo }
    if x > hi { return hi }
    return x
}

function main() -> i32 {
    printf("%d %d %d\n", clamp(-5, 0, 10), clamp(3, 0, 10), clamp(99, 0, 10))
    return 0
}
```
