# Flow vs Zig

<img src="https://cdn.simpleicons.org/zig/F7A41D" alt="Zig logo" width="64" height="64">

Zig and Flow share a preference for explicit native code, simple deployment and good C interoperability. Zig keeps the language deliberately small and makes allocators, errors and compile-time execution explicit. Flow is willing to add higher-level semantic constructs when they can remove repeated framework code.

[← All language comparisons](../comparison.md)

## Example: explicit implementation versus explicit model

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

### Zig

```zig
const std = @import("std");

const Decay = struct {
    value: f64 = 1.0,
    rate: f64 = 0.5,

    fn step(self: *Decay, dt: f64) void {
        const derivative = -self.rate * self.value;
        self.value += derivative * dt;
    }
};

pub fn main() !void {
    var system = Decay{};

    for (0..100) |_| {
        system.step(0.01);
    }

    std.debug.print("{d}\n", .{system.value});
}
```

The Zig source is already compact. The distinction is semantic density: Flow knows that one field is state, one is a parameter, and the expression is an evolution law. In Zig those meanings are intentionally left to ordinary code.

## Why that matters

A Zig project tends to build higher-level behavior in libraries while keeping the language itself small. Flow instead wants recurring concepts such as effects, dynamics, audio processing and target-specific lowering to remain visible to the compiler.

That creates room for specialized verification, code generation and tooling without requiring every project to invent its own conventions.

## Where Zig still wins

Zig is excellent when explicit allocators, freestanding targets, cross-compilation, C integration and a small predictable language are the main requirements. Its toolchain and low-level standard library are substantially more mature.

Flow is the stronger proposition when domain semantics are important enough that representing them as plain functions and structs becomes repetitive infrastructure.

## See also

[Memory](../tutorials/memory.md) · [C interop](../language/export-abi.md) · [Dynamics DSL](../language/dynamics-dsl.md)
