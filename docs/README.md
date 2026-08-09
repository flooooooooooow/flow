# Flow Documentation

<p align="center">
  <img src="assets/flow-logo-with-text.png" alt="Flow" width="280">
</p>

<p align="center">
  <strong>Write with effects. Compile like C.</strong>
</p>

<p align="center">
  A statically typed language for systems that evolve through time:
  dynamics, algebraic effects, and autodiff, compiling to C or MLIR.
</p>

<p align="center">
  <a href="getting-started.md">Install &amp; run</a>
  ·
  <a href="demos/overview.md">Galleries</a>
  ·
  <a href="tutorials/beginner.md">Tutorials</a>
  ·
  <a href="LANGUAGE_SPEC.md">Spec</a>
  ·
  <a href="https://github.com/flooooooooooow/flow">Source</a>
</p>

```flow
flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}
```

You write how a system evolves. That description is what runs. The compiler emits C by default, MLIR when you ask for it, and the stdlib ships autodiff, dynamics solvers, audio DSP, and a native `gfx` backend in the same tree.

---

## Why Flow

Most languages are built around computation: sequences of instructions that transform inputs to outputs.

Flow is built around evolution. You describe how a system changes through time. That description is what runs.

An engineer working on a physical system today crosses Python for analysis, MATLAB for controller design, Simulink for block diagrams, C/C++ for deployment, Verilog for hardware, and vendor tools for the rest. Every handoff loses information. The mathematical model drifts from the deployed code.

Flow collapses those boundaries. The model is the program. The compiler understands units, sample rates, timing contracts, memory topology, and numeric precision as part of the type system, and emits portable C by default.

That is a complete program. The compiler hands the right-hand side to an RK4 solver and runs it at native speed. No notebook, no glue code, no translation step between model and deployment.

Full thesis: [Vision](vision.md). Domain architecture: [physical-systems.md](vision/physical-systems.md).

---

## Three ways in

Pick one path. Everything else lives in the sections below.

| | Path | What you get |
|---|---|---|
| **01 · Start** | [Install in five minutes](getting-started.md) | Compile `hello_world`, then run the tutorial app in the browser. |
| **02 · Watch** | [See compiled programs run](demos/overview.md) | Games, morphogenesis, neurons, planets. Real `gfx` recordings, not mocks. |
| **03 · Reference** | [Language and library](language/spec-index.md) | Spec, grammar, stdlib, effects, autodiff, memory, RT safety. |

---

## See it run

Frames below come straight from the native `gfx` backend.

| | | |
|:---:|:---:|:---:|
| ![Lorenz attractor](demos/lorenz.gif) | ![Flow Tetris](demos/tetris.gif) | ![Flow 2048](demos/2048.gif) |
| [Lorenz](../examples/evolution/lorenz_gfx.flow), `flow` block, RK4 | [Tetris](../examples/games/tetris_gfx.flow), full game loop | [2048](../examples/games/2048_gfx.flow), grid logic |

[All galleries](demos/overview.md): games, morphogenesis, neurons, evolution, planets, procgen, numerical, WASM.

Run any of them natively:

```bash
./flow gfx examples/games/tetris_gfx.flow
./flow gfx examples/evolution/lorenz_gfx.flow
./flow gfx examples/morphogenesis/gray_scott.flow
./flow gfx examples/neuro/hodgkin_huxley.flow
```

Record any headlessly, no display needed:

```bash
FLOW_GFX_RECORD_FRAMES=240 ./flow record examples/<path>/<name>_gfx.flow
```

---

## Features that matter here

| | |
|---|---|
| **Algebraic effects** | Swap I/O and state at the handler. Call sites stay pure. |
| **Built-in autodiff** | Forward and reverse mode in the language. Not a library bolt-on. |
| **`flow` / `evolves`** | Continuous and hybrid dynamics as syntax, with solvers and analysis. |
| **Dual backends** | Portable C by default. MLIR when you want JIT. |
| **Native `gfx`** | Real-time 2D and 3D drawing from the runtime, used by every gallery. |
| **Real-time audio** | DSP primitives and an RT-safe audio module in the stdlib. |

