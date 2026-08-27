# Flow vs Go

<img src="https://cdn.simpleicons.org/go/00ADD8" alt="Go logo" width="64" height="64">

Go optimizes for a small language, fast builds and straightforward concurrency. Flow targets a lower-level/no-GC runtime and tries to make effects and domain semantics explicit without requiring a separate framework vocabulary.

[← All language comparisons](../comparison.md)

## Example: model semantics

### Flow

```flow
flow Decay {
    state value : f64 = 1.0
    param rate  : f64 = 0.5

    value evolves as -rate * value
}

function main() -> i32 {
    let mut system: Decay = Decay_new()

    for i in 0 to 100 {
        Decay_step(&system, 0.01)
    }

    println(system.value)
    return 0
}
```

### Go

```go
package main

import "fmt"

type Decay struct {
    Value float64
    Rate  float64
}

func (d *Decay) Step(dt float64) {
    derivative := -d.Rate * d.Value
    d.Value += derivative * dt
}

func main() {
    system := Decay{Value: 1.0, Rate: 0.5}

    for i := 0; i < 100; i++ {
        system.Step(0.01)
    }

    fmt.Println(system.Value)
}
```

Go is concise, but the model is still encoded as ordinary fields and methods. Flow elevates the distinction between state, parameter and evolution law into source-level semantics.

## Concurrency is the more interesting comparison

Go's goroutines, channels and runtime scheduler are one of the best productivity stories in systems-adjacent programming. Flow does not claim that a shorter syntax alone beats that ecosystem.

Flow's wedge is different: effects can separate *what* asynchronous or concurrent behavior is requested from *how* it is implemented, while Flow can also run without a garbage-collected runtime. The repository already has dedicated pages for the details and current limits.

[Concurrency vs Go](../language/concurrency-vs-go.md) · [Replacing Go](../language/replace-go.md)

## Where Go still wins

Choose Go for mature network services, operational tooling, a huge standard ecosystem and teams that benefit from the runtime's deliberately opinionated concurrency model.

Choose Flow when predictable native execution, no GC, richer domain semantics or effect-based substitution are central enough to justify a younger language.

## See also

[Async via effects](../language/async-effects.md) · [Concurrency tutorial](../tutorials/concurrency.md) · [Effects showcase](../effects-showcase.md)
