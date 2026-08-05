# Mini Projects

> Small complete programs to stitch skills together.


## Part 1: Games

### 1.1 Guess scoring

```flow
function score_guess(secret: i32, guess: i32) -> i32 {
    let mut d: i32 = guess - secret
    if d < 0 {
        d = -d
    }
    return 100 - d * 10
}

function main() -> i32 {
    printf("%d\n", score_guess(50, 45))
    printf("%d\n", score_guess(50, 50))
    return 0
}
```
### 1.2 Tic-tac cell

```flow
function winner(b: ptr<i32>) -> i32 {
    if b[0] != 0 && b[0] == b[1] && b[1] == b[2] {
        return b[0]
    }
    return 0
}

function main() -> i32 {
    let board: [i32; 9] = [1, 1, 1, 0, 2, 0, 0, 0, 2]
    printf("winner=%d\n", winner(board))
    return 0
}
```

## Part 2: Tools

### 2.1 Running average

```flow
function main() -> i32 {
    let xs: [i32; 5] = [2, 4, 6, 8, 10]
    let mut sum: i32 = 0
    for i in 0 to 5 {
        sum = sum + xs[i]
        printf("avg@%d=%d\n", i, sum / (i + 1))
    }
    return 0
}
```
### 2.2 Mini CSV sum column

```flow
function main() -> i32 {
    let col: [i32; 4] = [10, 20, 30, 40]
    let mut s: i32 = 0
    for i in 0 to 4 {
        s = s + col[i]
    }
    printf("sum=%d\n", s)
    return 0
}
```

## Part 3: Simulations

### 3.1 Bouncing value

```flow
function main() -> i32 {
    let mut x: i32 = 0
    let mut v: i32 = 3
    for t in 0 to 10 {
        x = x + v
        if x > 10 || x < 0 {
            v = -v
            x = x + v
        }
        printf("%d ", x)
    }
    printf("\n")
    return 0
}
```
### 3.2 Population step

```flow
function main() -> i32 {
    let mut pop: i32 = 100
    for year in 0 to 5 {
        pop = pop + pop / 10
        printf("y%d=%d\n", year, pop)
    }
    return 0
}
```
### 3.3 Dice histogram

```flow
function main() -> i32 {
    let rolls: [i32; 10] = [1, 2, 6, 6, 3, 4, 6, 2, 1, 5]
    let mut hist: [i32; 7] = [0, 0, 0, 0, 0, 0, 0]
    for i in 0 to 10 {
        hist[rolls[i]] = hist[rolls[i]] + 1
    }
    for face in 1 to 7 {
        printf("%d:%d ", face, hist[face])
    }
    printf("\n")
    return 0
}
```