Thesis: [Vision](vision.md). How to write it: [Best practices](language/best-practices.md). Vs others: [Comparison](comparison.md).

---

## Everyday commands

```bash
./flow run program.flow        # C backend (default)
./flow gfx examples/...        # native window
./flow test --strict --tier2   # type-check + corpus
./flow mlir-run program.flow   # MLIR pipeline
./flow lsp                     # editor support
./flow repl                    # interactive mode
./flow fmt program.flow        # format
./flow python mylib.flow       # emit a pip-installable wheel
```

Host switch: `FLOW_HOST=flowc|python|auto` (default `flowc` for `run` and `compile`).

[CLI and development](DEVELOPMENT.md).

---

## Language reference

| Document | What it covers |
|---|---|
| [Overview](language/overview.md) | Language philosophy and feature tour |
| [Best practices](language/best-practices.md) | Idioms and why Flow favors fluid abstraction |
| [Spec index](language/spec-index.md) | Entry point into the full specification |
| [Language spec](LANGUAGE_SPEC.md) | Complete language reference |
| [Grammar](language/grammar.md) · [EBNF](grammar.ebnf) | Formal grammar |
| [Syntax](language/syntax.md) | Lexical structure |
| [Types](language/types.md) | Type system |
| [Spans](language/spans.md) | Source spans and diagnostics |
| [Lifetime domains](language/lifetime-domains.md) | Ownership and borrowing model |
| [Variables](language/variables.md) | Variables and mutability |
| [Functions](language/functions.md) | Function definitions |
| [Modules](language/modules.md) · [Namespacing](language/modules-namespacing.md) | Module system |
| [Dynamics DSL](language/dynamics-dsl.md) | `flow` / `evolves` syntax and solvers |
| [Graphics](language/graphics.md) · [3D](language/graphics-3d.md) · [Shaders](language/shaders.md) | Native graphics API |
| [Async effects](language/async-effects.md) | Effect handlers and async |
| [Concurrency vs Go](language/concurrency-vs-go.md) · [Replace Go](language/replace-go.md) | Concurrency model |
| [WASM](language/wasm.md) · [WASM crossings](language/wasm-crossings.md) | WebAssembly target |
| [MLIR opt flags](language/mlir-opt-flags.md) | MLIR pipeline tuning |
| [Explainable compilation](language/explainable-compilation.md) | Compiler transparency |
| [Debugging](language/debugging.md) | Debug workflow |
| [Ordering](language/ordering.md) | Evaluation order |
| [C fnptr call](language/c-fnptr-call.md) | FFI function pointers |

---

## Standard library

| Module | What it gives you |
|---|---|
| [API reference](library/stdlib-reference.md) · [API index](library/stdlib-api.md) | Full stdlib index |
| [Core](library/core.md) | Built-in functions |
| [Autodiff](library/autodiff.md) · [Guide](library/autodiff-guide.md) | Forward and reverse mode |
| [Dynamics](library/dynamics.md) | Solvers and analysis for `flow` blocks |
| [Audio](library/audio.md) · [Audio safety](library/audio-safety.md) | Real-time DSP primitives |
| [Memory](library/memory.md) | Memory management |
| [GPU memory](library/gpu-memory.md) | GPU memory model |
| [RT safety](library/rt-safety.md) | Real-time safety guarantees |
| [Planet](library/planet.md) | Cubesphere planet pipeline |
| [Procgen](library/procgen.md) | Noise, WFC, Voronoi, biomes |
| [FMM 2D](library/fmm2d.md) | Adaptive Fast Multipole Method |

---

## Verification and proofs

