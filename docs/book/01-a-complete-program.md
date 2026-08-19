# 1. A complete program

A Flow source file is plain text, conventionally stored with the `.flow`
extension. The smallest useful program defines `main`:

```flow from=examples/book/01_hello.flow
function main() -> i32 {
    println("Hello, Flow.")
    return 0
}
```

The complete source is
[`examples/book/01_hello.flow`](../../examples/book/01_hello.flow).

Run it from the repository root:

```bash
./flow run examples/book/01_hello.flow
```

Program output:

```text
Hello, Flow.
```

## 1.1 The entry point

The signature

```flow
function main() -> i32
```

has three parts:

| Form | Meaning |
|---|---|
| `function` | begin a function declaration |
| `main()` | define the program entry point with no parameters |
| `-> i32` | return a signed 32-bit integer |

The braces contain the function body. Statements execute from top to bottom
unless a control construct changes that order.

`return 0` reports success to the process that launched the program. A nonzero
value reports failure. Shell scripts and test runners use this value even when
the program prints no text.

## 1.2 Output is not the result

Printing and returning have different jobs:

```flow
println("calibration complete")  # visible text for a person
return 0                         # status for the calling process
```

A diagnostic program can print a useful result and still return failure:

```flow
function main() -> i32 {
    println("sensor not found")
    return 2
}
```

After execution, a POSIX shell exposes the status as `$?`:

```bash
./flow run program.flow
echo $?
```

## 1.3 Source to process

The default native build has these stages:

```text
source.flow  ->  Flow compiler  ->  generated C  ->  C compiler  ->  executable
```

`flow run` performs the stages and launches the executable. `flow compile`
stops after producing the native program:

```bash
./flow compile examples/book/01_hello.flow
```

The result is an ordinary native executable. C libraries and standard system
tools can work with it directly.

## 1.4 Comments and layout

A comment begins with `#` and continues to the end of the line:

```flow
# Temperature is measured in degrees Celsius.
let temperature: f64 = 21.5  # initial reading
```

Newlines separate statements. Semicolons are not required. Indentation is not
part of the grammar, but four spaces per nesting level makes block structure
visible.

```flow
function main() -> i32 {
    if true {
        println("inside the block")
    }
    return 0
}
```

## 1.5 A program as a check

Many examples in this book verify their own result:

```flow
function main() -> i32 {
    let answer: i32 = 6 * 7
    if answer != 42 {
        return 1
    }
    return 0
}
```

Printed output describes the run. The exit status says whether the check
passed, which makes the program suitable for a test script.

## 1.6 Demonstration

Change the greeting, then run the file again:

```flow
function main() -> i32 {
    println("measurement started")
    println("measurement finished")
    return 0
}
```

Expected output:

```text
measurement started
measurement finished
```

The two calls execute in source order. The process terminates when `main`
returns.

## Exercises

1. Write a program that prints three lines and returns success.
2. Change its return value to `7`; inspect the shell status after execution.
3. Remove a closing brace and read the compiler diagnostic. Restore the brace
   before continuing.

Next: [Values and types](02-values-and-types.md).
