# Strings & Formatting

> printf, strings, and simple parsing patterns.


## Part 1: Printing

### 1.1 printf basics

```flow
function main() -> i32 {
    printf("hello %s\n", "flow")
    printf("i=%d f=%f\n", 42, 3.14)
    return 0
}
```
### 1.2 Table row

```flow
function main() -> i32 {
    printf("%-8s %4d\n", "alice", 12)
    printf("%-8s %4d\n", "bob", 7)
    return 0
}
```

## Part 2: Char logic

### 2.1 Digit check

```flow
function is_digit(c: i32) -> bool {
    return c >= 48 && c <= 57
}

function main() -> i32 {
    printf("%d %d\n", is_digit(50), is_digit(65))
    return 0
}
```
### 2.2 Parse int from digits

```flow
function parse3(a: i32, b: i32, c: i32) -> i32 {
    return (a - 48) * 100 + (b - 48) * 10 + (c - 48)
}

function main() -> i32 {
    printf("%d\n", parse3(49, 50, 51))
    return 0
}
```

## Part 3: Building messages

### 3.1 Status line

```flow
function main() -> i32 {
    let hp: i32 = 80
    let mp: i32 = 30
    printf("[HP %d | MP %d]\n", hp, mp)
    return 0
}
```
### 3.2 Escape practice

```flow
function main() -> i32 {
    printf("line1\nline2\n")
    printf("tab\tseparated\n")
    printf("100%%%% complete\n")
    return 0
}
```
