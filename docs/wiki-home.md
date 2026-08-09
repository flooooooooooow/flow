<div class="wiki-hero">

<h1 class="wiki-hero-brand">Flow</h1>
<p class="wiki-hero-eyebrow">v0.9 · systems through time</p>

<p class="wiki-hero-title">Write with effects.<br>Compile like C.</p>

<p class="wiki-hero-lead">
A statically typed language for systems that evolve through time: dynamics,
algebraic effects, and autodiff, compiling to C or MLIR.
</p>

<div class="wiki-hero-actions">
  <a href="getting-started.md" class="wiki-cta wiki-cta-primary">Install &amp; run</a>
  <a href="tutorials/index.html" class="wiki-cta">257 interactive lessons</a>
</div>

<pre class="wiki-hero-code"><code class="language-flow">flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}</code></pre>

</div>

## Three ways in

Pick a path. The rest is in the sidebar tabs.

<nav class="wiki-paths" aria-label="Ways into the docs">

<a class="wiki-path" href="getting-started.md">
<span class="wiki-path-kicker">01 · Start</span>
<strong>Install in five minutes</strong>
<span>Compile `hello_world`, then open the tutorial app in the browser.</span>
</a>

<a class="wiki-path" href="demos/overview.md">
<span class="wiki-path-kicker">02 · Watch</span>
<strong>See compiled programs run</strong>
<span>Games, morphogenesis, neurons, planets: real `gfx` recordings, not mocks.</span>
</a>

<a class="wiki-path" href="language/spec-index.md">
<span class="wiki-path-kicker">03 · Reference</span>
<strong>Language and library</strong>
<span>Spec, grammar, stdlib, effects, autodiff, memory, and RT safety.</span>
</a>

</nav>

---

## See it run

Frames come from the native `gfx` backend.

<div class="wiki-demo-grid">

<figure class="wiki-demo">
<img src="demos/lorenz.gif" alt="Lorenz attractor traced in real time" loading="lazy">
<figcaption>

**[Lorenz](../examples/evolution/lorenz_gfx.flow)**: `flow` block, RK4, drawn each frame.

</figcaption>
</figure>

<figure class="wiki-demo">
<img src="demos/tetris.gif" alt="Tetris being played" loading="lazy">
<figcaption>

**[Tetris](../examples/games/tetris_gfx.flow)**: full game loop with ghost piece.

</figcaption>
</figure>

<figure class="wiki-demo">
<img src="demos/2048.gif" alt="2048 tiles merging" loading="lazy">
<figcaption>

**[2048](../examples/games/2048_gfx.flow)**: grid logic under scripted input.

</figcaption>
</figure>

</div>

<p class="wiki-section-foot">
<a href="demos/overview.md">All galleries →</a>
<span class="wiki-dot">·</span>
games, morphogenesis, neurons, evolution, planets, procgen, numerical, WASM
</p>

---

## Features that matter here

| | |
|---|---|
| Algebraic effects | Swap I/O and state at the handler; call sites stay the same. |
| Built-in autodiff | Forward and reverse mode in the language, not a bolt-on library. |
| `flow` / `evolves` | Continuous and hybrid dynamics as syntax, with solvers and analysis. |
| Dual backends | Portable C by default; MLIR when you want JIT. |

Thesis: [Vision](vision.md) · how to write it: [Best practices](language/best-practices.md) · vs others: [Comparison](comparison.md)

---

## Everyday commands

```bash
./flow run program.flow        # C backend (default)
./flow gfx examples/...        # native window
./flow test --strict --tier2   # type-check + corpus
./flow mlir-run program.flow   # MLIR pipeline
./flow lsp                     # editor support
```

[CLI and development →](DEVELOPMENT.md)

---

## Project

| | |
|---|---|
| Version | 0.10.0 · [changelog](project/CHANGELOG.md) |
| License | MIT |
| Source | [github.com/flooooooooooow/flow](https://github.com/flooooooooooow/flow) |
| Community | [Discord](https://discord.gg/YK7VaHy24T) · [Discussions](https://github.com/flooooooooooow/flow/discussions) |
| Optional proofs | [flow-verify](third-party/flow-verify.md) (third-party; not required to use Flow) |
