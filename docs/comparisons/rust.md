# Flow vs Rust

<img src="https://cdn.simpleicons.org/rust/000000" alt="Rust logo" width="64" height="64">

Rust and Flow both target native, no-GC software, but they spend complexity differently. Rust makes ownership and borrowing central to general-purpose safety. Flow is trying to make effects, domain behavior and target intent central while retaining explicit low-level control.

[← All language comparisons](../comparison.md)

## A fair comparison

Rust often wins when the hard problem is proving memory ownership across a large codebase. Flow's expressiveness case is strongest when the hard problem is describing what a high-performance system does.

## Example: evolution as syntax

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

### Rust

```rust
struct Decay {
    value: f64,
    rate: f64,
}

impl Decay {
    fn step(&mut self, dt: f64) {
        let derivative = -self.rate * self.value;
        self.value += derivative * dt;
    }
}

fn main() {
    let mut system = Decay { value: 1.0, rate: 0.5 };
    for _ in 0..100 {
        system.step(0.01);
    }
    println!("{}", system.value);
}
```

Rust expresses the implementation cleanly. Flow expresses the model directly: `state`, `param` and `evolves as` are semantic information rather than conventions encoded in a struct and method.

## Ordinary typed code

```flow
struct Point {
    x: f32,
    y: f32
}

function squared_length(p: Point) -> f32 {
    return p.x * p.x + p.y * p.y
}
```

Rust is similarly compact here. Flow's goal is not to beat Rust on every five-line function; it is to avoid forcing every higher-level semantic distinction through traits, wrapper types and library APIs.

## Effects versus plumbing

Rust's `Result`, traits, lifetimes and async ecosystem are mature ways to make important behavior explicit. Flow's effects/capabilities system attacks a different layer: side effects can be part of a function's semantic contract and handled separately from the computation that requests them. See the [effects showcase](../effects-showcase.md) for the current executable surface.

That can make alternate implementations, simulation and testing read as changes in handlers/capabilities instead of changes threaded through every call site.

## Where Rust still wins

Rust is the stronger choice today for production memory safety, crates.io breadth, mature async/networking, tooling, operating-system components and teams that want the borrow checker to reject broad classes of lifetime mistakes.

Flow needs to earn its place by making systems with rich domain semantics materially smaller and clearer, not by claiming Rust's safety model is unnecessary.

## See also

[Lifetime domains](../language/lifetime-domains.md) · [Effects showcase](../effects-showcase.md) · [Safety profiles](../language/safety-profiles.md)
