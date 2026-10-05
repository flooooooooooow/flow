# Flow on Rosetta Code

This page is the submission pack for adding Flow to Rosetta Code.

Rosetta Code's language-addition guidance asks for a language category, a redirect, and at least one or two task examples. Flow already has a mature public implementation and a large verified example corpus, so the goal here is to make the wiki edits mechanical.

## Language category

Create `Category:Flow` with:

```text
{{stub}}{{language|Flow}}
```

Then expand the category description with:

> Flow is a statically typed, compiled systems language for systems that evolve through time. Its stable core is self-hosted and targets portable C. The project also includes experimental surfaces for dynamical systems, algebraic effects, automatic differentiation, graphics, MLIR and other domain-specific compilation paths.

Official implementation: https://github.com/flooooooooooow/flow

Documentation: https://flooooooooooow.github.io/flow/

## Redirect

Create the main-namespace page `Flow` with:

```text
REDIRECT [[:Category:Flow]]
```

## Starter tasks

These examples use syntax already exercised by the Flow documentation and example suite.

### User Output

```flow
function main() -> i32 {
    println("Hello, Flow!")
    return 0
}
```

Run with:

```bash
flow run hello.flow
```

### Conditional Structures

```flow
function check_number(n: i32) -> void {
    if n > 0 {
        printf("%d is positive\n", n)
    } elif n < 0 {
        printf("%d is negative\n", n)
    } else {
        printf("zero\n")
    }
}

function main() -> i32 {
    check_number(5)
    check_number(-3)
    check_number(0)
    return 0
}
```

### Loop Structures

```flow
function main() -> i32 {
    let mut i: i32 = 1

    while i <= 5 {
        printf("%d\n", i)
        i = i + 1
    }

    for j in 0..5 {
        printf("%d\n", j)
    }

    return 0
}
```

### Factorial

```flow
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }

    return n * factorial(n - 1)
}

function main() -> i32 {
    printf("%d\n", factorial(5))
    return 0
}
```

### Fibonacci sequence

```flow
function fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n
    }

    return fibonacci(n - 1) + fibonacci(n - 2)
}

function main() -> i32 {
    for i in 0..10 {
        printf("%d\n", fibonacci(i))
    }

    return 0
}
```

### Greatest common divisor

```flow
function gcd(a: i32, b: i32) -> i32 {
    let mut x: i32 = a
    let mut y: i32 = b

    while y != 0 {
        let next: i32 = x % y
        x = y
        y = next
    }

    return x
}

function main() -> i32 {
    printf("%d\n", gcd(56, 98))
    return 0
}
```

### FizzBuzz

```flow
function main() -> i32 {
    for i in 1..101 {
        if i % 15 == 0 {
            println("FizzBuzz")
        } elif i % 3 == 0 {
            println("Fizz")
        } elif i % 5 == 0 {
            println("Buzz")
        } else {
            printf("%d\n", i)
        }
    }

    return 0
}
```

## Validation

Before copying a snippet to Rosetta Code, save it as a temporary `.flow` file and run:

```bash
./flow run /tmp/rosetta.flow
```

The corresponding repository examples and tutorial material should remain the source of truth for syntax.

## Suggested next tasks

After the starter set, add tasks that show Flow rather than merely proving basic syntax: Euler method, Runge-Kutta method, numerical integration, producer-consumer, matrix multiplication, FFT/DFT, cellular automata, state-machine tasks, and other dynamical or systems-oriented examples.

## Unimplemented-task page

Once the Flow category exists, create its unimplemented-task page using Rosetta Code's standard template:

```text
{{unimpl_Page|Flow}}
```
