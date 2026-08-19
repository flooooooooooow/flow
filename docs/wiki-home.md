<div class="wiki-hero">

<h1 class="wiki-hero-brand">Flow</h1>
<p class="wiki-hero-eyebrow">v0.11.1 · systems through time</p>

<p class="wiki-hero-title">Write with effects.<br>Compile like C.</p>

<p class="wiki-hero-lead">
A statically typed language where evolution through time is the primary
abstraction: dynamics, algebraic effects, and built-in autodiff on dual
C / MLIR backends.
</p>

<div class="wiki-hero-actions">
  <a href="start-here.md" class="wiki-cta wiki-cta-primary">Start here</a>
  <a href="effects-showcase.md" class="wiki-cta">Effects &amp; capabilities</a>
  <a href="getting-started.md" class="wiki-cta">Install</a>
  <a href="demos/overview.md" class="wiki-cta">Galleries</a>
  <a href="tutorials/index.html" class="wiki-cta">Interactive tutorials</a>
</div>

<pre class="wiki-hero-code"><code class="language-flow">flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}</code></pre>

</div>

<div class="wiki-stat-row" aria-label="Documentation at a glance">
<span><strong>19</strong> book chapters</span>
<span><strong>257</strong> interactive lessons</span>
<span><strong>24</strong> effect patterns</span>
<span><strong>150+</strong> recorded demos</span>
<span><strong>9</strong> galleries</span>
<span><strong>C + MLIR</strong> backends</span>
</div>

## Documentation

Python-style entry points. Pick a section; the sidebar tabs mirror this map.

<nav class="wiki-doc-index" aria-label="Documentation sections">

<a class="wiki-doc" href="book/README.md">
<strong>The Flow Book</strong>
<span>Guided chapters from first program through effects, evolution, autodiff, and media.</span>
</a>

<a class="wiki-doc" href="tutorials/index.html">
<strong>Interactive tutorials</strong>
<span>Browser lessons with a live runner: beginner tracks through graphics, shaders, and RT audio.</span>
</a>

<a class="wiki-doc" href="getting-started.md">
<strong>Install &amp; quick start</strong>
<span>Clone, compile <code>hello_world</code>, open a native window, run the test suite.</span>
</a>

<a class="wiki-doc" href="start-here.md">
<strong>Start here (beginners)</strong>
<span>Zero-to-running path for people new to programming or new to Flow.</span>
</a>

<a class="wiki-doc" href="effects-showcase.md">
<strong>Effects &amp; capabilities cookbook</strong>
<span>24 concrete patterns: handler swaps, nested scopes, multi-effect capabilities, DI, testing, strict rows, state policy, retry, timeout, and async.</span>
</a>

<a class="wiki-doc" href="demos/overview.md">
<strong>Galleries</strong>
<span>Games, morphogenesis, neurons, planets, evolution, WASM. Real <code>gfx</code> recordings.</span>
</a>

<a class="wiki-doc" href="language/spec-index.md">
<strong>Language reference</strong>
<span>Spec index, syntax, types, modules, grammar, spans, WASM, graphics.</span>
</a>

<a class="wiki-doc" href="library/stdlib-reference.md">
<strong>Standard library</strong>
<span>Core APIs, autodiff, audio DSP, RT safety, and memory helpers.</span>
</a>

<a class="wiki-doc" href="DEVELOPMENT.md">
<strong>CLI &amp; tooling</strong>
<span>Commands, LSP, targets, and how to work on the compiler itself.</span>
</a>

<a class="wiki-doc" href="vision.md">
<strong>Vision</strong>
<span>Why evolution is the primary abstraction, and what that buys you at compile time.</span>
</a>

<a class="wiki-doc" href="comparison.md">
<strong>Comparison</strong>
<span>Flow vs C, Rust, Zig, Mojo, and the MATLAB / Simulink lane.</span>
</a>

<a class="wiki-doc" href="third-party/flow-verify.md">
<strong>Optional proofs</strong>
<span>flow-verify is third-party. Useful for formal claims; not required to write Flow.</span>
</a>

</nav>

---

## Effects & capabilities

If you are evaluating Flow's effect system, start with the cookbook rather than the language spec.
It uses the syntax the current compiler actually accepts and links directly to runnable programs.

