# Pointers

> Work with `ptr<T>`, null, and indexing.


## Part 1: Basics

### 1.1 Null pointer

```flow
function main() -> i32 {
    let p: ptr<i32> = null
    if p == null {
        printf("null\n")
    }
    return 0
}
```
### 1.2 Point at stack array

```flow
function main() -> i32 {
    let mut xs: [i32; 3] = [10, 20, 30]
    let p: ptr<i32> = xs
    printf("%d %d %d\n", p[0], p[1], p[2])
    p[1] = 99
    printf("xs[1]=%d\n", xs[1])
    return 0
}
```
### 1.3 Pass pointer to function

```flow
function bump(p: ptr<i32>) -> void {
    p[0] = p[0] + 1
}

function main() -> i32 {
    let mut x: i32 = 41
    bump(&x)
    printf("%d\n", x)
    return 0
}
```

## Part 2: Indexing

### 2.1 Walk a buffer

```flow
function main() -> i32 {
    let mut data: [i32; 5] = [1, 2, 3, 4, 5]
    let p: ptr<i32> = data
    for i in 0 to 5 {
        printf("%d ", p[i])
    }
    printf("\n")
    return 0
}
```
### 2.2 Swap via pointers

```flow
function swap(a: ptr<i32>, b: ptr<i32>) -> void {
    let t: i32 = a[0]
    a[0] = b[0]
    b[0] = t
}

function main() -> i32 {
    let mut x: i32 = 1
    let mut y: i32 = 2
    swap(&x, &y)
    printf("%d %d\n", x, y)
    return 0
}
```
### 2.3 Pointer to struct field path

```flow
struct Cell {
    value: i32
}

function main() -> i32 {
    let mut c: Cell = Cell { value: 7 }
    let p: ptr<Cell> = &c
    p[0].value = 8
    printf("%d\n", c.value)
    return 0
}
```

## Part 3: Safety

### 3.1 Guard before deref

```flow
function read_or_neg1(p: ptr<i32>) -> i32 {
    if p == null {
        return -1
    }
    return p[0]
}

function main() -> i32 {
    printf("%d\n", read_or_neg1(null))
    let mut v: i32 = 5
    printf("%d\n", read_or_neg1(&v))
    return 0
}
```
### 3.2 Length + pointer pair

```flow
function print_slice(p: ptr<i32>, n: i32) -> void {
    for i in 0 to n {
        printf("%d ", p[i])
    }
    printf("\n")
}

function main() -> i32 {
    let mut xs: [i32; 4] = [4, 3, 2, 1]
    print_slice(xs, 4)
    return 0
}
```
