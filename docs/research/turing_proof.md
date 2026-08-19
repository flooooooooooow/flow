# Flow is Turing complete

Flow is Turing complete in the ordinary programming-language sense: under the usual abstract-machine assumption of unbounded available memory, it can express mutable storage, conditional branching, unbounded iteration, and general recursion. Those facilities are sufficient to simulate a Turing machine or another known universal model.

This page uses only current Flow syntax. Every block labelled `flow` is compiler-checked in CI.

## Mutable state

```flow
function mutate_state() -> i32 {
    let mut cell: i32 = 0
    cell = 42
    return cell
}
```

## Conditional branching

```flow
function choose(symbol: i32) -> i32 {
    if symbol == 0 {
        return 1
    } else {
        return 0
    }
}
```

## Unbounded iteration

A `while` loop has no language-imposed iteration bound:

```flow
function count_until(limit: i32) -> i32 {
    let mut value: i32 = 0
    while value < limit {
        value = value + 1
    }
    return value
}
```

Whether a particular execution terminates is a property of the program and input, not of the syntax.

## Random-access memory

Flow exposes explicit pointers and heap allocation. A complete checked example uses the memory standard library:

```flow
import "stdlib/memory.flow"

function random_access() -> i32 {
    let memory: ptr<i32> = alloc_i32(4096)
    if memory == null {
        return 1
    }

    memory[1234] = 42
    let result: i32 = memory[1234]
    free(memory)
    return result - 42
}
```

Physical machines have finite memory, as they do for C, Rust, Python, and every practical implementation. Turing-completeness statements abstract over that implementation limit.

## A state-machine step

```flow
function machine_step(state: i32, symbol: i32) -> i32 {
    if state == 0 {
        if symbol == 0 {
            return 1
        }
        return 0
    }
    return state
}
```

A universal simulator combines a mutable tape, an integer head position, an integer state, and a loop that repeatedly applies a transition function. Flow has each of those ingredients.

## General recursion

```flow
function ackermann(m: i32, n: i32) -> i32 {
    if m == 0 {
        return n + 1
    }
    if n == 0 {
        return ackermann(m - 1, 1)
    }
    return ackermann(m - 1, ackermann(m, n - 1))
}
```

Ackermann growth is not itself a proof of Turing completeness, but it demonstrates that Flow is not restricted to primitive recursion.

## Reduction argument

To simulate a single-tape Turing machine, represent each tape cell in mutable random-access storage, the head as an integer index, and the machine state as an integer or enum. Encode the finite transition table as conditionals or table data. A `while` loop repeatedly reads the current cell, computes the transition, writes the new symbol, moves the head, and updates the state until a halting state is reached.

Because an arbitrary Turing-machine transition table can be encoded this way, Flow can simulate any Turing machine given sufficient memory. Equivalently, a Brainfuck or register-machine interpreter can be written using the same facilities.

## What this does not imply

Turing completeness does not make the halting problem decidable, prove termination, imply memory safety for arbitrary pointer code, or guarantee that every backend supports every optional Flow feature. It is a statement about computational expressiveness of the language core.

## Practical source examples

[`examples/systems/manual_memory.flow`](../../examples/systems/manual_memory.flow) demonstrates explicit heap memory. The ordinary control-flow and recursive examples throughout the [book](../book/README.md) demonstrate the other ingredients without relying on historical pointer syntax such as `[*T]` or invented allocation functions.