| I want to see… | Jump straight to |
|---|---|
| the smallest complete effect | [The model in 30 seconds](effects-showcase.md#the-model-in-30-seconds) |
| swapping production and test implementations | [Swap implementations](effects-showcase.md#5-swap-implementations-without-changing-business-code) |
| nested dynamic scoping | [Nested handler override](effects-showcase.md#6-override-a-handler-in-a-nested-dynamic-scope) |
| one capability handling several effects | [Multi-effect capability](effects-showcase.md#7-handle-several-effects-with-one-capability) |
| handlers calling other effects | [Handler composition](effects-showcase.md#8-let-one-handler-perform-another-effect) |
| dependency injection without a framework | [Database DI](effects-showcase.md#16-use-effects-for-dependency-injection) |
| strict effect rows | [Effect rows](effects-showcase.md#10-declare-an-effect-row-on-a-function) |
| stateful loops with stateless capabilities | [Explicit state + policy](effects-showcase.md#19-keep-mutable-state-explicit-use-the-effect-as-policy) |
| timeout and retry | [Timeout](effects-showcase.md#20-model-timeout-policy-as-an-effect) · [Retry](effects-showcase.md#21-model-retry-policy-as-an-effect) |
| async through effects | [Async](effects-showcase.md#22-express-async-operations-through-an-effect-interface) |
| every runnable effect example | [Runnable example map](effects-showcase.md#runnable-example-map) |

<p class="wiki-section-foot">
<a href="effects-showcase.md">Open the effects &amp; capabilities cookbook →</a>
<span class="wiki-dot">·</span>
<a href="../examples/effects/showcase.flow">Open the runnable checkout showcase →</a>
</p>

---

## What Flow looks like

Three signatures of the language. Full write-ups live under Language and Library.

<div class="wiki-showcase">

<div class="wiki-showcase-item">
<p class="wiki-showcase-label">Algebraic effects</p>
<p class="wiki-showcase-desc">Call sites name typed effect interfaces. Enclosing handlers swap I/O, inventory, logging, time, configuration, and test policy for a dynamic scope.</p>

```text
effect Inventory {
    stock_of(sku: i32) -> i32,
    reserve(sku: i32, qty: i32) -> i32,
}

handle Inventory, Notify with TestBackend {
    let order_id: i32 = place_order(2002, 1)
}
```

<p class="wiki-showcase-more"><a href="effects-showcase.md">24-pattern effects cookbook →</a></p>
</div>

<div class="wiki-showcase-item">
<p class="wiki-showcase-label">Evolution</p>
<p class="wiki-showcase-desc"><code>flow</code> / <code>evolves</code> make continuous and hybrid dynamics syntax, with solvers attached.</p>

```flow
flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}
```

<p class="wiki-showcase-more"><a href="book/13-evolution-and-dynamics.md">Book · Evolution →</a></p>
</div>

<div class="wiki-showcase-item">
<p class="wiki-showcase-label">Built-in autodiff</p>
<p class="wiki-showcase-desc">Forward mode with dual numbers in the language, not a bolted-on library.</p>

```text
function quadratic(x: Dual, a: f32, b: f32, c: f32) -> Dual {
    return a * x * x + b * x + c
}

let x: Dual = dx(2.0)
let q: Dual = quadratic(x, 2.0, 3.0, 1.0)
# q.val = 15, q.grad = 11
```

<p class="wiki-showcase-more"><a href="library/autodiff-guide.md">Autodiff guide →</a></p>
</div>

</div>

---

## See it run

Frames below come from the native `gfx` backend: the same drawing calls a window receives.

<div class="wiki-demo-grid">

<figure class="wiki-demo">
<img src="demos/lorenz.gif" alt="Lorenz attractor traced in real time" loading="lazy">
<figcaption>

**[Lorenz](../examples/evolution/lorenz_gfx.flow)** — `flow` block, RK4, drawn each frame.

</figcaption>
</figure>

<figure class="wiki-demo">
<img src="demos/tetris.gif" alt="Tetris being played" loading="lazy">
<figcaption>

**[Tetris](../examples/games/tetris_gfx.flow)** — full game loop with ghost piece.

</figcaption>
</figure>

<figure class="wiki-demo">
<img src="demos/2048.gif" alt="2048 tiles merging" loading="lazy">
<figcaption>

**[2048](../examples/games/2048_gfx.flow)** — grid logic under scripted input.

</figcaption>
</figure>

</div>

### Galleries

| Gallery | What you get |
|---|---|
| [Games](demos/games.md) | Snake, Tetris, Asteroids, Flappy, and more (25 GIFs) |
| [Morphogenesis](demos/morphogenesis.md) | Reaction-diffusion, Turing patterns, Physarum (40) |
| [Neurons](demos/neuro.md) | Hodgkin-Huxley, Izhikevich, Hopfield, CPG (15) |
| [Evolutionary biology](demos/evoleco.md) | Wright-Fisher, SIR, Red Queen (25) |
| [Evolution suite](demos/evolution.md) | Systems through time, checked against theory (34) |
| [Planets](demos/planet.md) · [Procgen](demos/procgen.md) · [Numerical](demos/numerical.md) · [WASM](demos/wasm.md) | Cubesphere, WFC, FMM, live browser demos |

<p class="wiki-section-foot">
<a href="demos/overview.md">All galleries →</a>
<span class="wiki-dot">·</span>
<a href="wasm/index.html">Live WASM demos →</a>
</p>

---

## Install in five minutes

```bash
git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow run examples/basics/hello_world.flow
./flow gfx examples/evolution/lorenz_gfx.flow   # native window
./flow test --strict --tier2                    # type-check + corpus
```

More detail: [Quick start](getting-started.md) · [CLI reference](DEVELOPMENT.md) · [Start here](start-here.md)

Everyday commands:

```bash
./flow run program.flow        # C backend (default)
./flow mlir-run program.flow   # MLIR pipeline
./flow lsp                     # editor support
```

---

## Project

| | |
|---|---|
| Version | 0.11.1 · [changelog](project/CHANGELOG.md) |
| License | MIT |
| Source | [github.com/flooooooooooow/flow](https://github.com/flooooooooooow/flow) |
| Community | [Discord](https://discord.gg/YK7VaHy24T) · [Discussions](https://github.com/flooooooooooow/flow/discussions) |
| Optional proofs | [flow-verify](third-party/flow-verify.md) (third-party, not required to use Flow) |
