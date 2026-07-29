# Functions

> Parameters, returns, recursion, and composition.


## Part 1: Basics

### 1.1 Add

```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function main() -> i32 {
    printf("%d\n", add(2, 40))
    return 0
}
```
### 1.2 Multiple params

```flow
function lerp(a: i32, b: i32, t: i32) -> i32 {
    return a + (b - a) * t / 100
}

function main() -> i32 {
    printf("%d\n", lerp(0, 100, 25))
    return 0
}
```

## Part 2: Recursion

### 2.1 Factorial

```flow
function fact(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * fact(n - 1)
}

function main() -> i32 {
    printf("%d\n", fact(6))
    return 0
}
```
### 2.2 Fibonacci

```flow
function fib(n: i32) -> i32 {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

function main() -> i32 {
    for i in 0 to 10 {
        printf("%d ", fib(i))
    }
    printf("\n")
    return 0
}
```

## Part 3: Composition

### 3.1 Pipeline-ish

```flow
function double(x: i32) -> i32 { return x * 2 }
function inc(x: i32) -> i32 { return x + 1 }

function main() -> i32 {
    printf("%d\n", double(inc(10)))
    return 0
}
```
### 3.2 void helpers

```flow
function banner(msg: string) -> void {
    printf("== %s ==\n", msg)
}

function main() -> i32 {
    banner("flow")
    banner("functions")
    return 0
}
```
