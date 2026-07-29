# Algorithms

> Classic algorithms you can run in the browser.


## Part 1: Searching

### 1.1 Binary search

```flow
function bsearch(xs: ptr<i32>, n: i32, target: i32) -> i32 {
    let mut lo: i32 = 0
    let mut hi: i32 = n - 1
    while lo <= hi {
        let mid: i32 = (lo + hi) / 2
        if xs[mid] == target {
            return mid
        } elif xs[mid] < target {
            lo = mid + 1
        } else {
            hi = mid - 1
        }
    }
    return -1
}

function main() -> i32 {
    let xs: [i32; 7] = [1, 3, 4, 7, 9, 12, 15]
    printf("%d\n", bsearch(xs, 7, 9))
    return 0
}
```
### 1.2 Two-sum indices

```flow
function main() -> i32 {
    let xs: [i32; 5] = [2, 7, 11, 15, 3]
    let target: i32 = 18
    for i in 0 to 5 {
        for j in i + 1 to 5 {
            if xs[i] + xs[j] == target {
                printf("%d+%d\n", i, j)
                return 0
            }
        }
    }
    printf("none\n")
    return 0
}
```

## Part 2: Sorting

### 2.1 Bubble sort

```flow
function main() -> i32 {
    let mut xs: [i32; 6] = [5, 1, 4, 2, 8, 0]
    for i in 0 to 6 {
        for j in 0 to 5 - i {
            if xs[j] > xs[j + 1] {
                let t: i32 = xs[j]
                xs[j] = xs[j + 1]
                xs[j + 1] = t
            }
        }
    }
    for k in 0 to 6 {
        printf("%d ", xs[k])
    }
    printf("\n")
    return 0
}
```
### 2.2 Selection sort

```flow
function main() -> i32 {
    let mut xs: [i32; 5] = [64, 25, 12, 22, 11]
    for i in 0 to 5 {
        let mut best: i32 = i
        for j in i + 1 to 5 {
            if xs[j] < xs[best] {
                best = j
            }
        }
        let t: i32 = xs[i]
        xs[i] = xs[best]
        xs[best] = t
    }
    for k in 0 to 5 {
        printf("%d ", xs[k])
    }
    printf("\n")
    return 0
}
```

## Part 3: Numerics

### 3.1 GCD

```flow
function gcd(a: i32, b: i32) -> i32 {
    let mut x: i32 = a
    let mut y: i32 = b
    while y != 0 {
        let t: i32 = y
        y = x % y
        x = t
    }
    return x
}

function main() -> i32 {
    printf("%d\n", gcd(48, 18))
    return 0
}
```
### 3.2 Prime sieve mark

```flow
function main() -> i32 {
    let mut mark: [i32; 21] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    mark[0] = 1
    mark[1] = 1
    for p in 2 to 21 {
        if mark[p] == 0 {
            let mut k: i32 = p * p
            while k < 21 {
                mark[k] = 1
                k = k + p
            }
        }
    }
    for n in 2 to 21 {
        if mark[n] == 0 {
            printf("%d ", n)
        }
    }
    printf("\n")
    return 0
}
```
### 3.3 Prefix sums

```flow
function main() -> i32 {
    let xs: [i32; 5] = [1, 2, 3, 4, 5]
    let mut pref: [i32; 5] = [0, 0, 0, 0, 0]
    pref[0] = xs[0]
    for i in 1 to 5 {
        pref[i] = pref[i - 1] + xs[i]
    }
    for i in 0 to 5 {
        printf("%d ", pref[i])
    }
    printf("\n")
    return 0
}
```