| Document | What it covers |
|---|---|
| [Verification design](language/verification.md) | `theorem` / `therefore` language spec |
| [Epistemology](language/epistemology.md) | Claim Path grammar |
| [Proof book](language/math-proof-book.md) | Numbered proof book plan |
| [Mathlib roadmap](language/mathlib-equivalence-toc.md) | Mathlib parity TOC |
| [Claim coordinates](language/claim-coordinates.md) | How claims are located |
| [flow-verify](third-party/flow-verify.md) | Third-party formal proof library |
| [Proof catalog](third-party/flow-verify-catalog.md) | Auto-generated proof index |
| [Proof graph](third-party/proof-graph.md) | Dependency graph of proofs |

Proofs are optional. `flow-verify` is third-party and not required to use Flow.

---

## Tutorials

| Lesson | Level |
|---|---|
| [Beginner](tutorials/beginner.md) | First programs |
| [Intermediate](tutorials/intermediate.md) | Deeper concepts |
| [Advanced](tutorials/advanced.md) | Expert techniques |
| [Dynamics](tutorials/dynamics.md) | `flow` blocks and solvers |
| [Control](tutorials/control.md) | Controllers and stability |
| [Systems](tutorials/systems.md) | Systems modeling |
| [Domains](tutorials/domains.md) | Lifetime domains |
| [Game AI](tutorials/game-ai.md) | Game AI training |
| [ML on a MacBook](tutorials/ml-on-macbook.md) | ML training on CPU |
| [Effects basics](tutorials/effects-basics.md) | Algebraic effects |
| [Autodiff basics](tutorials/autodiff-basics.md) | Differentiation |
| [Audio basics](tutorials/audio-basics.md) · [RT audio](tutorials/rt-audio.md) | Audio DSP |
| [gfx basics](tutorials/gfx-basics.md) · [Shaders](tutorials/shaders.md) | Graphics |
| [Arrays](tutorials/arrays.md) · [Strings](tutorials/strings.md) · [Structs](tutorials/structs.md) | Data structures |
| [Functions](tutorials/functions.md) · [Pointers](tutorials/pointers.md) · [Memory](tutorials/memory.md) | Low-level |
| [Errors](tutorials/errors.md) · [Spans](tutorials/spans.md) | Error handling |
| [Concurrency](tutorials/concurrency.md) · [Pipelines](tutorials/pipelines.md) | Concurrent code |
| [Algorithms](tutorials/algorithms.md) | Algorithms |
| [Evolution](tutorials/evolution.md) | Evolutionary biology |
| [WASM](tutorials/wasm.md) | WebAssembly target |
| [Projects](tutorials/projects.md) | Building larger programs |

---

## Demos and galleries

| Gallery | What it is | GIFs |
|---|---|---|
| [Games](demos/games.md) | Snake, Tetris, Asteroids, Flappy, and more | 25 |
| [Morphogenesis](demos/morphogenesis.md) | Reaction-diffusion, Turing patterns, DLA, L-systems, Physarum | 40 |
| [Neurons](demos/neuro.md) | Hodgkin-Huxley, Izhikevich, balanced E/I, Hopfield, CPG gaits | 15 |
| [Evolutionary biology](demos/evoleco.md) | Wright-Fisher, SIR, Muller ratchet, Red Queen, runaway selection | 25 |
| [Planets](demos/planet.md) | Cubesphere pipeline: tectonics through biomes | 7 |
| [Procedural generation](demos/procgen.md) | Noise, heightmaps, caves, WFC, Voronoi, islands | 8 |
| [Numerical methods](demos/numerical.md) | Adaptive Fast Multipole Method, gated against the direct sum | recorded |
| [Evolution suite](demos/evolution.md) | Systems evolving through time, checked against theory | 34 |
| [WebAssembly](demos/wasm.md) | Games and demos running in a browser | live |
| [Recording demos](demos/README.md) | How the GIFs are captured | scripts |

[Effects showcase](effects-showcase.md): algebraic effects end to end, with `examples/effects/showcase.flow`.

---

