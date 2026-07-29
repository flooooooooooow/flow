# Arrays

> Fixed arrays, loops, and in-place algorithms.


## Part 1: Fixed arrays

### 1.1 Declare and print

```flow
function main() -> i32 {
    let xs: [i32; 4] = [1, 2, 3, 4]
    for i in 0 to 4 {
        printf("%d ", xs[i])
    }
    printf("\n")
    return 0
}
```
### 1.2 Sum

```flow
function main() -> i32 {
    let xs: [i32; 5] = [5, 4, 3, 2, 1]
    let mut s: i32 = 0
    for i in 0 to 5 {
        s = s + xs[i]
    }
    printf("%d\n", s)
    return 0
}
```
### 1.3 Max

```flow
function main() -> i32 {
    let xs: [i32; 5] = [3, 9, 2, 7, 4]
    let mut m: i32 = xs[0]
    for i in 1 to 5 {
        if xs[i] > m {
            m = xs[i]
        }
    }
    printf("max=%d\n", m)
    return 0
}
```

## Part 2: Algorithms

### 2.1 Reverse in place

```flow
function main() -> i32 {
    let mut xs: [i32; 5] = [1, 2, 3, 4, 5]
    let mut i: i32 = 0
    let mut j: i32 = 4
    while i < j {
        let t: i32 = xs[i]
        xs[i] = xs[j]
        xs[j] = t
        i = i + 1
        j = j - 1
    }
    for k in 0 to 5 {
        printf("%d ", xs[k])
    }
    printf("\n")
    return 0
}
```
### 2.2 Linear search

```flow
function find(xs: ptr<i32>, n: i32, target: i32) -> i32 {
    for i in 0 to n {
        if xs[i] == target {
            return i
        }
    }
    return -1
}

function main() -> i32 {
    let xs: [i32; 5] = [4, 8, 15, 16, 23]
    printf("idx=%d\n", find(xs, 5, 15))
    return 0
}
```
### 2.3 Counting sort-ish histogram

```flow
function main() -> i32 {
    let xs: [i32; 8] = [1, 2, 1, 3, 2, 1, 0, 2]
    let mut hist: [i32; 4] = [0, 0, 0, 0]
    for i in 0 to 8 {
        hist[xs[i]] = hist[xs[i]] + 1
    }
    for v in 0 to 4 {
        printf("%d:%d ", v, hist[v])
    }
    printf("\n")
    return 0
}
```

## Part 3: 2D patterns

### 3.1 Flatten index

```flow
function at(row: i32, col: i32, width: i32) -> i32 {
    return row * width + col
}

function main() -> i32 {
    let mut grid: [i32; 9] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    grid[at(1, 2, 3)] = 5
    printf("%d\n", grid[5])
    return 0
}
```
### 3.2 Row sum

```flow
function main() -> i32 {
    let grid: [i32; 6] = [1, 2, 3, 4, 5, 6]
    let mut sum: i32 = 0
    for c in 0 to 3 {
        sum = sum + grid[0 * 3 + c]
    }
    printf("row0=%d\n", sum)
    return 0
}
```
