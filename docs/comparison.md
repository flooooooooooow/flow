# Compare Flow

Flow is easiest to understand beside languages you already know. These pages compare **complete implementations and programming models**, not isolated punctuation.

The question is not “can Flow write this expression with fewer characters?” It is: **how much code and machinery does the programmer have to maintain before the source says what the system actually does?**

## Pick a language

<table>
<tr>
<td align="center" width="25%"><a href="comparisons/c.md"><img src="https://cdn.simpleicons.org/c/A8B9CC" alt="C" width="56"><br><strong>Flow vs C</strong></a><br><small>ABI-level control vs semantic structure</small></td>
<td align="center" width="25%"><a href="comparisons/cpp.md"><img src="https://cdn.simpleicons.org/cplusplus/00599C" alt="C++" width="56"><br><strong>Flow vs C++</strong></a><br><small>Framework machinery vs language-level intent</small></td>
<td align="center" width="25%"><a href="comparisons/rust.md"><img src="https://cdn.simpleicons.org/rust/000000" alt="Rust" width="56"><br><strong>Flow vs Rust</strong></a><br><small>Ownership-first vs semantics-first systems code</small></td>
<td align="center" width="25%"><a href="comparisons/zig.md"><img src="https://cdn.simpleicons.org/zig/F7A41D" alt="Zig" width="56"><br><strong>Flow vs Zig</strong></a><br><small>Minimal explicitness vs richer compiler-visible meaning</small></td>
</tr>
<tr>
<td align="center"><a href="comparisons/go.md"><img src="https://cdn.simpleicons.org/go/00ADD8" alt="Go" width="56"><br><strong>Flow vs Go</strong></a><br><small>Runtime concurrency vs effects + no GC</small></td>
<td align="center"><a href="comparisons/python.md"><img src="https://cdn.simpleicons.org/python/3776AB" alt="Python" width="56"><br><strong>Flow vs Python</strong></a><br><small>Readable scripting vs readable native implementation</small></td>
<td align="center"><a href="comparisons/mojo.md"><span style="font-size:56px">🔥</span><br><strong>Flow vs Mojo</strong></a><br><small>AI/kernel metaprogramming vs broader domain semantics</small></td>
<td align="center"><a href="comparisons/julia.md"><img src="https://cdn.simpleicons.org/julia/9558B2" alt="Julia" width="56"><br><strong>Flow vs Julia</strong></a><br><small>Scientific dynamism vs deployable native domain code</small></td>
</tr>
</table>

<img src="assets/flow-logo-alone.png" alt="Flow logo" width="72">

## How these comparisons are written

Every comparison follows the same rules:

1. Compare the **same semantics**, not vaguely similar snippets.
2. Prefer complete, runnable implementations over syntax fragments.
3. Do not hide required helpers or framework machinery outside the shown code.
4. Do not claim Flow is shorter where the other language is genuinely just as direct.
5. Distinguish language expressiveness from library/ecosystem breadth.
6. State where the competing language is currently the better choice.
7. Keep performance claims separate from readability claims and link measurements when they exist.

The strongest Flow examples are usually not tiny arithmetic functions. They are places where another language must reconstruct a domain concept from structs, methods, callbacks, traits, framework objects or conventions while Flow can preserve that concept directly in the source.

## A representative example

The same decay model can be encoded as ordinary state plus a stepping convention in almost any language. In Flow, the model itself is syntax:

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

This is the sort of expressiveness the comparison pages are meant to expose. `state`, `param` and `evolves as` are not comments or naming conventions. They are program structure available to the compiler.

## At a glance

| Dimension | Flow | C | Rust | Zig | Go | Python | Mojo | Julia |
|-----------|------|---|------|-----|----|--------|------|-------|
| Runtime model | Native, no GC | Native, no GC | Native, no GC | Native, no GC | GC runtime | Managed interpreter/runtime | Native systems/accelerator | JIT/runtime |
| Low-level control | Explicit + C interop | Maximum | Strong, safety-mediated | Strong, explicit allocators | Limited relative to systems languages | Via extensions/FFI | Strong | Available, not the center |
| Effects / capabilities | First-class Flow surface | Conventions | Types/traits/`Result` + libraries | Explicit errors + conventions | Context/channels/interfaces | Exceptions/context managers/frameworks | Typed systems features | Exceptions/tasks/libraries |
| Domain evolution | `flow` declarations | Hand-written model API | Hand-written model API | Hand-written model API | Hand-written model API | Class/library model | Struct/library model | Struct/library/ecosystem model |
| Audio / DSP direction | First-class project focus | Libraries | Crates | Libraries/C interop | Not a core focus | Native libraries behind Python APIs | Not a core focus | Packages |
| Portable C path | Yes | Already C | C ABI interoperability | Excellent C interop | cgo | Extensions/FFI | Interop-oriented | `ccall`/FFI |
| Best argument for it | Semantic density + native deployment | Universal ABI and maturity | Memory safety at scale | Explicit small systems language | Operational simplicity | Ecosystem and iteration speed | AI/GPU metaprogramming | Scientific computing |

## Where Flow is deliberately different

### Domain semantics stay in the language

Flow is willing to make recurring high-value concepts compiler-visible: evolution/dynamics, effects and capabilities, DSP/audio surfaces, target information and other domain constructs. In C/C++/Rust/Zig/Go those are normally library or framework designs. In Python/Julia they are often library objects backed by a separate native implementation layer.

### The readable layer can also be the native layer

Python is often the shortest call-site language because the hard implementation lives somewhere else. Flow's goal is for the readable source to remain the implementation that is compiled and deployed rather than becoming a wrapper around another language.

### Expressiveness is not permission to hide costs

Flow still exposes explicit types, mutation, pointers, loops, extern declarations and low-level escape hatches. The goal is to remove incidental machinery without hiding the parts that determine runtime behavior.

## Existing focused comparisons

The Go concurrency story already has deeper material: [Concurrency vs Go](language/concurrency-vs-go.md) and [Replacing Go](language/replace-go.md). For control engineering, see [Dynamics DSL](language/dynamics-dsl.md) and the project [Vision](../VISION.md).

## Performance

Measured Flow-vs-C results belong in the benchmark corpus rather than being inferred from syntax. The published benchmark page contains methodology and current results: [Benchmark results](project/benchmark-results.md).

The important rule for this section is simple: **shorter source does not imply faster source, and faster source does not imply better source.** Flow should demonstrate both independently.

## What should be added next

These pages are the foundation, not the finish line. The comparison corpus should grow toward larger equivalent programs: parsers, concurrent services, DSP graphs, GPU kernels, simulations, embedded state machines, error-heavy systems code and complete small applications. Those are the examples where language design differences become much harder to fake with clever formatting.

## See also

[Quick Start](getting-started.md) · [Flow syntax](language/syntax.md) · [Effects showcase](effects-showcase.md) · [Language overview](language/overview.md) · [Demo showcase](demos/overview.md)