## Research

| Document | What it is |
|---|---|
| [Turing proof](research/turing_proof.md) | Turing-completeness argument |
| [Research paper](research/FLOW_RESEARCH_PAPER.md) | Language research writeup |
| [Compiler architecture](research/flow_compiler_architecture/) | Compiler design notes |
| [Schur lattice allpass](research/schur_lattice_allpass/) | Audio filter research |

---

## Project

| Document | What it covers |
|---|---|
| [Changelog](project/CHANGELOG.md) | Version history and audit fixes |
| [Contributing](project/CONTRIBUTING.md) | How to contribute, security policy |
| [Releasing](project/RELEASING.md) | Release process |
| [Architecture](project/architecture-writeup.md) | Codebase architecture |
| [Maturity](project/maturity.md) | Feature maturity by area |
| [Self-hosting](project/self-hosting.md) | Stage-A `flowc` in `compiler/` |
| [Questions](project/Questions.md) | Open questions |
| [What's next](NEXT.md) | Prioritized roadmap after v0.7.0 audit |
| [Development](DEVELOPMENT.md) | Building Flow from source |
| [Package registry](project/package-registry.md) | Flow package registry |
| [Pattern adoption](project/pattern-adoption.md) | Codebase patterns |
| [Example atlas](project/example-atlas.md) | Example index |
| [Tests in Flow](project/tests-in-flow.md) · [Runtime in Flow](project/runtime-in-flow.md) · [Python in Flow](project/python-in-flow.md) | Self-hosting tracks |
| [Linguist](project/linguist.md) | Language detection |
| [Issues checklist](project/issues-checklist.md) | Open issues |

---

## Documentation project

| Document | What it is |
|---|---|
| [Wiki strategy](wiki-strategy.md) | Long-term documentation architecture |
| [Wiki roadmap](wiki-roadmap.md) | Phased wiki delivery plan |

Site: [flooooooooooow.github.io/flow](https://flooooooooooow.github.io/flow/).

---

## Examples

All examples live in [`examples/`](../examples/):

```
examples/
├── basics/           # Hello world, fibonacci, etc.
├── games/            # Tetris, 2048, Snake, Asteroids (24 entries)
├── ml/               # ML framework + autodiff
├── morphogenesis/    # Reaction-diffusion, Turing patterns
├── neuro/            # Hodgkin-Huxley, Izhikevich, Hopfield
├── evoleco/          # Wright-Fisher, SIR, Muller ratchet
├── effects/          # Algebraic effects demos
├── evolution/        # Lorenz, RK4, systems through time
├── planet/           # Cubesphere planet pipeline
├── procgen/          # Noise, WFC, Voronoi, biomes
├── numerical/        # FMM and numerical methods
├── stats/            # Regression and stats
├── net/              # Networking sketches
└── ...
```

Entrypoints by domain: [examples/README.md](../examples/README.md). Compile status of every example: [examples/STATUS.md](../examples/STATUS.md).

Run any example:

```bash
./flow run examples/basics/hello_world.flow
./flow gfx examples/games/tetris_gfx.flow
```

---

## Project

| | |
|---|---|
| Version | 0.9.0 · [changelog](project/CHANGELOG.md) |
| License | [MIT](../LICENSE) |
| Source | [github.com/flooooooooooow/flow](https://github.com/flooooooooooow/flow) |
| Community | [Discord](https://discord.gg/YK7VaHy24T) · [Discussions](https://github.com/flooooooooooow/flow/discussions) |
| Cite | [CITATION.cff](../CITATION.cff) |
| Optional proofs | [flow-verify](third-party/flow-verify.md), third-party, not required to use Flow |

---

<p align="center">
  <img src="assets/flow-mascot.png" alt="Flowy the Hedgehog, the Flow mascot" width="80">
  <br>
  <em>Made with care by humans and AI · mascot: <a href="assets/mascot.md">Flowy the Hedgehog</a></em>
</p>
