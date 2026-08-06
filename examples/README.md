# Flow Examples

Comprehensive examples demonstrating Flow's capabilities across multiple domains.

## Directory Structure

```
examples/
├── ai/               # Game-AI training (Q-learning, GA, policy gradients)
├── basics/           # Fundamental algorithms, Result, match
├── audio/            # Real-time audio DSP (@rt_safe demos)
├── compilers/        # Language implementation demos
├── concurrency/      # Channels / pipelines (Go-style runtime)
├── crypto/           # Cryptographic algorithms
├── data/             # Data processing
├── dynamics/         # Dynamical systems, control, GA search (dsys DSL)
├── concurrency/      # Channels, select2, FiberAsync, netpoll, parallel for
├── ecosystem/        # Registry packages: json, toml, http, sqlite demos
├── effects/          # Flow's unique effect system
├── evolution/        # Flagship vision suite: systems evolving through time
├── games/            # Interactive games with graphics
├── generics_traits/  # Generic programming and traits
├── gpu/              # GPU/Metal computation
├── graphics/         # Rendering and shaders
├── interop/          # FFI / Python embedding
├── linalg/           # Linear algebra
├── ml/               # Machine learning framework
│   ├── models/       # Trained demos (XOR MLP, …)
│   └── autodiff/     # Autodiff + neural-net examples (was neural_networks/)
├── circuits/         # Circuit simulation: MNA solver, SPICE front end, 12 gated examples
├── morphogenesis/    # Pattern formation and growth: 40 live gfx demos
├── net/              # Networking sketches (HTTP / TCP)
├── neuro/            # Neurons and networks: 15 gated gfx simulations
├── evoleco/          # Evolutionary biology: 15 gated pop-gen / game / ecology gfx
├── numerical/        # Scientific computing
├── packages/         # Path-dependency package consumer
├── physics/          # Physics DSL experiments
├── stats/            # Statistics / regression
├── systems/          # Systems programming + system_info
├── threed/           # Software 3D renderer demos (render3d.flow)
├── ui/               # UI layout (stdlib ui_layout)
├── verify/           # flow-verify proof corpus (not the tourist showcase)
└── wasm/             # WASM target smoke (Flow→C→emcc)
```

> **Note:** `verify/` is a large proof / theorem corpus written ahead of the
> verification checker. Prefer the **Canonical entrypoints** tables below for
> “show me Flow” demos — not random files under `verify/`.

## Canonical entrypoints (Tier-0)

| Domain | Path | Run command |
|--------|------|-------------|
| Basics / hello | `examples/basics/hello_world.flow` | `./flow run examples/basics/hello_world.flow` |
| Effects | `examples/effects/showcase.flow` | `./flow run examples/effects/showcase.flow` |
| ML (XOR net) | `examples/ml/models/mlp_xor.flow` | `./flow run examples/ml/models/mlp_xor.flow` |
| ML (digits trainer) | `examples/ml/digits_mlp.flow` | `FLOW_HOST=python ./flow run examples/ml/digits_mlp.flow` |
| Audio / `@rt_safe` | `examples/audio/rt_safe_callback.flow` | `./flow run examples/audio/rt_safe_callback.flow` |
| Audio / DSP | `examples/audio/lattice_allpass_phase_engine.flow` | `./flow run examples/audio/lattice_allpass_phase_engine.flow` |
| UI layout | `examples/ui/layout_hello.flow` | `./flow run examples/ui/layout_hello.flow` |
| UI (windowed) | `demos/ui_layout_flow` | `./flow demo ui-layout` |
| HTTP slice | `examples/net/http_hello.flow` | `./flow run examples/net/http_hello.flow` |
| Packages | `examples/packages/use_hello_lib/` | `python3 -m flow.package install` then `./flow run …/src/main.flow` |
| WASM | `examples/wasm/hello_wasm.flow` | `./flow run` / `./flow wasm examples/wasm/hello_wasm.flow` |
| Concurrency | `examples/concurrency/channels.flow` | `./flow run examples/concurrency/channels.flow` |
| Morphogenesis | `examples/morphogenesis/gray_scott.flow` | `./flow gfx examples/morphogenesis/gray_scott.flow` |
| Circuits | `examples/circuits/rc_rl_rlc.flow` | `./flow run examples/circuits/rc_rl_rlc.flow` |
| Neurons | `examples/neuro/hodgkin_huxley.flow` | `./flow gfx examples/neuro/hodgkin_huxley.flow` |

## Quick Start

```bash
# Run any example
./flow run examples/basics/hello_world.flow

# Run with graphics (macOS)
./flow compile examples/games/tetris_gfx.flow
clang -O2 build/tetris_gfx.c runtime/gfx_macos.m \
    -framework Cocoa -framework CoreGraphics -framework QuartzCore \
    -o build/tetris_gfx
./build/tetris_gfx
```

## Canonical entrypoints

One tourist-facing entrypoint per domain. Prefer these when demoing or linking from docs.

| Domain | Path | Run command |
|--------|------|-------------|
| Basics / hello | `examples/basics/hello_world.flow` | `./flow run examples/basics/hello_world.flow` |
| Errors / Result | `examples/basics/result_pipeline.flow` | `./flow run examples/basics/result_pipeline.flow` |
| Match / enums | `examples/basics/match_enums.flow` | `./flow run examples/basics/match_enums.flow` |
| Effects | `examples/effects/showcase.flow` | `./flow run examples/effects/showcase.flow` |
| ML (XOR net) | `examples/ml/models/mlp_xor.flow` | `./flow run examples/ml/models/mlp_xor.flow` |
| Autodiff / NN | `examples/ml/autodiff/nn_xor.flow` | `./flow run examples/ml/autodiff/nn_xor.flow` |
| Stats / regression | `examples/stats/regression_gd.flow` | `./flow run examples/stats/regression_gd.flow` |
| Evolution (flagship) | `examples/evolution/pendulum_evolves.flow` | `./flow run examples/evolution/pendulum_evolves.flow` |
| Dynamics / `dsys` | `examples/dynamics/ga_dsys_syntax.flow` | `./flow run examples/dynamics/ga_dsys_syntax.flow` |
| Games / graphics | `examples/games/tetris_gfx.flow` | `./flow gfx examples/games/tetris_gfx.flow` |
| 3D / software raster | `examples/threed/spinning_solids.flow` | `./flow gfx examples/threed/spinning_solids.flow` |
| Shaders | `examples/graphics/shader_demo.flow` | `./flow run examples/graphics/shader_demo.flow` |
| GPU / SIMD | `examples/gpu/simd_saxpy.flow` | `./flow run examples/gpu/simd_saxpy.flow` |
| Linalg | `examples/linalg/matrix_ops.flow` | `./flow run examples/linalg/matrix_ops.flow` |
| Numerical | `examples/numerical/ode_solver.flow` | `./flow run examples/numerical/ode_solver.flow` |
| Systems | `examples/systems/ring_buffer.flow` | `./flow run examples/systems/ring_buffer.flow` |
| System info | `examples/systems/system_info.flow` | `./flow run examples/systems/system_info.flow` |
| Networking | `examples/net/tcp_echo.flow` | `./flow run examples/net/tcp_echo.flow` |
| Interop / FFI | `examples/interop/python_embed.flow` | `./flow run examples/interop/python_embed.flow` |
| Audio / RT | `examples/audio/lattice_allpass_phase_engine.flow` | `./flow run examples/audio/lattice_allpass_phase_engine.flow` |
| Generics / traits | `examples/generics_traits/generics_demo.flow` | `./flow run examples/generics_traits/generics_demo.flow` |
| Verify (repair) | `examples/verify/circuits/full_adder.flow` | proof corpus — see `full_adder.proof.md` |
| HTTP slice | `apps/flow-http/http.flow` | `./flow run apps/flow-http/http.flow` |
| Concurrency | `examples/concurrency/channels.flow` | `./flow run examples/concurrency/channels.flow` |

## Categories

### Basics (`basics/`)
Fundamental algorithms demonstrating Flow syntax:
- `hello_world.flow` - First program
- `fibonacci.flow` - Recursive functions
- `bubble_sort.flow` - Array manipulation
- `prime_numbers.flow` - Loops and conditionals
- `result_pipeline.flow` - Option/Result-style error chaining
- `pipeline_placeholder.flow` - `|>` pipeline with `_` argument placeholder
- `pipeline_fork.flow` - `|>` fork block: one value into a named record of pipelines
- `pipeline_fork_inferred.flow` - `|>` anonymous fork block with an inferred record type
- `pipeline_choose.flow` - `|>` `choose` stage: state-driven pipeline selection
- `match_enums.flow` - `match` on a simple enum

### Games (`games/`)
25 complete games, all playable via `./flow gfx <file>` (or headless via `./flow record <file>`). Every game has a recorded gameplay GIF in the [game gallery](../docs/demos/games.md). Flagship writeup: [docs/demos/chetris.md](../docs/demos/chetris.md).

Arcade:
- `snake_gfx.flow` - Snake with growth, speed-up, wall/self death
- `pong_gfx.flow` - Pong vs AI, hit-position bounce angles, first to 7
- `breakout_gfx.flow` - 6 brick rows, lives, staged speed-ups, level rebuild
- `asteroids_gfx.flow` - Inertial ship, splitting asteroids, waves
- `tetris_gfx.flow` - Complete Tetris: 7 tetrominoes, ghost piece, levels
- `invaders_gfx.flow` - Marching alien grid, bombs, destructible bunkers
- `flappy_gfx.flow` - Gravity/flap physics, pipe gaps, session best score
- `frogger_gfx.flow` - Car lanes, ride-or-drown logs, home slots, timer
- `missile_gfx.flow` - Missile Command: crosshair, blast rings, six cities
- `maze_chase_gfx.flow` - Maze, pellets, 3 ghost styles, power-mode chains
- `lane_racer_gfx.flow` - 4-lane traffic dodger, near-miss bonus, fuel
- `jumper_gfx.flow` - Vertical platformer: moving/crumbling platforms, springs
- `icy_tower_gfx.flow` - Momentum platformer: running speed sets jump height and reach, wall bounces keep it, multi-floor landings chain a named combo, the tower scrolls faster the higher you get

Puzzle and logic:
- `minesweeper_gfx.flow` - 16x16, 40 mines, flood fill, safe first click
- `sokoban_gfx.flow` - 5 levels, push mechanics, undo, move counter
- `match3_gfx.flow` - 8x8 gems, cascade chains, move limit
- `lightsout_gfx.flow` - 5x5 cross-toggle, always-solvable scrambles
- `hanoi_gfx.flow` - 3-7 disks, legality enforcement, optimal-move compare
- `simon_gfx.flow` - Growing color sequences, strict fail, session best
- `2048_gfx.flow` - 2048 puzzle game (also `2048.flow` for the terminal)

Board:
- `connect4_gfx.flow` - vs AI (takes wins, blocks losses), falling-disc animation
- `othello_gfx.flow` - vs corner-aware AI, staged flip animation, pass handling
- `checkers_gfx.flow` - Hotseat, forced captures, multi-jump chains, kings
- `chetris_gfx.flow` / `chetris_test.flow` - Chess×Tetris hybrid + mechanics suite

Sandbox:
- `falling_sand_gfx.flow` - The Falling Sand Game: 384x192 cells at one cell per pixel, wall/sand/water/oil/fire/plant/salt/salt water/steam/ice plus spouts, keyboard pen

### 3D (`threed/`)
Eight demos on `lib/stdlib/render3d.flow`, a software rasterizer written in Flow
(pipeline, caps and limitations: [docs/language/graphics-3d.md](../docs/language/graphics-3d.md);
per-example table: [examples/threed/README.md](threed/README.md)):
- `spinning_solids.flow` - Five Platonic solids from vertex lists, faces recovered by a plane sweep; wire / flat / Gouraud / unlit
- `fps_camera.flow` - First-person camera, per-axis box collision, gravity and jumping
- `third_person.flow` - Chase camera with smoothing and raycast occlusion pull-in
- `heightmap_terrain.flow` - Value-noise terrain, four octaves, walked with distance fog
- `voxel_world.flow` - Chunked block field, visible-face meshing, raycast block selector
- `physics3d.flow` - Rigid spheres, restitution, sphere-sphere and sphere-plane impulses, energy readout
- `raycast_shooter.flow` - Ray-vs-AABB picking and hitscan from one query, waves and score
- `billboard_particles.flow` - 1200 alpha-blended billboards, depth-sorted by a counting sort

### Ecosystem (`ecosystem/`)
Registry package demos (`./flow install` then `./flow run` or `./flow run-native`):
- Pure Flow: `json_demo`, `toml_demo`, `serde_demo`, `strings_demo`, `cli_demo`, `log_demo`, `testing_demo`, `collectionsx_demo`
- Native: `http_get`, `sqlite_demo`, `sqlkit_demo`, `compress_demo`, `dns_demo`, `image_demo`, `ffi_demo`
- End-to-end: `app_cache/` — cli + log + json + sqlite + sqlkit (offline; `USE_HTTP=0`)

### Compilers (`compilers/` + `compiler/`)
Self-hosting bootstrap (not a full compiler yet — see [compiler/README.md](../compiler/README.md)):
- **`compiler/` (`flowc`)** — Flow-in-Flow front-end: token + lexer + AST + subset parser (no C emitter) — `./flow run compiler/src/main.flow`
- `compilers/calculator.flow` - Recursive-descent expression parser
- `compilers/flow_identifier_lexer.flow` / `flow_lexer.flow` - historical lexer seeds

### Game AI (`ai/`)
Trains real agents on headless re-simulations of the games, using
`lib/stdlib/ai.flow` (tutorial: [docs/tutorials/game-ai.md](../docs/tutorials/game-ai.md)).
Each demo prints its learning curve, evaluates against a random baseline and
exits 0 only when the trained agent wins by a wide margin:
- `q_snake.flow` - Tabular Q-learning on snake (`./flow run examples/ai/q_snake.flow`)
- `ga_flappy.flow` - Neuroevolution on flappy (`./flow run examples/ai/ga_flappy.flow`)
- `policy_pong.flow` - REINFORCE policy MLP on pong (`./flow run examples/ai/policy_pong.flow`)

### Machine Learning (`ml/`)
Neural network framework + autodiff:
- `tensor.flow` - N-dimensional tensor type
- `nn_layers.flow` - Dense layers, activations
- `optimizers.flow` - SGD, Adam, RMSprop
- `models/mlp_xor.flow` - XOR via grad codegen (`nn_autogen`)
- `models/mlp_xor_from_scratch.flow` - pedagogical hand backprop
- `digits_mlp.flow` - 10-class 8x8 digits MLP, synthetic dataset generated in Flow, minibatch SGD + momentum, 90% accuracy gate (`FLOW_HOST=python ./flow run`)
- `digits_mlp_parallel.flow` - same model with pthread gradient-accumulation shards; prints measured serial vs parallel speedup
- `digits_mlp_metal.flow` - Metal GPU status: unified buffers, elementwise kernel parity + CPU/GPU crossover timings
- `autodiff/` - Autodiff benchmarks, backprop, `nn_xor.flow` (merged from `neural_networks/`)

See the walkthrough with measured timings: [docs/tutorials/ml-on-macbook.md](../docs/tutorials/ml-on-macbook.md)

### Stats (`stats/`)
- `regression_gd.flow` - Gradient-descent line fit (plain f32 math)

### Networking (`net/`)
- `tcp_echo.flow` - TCP listener shape demo (full echo loop planned)

### Evolution (`evolution/`)
The flagship suite for Flow's founding vision — systems that evolve through time
(see [evolution/README.md](evolution/README.md)). Prefer declarative files:
- `pendulum_evolves.flow` / `pendulum_rk4.flow` / `pendulum_always.flow` — `flow` + `evolves`
- `bouncing_ball_evolves.flow` — `when … reaches` hybrid bounce
- `robot_connect.flow` — `connect` composition
- `spring_mass_control.flow` — Model → analyze → control (`dsys` DSL)
- `lorenz_gfx.flow` — `flow Lorenz` live in a window (`./flow gfx`)
- `pendulum.flow` / `bouncing_ball.flow` — pedagogical hand integrators only

### Circuits (`circuits/`)
Twelve circuit-simulation programs plus a SPICE-subset netlist front end (see
[circuits/README.md](circuits/README.md)). Each one prints what it measured
next to what the closed form says and gates its exit code on the two agreeing,
so they are measurements rather than pictures. Circuits that are genuinely
differential-algebraic use the modified-nodal-analysis solver in
`stdlib/circuit.flow`; circuits that are really ODEs are written as `flow`
blocks with `evolves as`, and every header says which and why:
- `rc_rl_rlc.flow` - three step responses, three integrators, three closed forms
- `mna_dc.flow` - two resistive ladders against hand arithmetic, to 8.7e-16
- `lc_tank.flow` - 1000 lossless cycles: trapezoidal conserves, backward Euler damps at its predicted rate
- `diode_iv.flow` / `bjt_curves.flow` - Newton against Shockley and Ebers-Moll
- `logic_delays.flow` - a ripple-carry adder from 20 one-line `flow` gates
- `chua.flow` - the double scroll, with a Lyapunov exponent measured two ways
- `netlist_demo.flow` - three SPICE decks parsed off disk into the same solver

### Morphogenesis (`morphogenesis/`)
Twenty live graphics demos of pattern formation and growth, the visual
companion to `evolution/` (see
[morphogenesis/README.md](morphogenesis/README.md)). Continuous models state
their dynamics as a `flow` block with `evolves as`; every example labels its
parameters on screen with `stdlib/text.flow` and carries a live measurement
of what it is claiming:
- `gray_scott.flow` - Gray-Scott reaction-diffusion, five F/k presets
- `turing_spots.flow` / `turing_stripes.flow` - one coefficient apart
- `belousov.flow` - Barkley excitable medium, rotating spiral waves
- `dla.flow` - diffusion-limited aggregation with a live fractal dimension
- `slime_mold.flow` - Physarum agents building a transport network
- `somite_clock.flow` - `phase evolves as omega` read out by a moving front

### Neurons and networks (`neuro/`)
Fifteen live graphics simulations of spiking dynamics, the second domain of
[the Example Atlas](../docs/project/example-atlas.md) (see
[neuro/README.md](neuro/README.md)). Each one measures the phenomenon it
demonstrates, prints the measurement beside the published value, and returns
a nonzero exit code if the comparison fails, so they are regression tests as
well as demos. Continuous models are `flow` blocks with `evolves as`; spike
resets are `when v reaches threshold { v becomes reset }`.
- `hodgkin_huxley.flow` - four gates, peak +40.26 mV, firing onset 6.213 uA/cm2
- `izhikevich_zoo.flow` - all twenty regimes of Izhikevich 2004 figure 1, each checked
- `lif_fi_curve.flow` - measured F-I curve against its closed form, 512 ppm
- `morris_lecar.flow` - Hopf point at 93.8576 uA/cm2 by bisection on tr J = 0
- `balanced_network.flow` - 12500 LIF neurons at the mean-field rate, CV(ISI) 0.795
- `hopfield.flow` - capacity 0.166 against the 0.138 N bound, energy monotone
- `reservoir.flow` - memory capacity 40.566 against Jaeger's bound of N = 100

Run them with `./flow record examples/neuro/<name>.flow --frames 90 --out
build/frames --gif build/<name>.gif`, or windowed with `./flow gfx`.
Gallery: [docs/demos/neuro.md](../docs/demos/neuro.md); regenerate with
`python3 scripts/record_demos.py --group neuro`.

### Evolutionary biology (`evoleco/`)
Fifteen live graphics simulations for evolutionary biologists — population
genetics, evolutionary games, and ecology companions — the chemistry/biology
domain of [the Example Atlas](../docs/project/example-atlas.md) (see
[evoleco/README.md](evoleco/README.md)). Each one gates a closed-form or
textbook measurement before the window opens.
- `wright_fisher.flow` - heterozygosity decay and fixation time vs 4 N ln 2
- `hardy_weinberg.flow` - genotype frequencies recover p^2 : 2pq : q^2
- `selection_locus.flow` / `mutation_selection.flow` - logistic selection; p* = u/s
- `spatial_pd.flow` / `rock_paper_scissors.flow` - spatial games vs mean-field
- `lotka_volterra_gfx.flow` / `sir_spatial.flow` - visual ecology companions

Run with `./flow gfx examples/evoleco/<name>.flow` or headless
`./flow record`. Gallery: [docs/demos/evoleco.md](../docs/demos/evoleco.md);
regenerate with `python3 scripts/record_demos.py --group evoleco`.

### Dynamics (`dynamics/`)
Dynamical systems, analysis, and control via `stdlib/dynamics` and the
declarative `dsys` surface syntax (see [dynamics/README.md](dynamics/README.md)):
- `ga_dsys_syntax.flow` - Every `dsys`/`sense`/`ga evolve`/`closed`/`analyze` block in one file
- `controllability_demo.flow` - Controllability + similarity transforms
- `gramian_demo.flow` - Finite vs infinite horizon Gramians
- `ga_full_analysis.flow` - GA control search with unified analysis report
- `lorenz_attractor.flow` - Chaos detection via Lyapunov separation proxy

### Concurrency (`concurrency/`)
Beat-Go track — see `docs/language/concurrency-vs-go.md`:
- `channels.flow` - Real buffered channel send/recv/close
- `select.flow` - Two-channel `select2` / `select2_try`
- `parallel_for.flow` - Data-parallel loop (OpenMP when available)
- `threaded_async.flow` - `ThreadedAsync` effect over real pthreads
- `fiber_async.flow` - `FiberAsync` M:N fibers (`FLOW_MAXPROCS`)
- `gomaxprocs.flow` - `async_set_maxprocs` (GOMAXPROCS analogue)
- `netpoll.flow` - `NetpollAsyncIO` (kqueue/epoll)

### Effects (`effects/`)
Flow's unique algebraic effects (not available in Mojo/Julia):
- `showcase.flow` - One business function, four handler stacks (production/test/nested/composed)
- `effect_rows.flow` - Signature effect rows (`with E`) under `--strict-effects`
- `dependency_injection.flow` - DI without frameworks
- `state_effects.flow` - Swappable policy effects with explicitly-threaded state
- `async_primitives.flow` - stdlib `Async`/`AsyncIO` via `handle`/`with`
- `async_effects.flow` - Timeout/Retry as policy effects

### Audio (`audio/`)
Real-time DSP:
- `rt_safe_callback.flow` - Minimal `@rt_safe` process block (no heap)
- `lattice_allpass_phase_engine.flow` - `@rt_safe` phase engine
- `loopback_effects.flow` - Input -> effect chain -> output (requires audio backend)
- `offline_graph_demo.flow` - Offline graph processing demo
- `bus_graph_demo.flow` - Parallel bus routing demo
- `gpu_gain_demo.flow` - GPU gain demo (CPU fallback)
- `live_graph_demo.flow` - Live graph single-standard demo
- `lattice_allpass_phase_engine.flow` - `@rt_safe` phase engine

### Linear Algebra (`linalg/`)
Matrix operations (Julia territory):
- `blas_demo.flow` - Accelerate/OpenBLAS via `stdlib/blas.flow`
- `lu_decomposition.flow` - `solve` + `lu_factor` (tourist)
- `lu_decomposition_pedagogical.flow` - hand Doolittle / pivoted LU
- `matrix_ops.flow` - Basic matrix operations

### Numerical (`numerical/`)
Scientific computing:
- `ode_solver.flow` - Euler, RK4 ODE solvers
- `optimization.flow` - Gradient descent, Newton's method

### Systems (`systems/`)
Low-level systems programming:
- `memory_pool.flow` - O(1) pool allocator
- `ring_buffer.flow` - Lock-free SPSC queue
- `hash_table.flow` - Open addressing hash table
- `system_info.flow` - OS/CPU info via stdlib (was `examples/system/`)

### GPU (`gpu/`)
Metal GPU computation:
- `gpu_fft.flow` - GPU FFT
- `simd_saxpy.flow` - SIMD operations
- `vector_add_gpu.flow` - GPU vector addition

### Graphics (`graphics/`)
- `graphics.flow` - Basic rendering helpers
- `shader_demo.flow` - Shader language catalog demo (keep; old `shader_showcase.flow` stub removed)

### Generics & Traits (`generics_traits/`)
Generic programming:
- `generics_demo.flow` - Generic type examples
- `traits_demo.flow` - Trait-based polymorphism
- `option_result_demo.flow` - Option/Result types
- `enum_match_exhaustive.flow` - Exhaustive match (deeper than `basics/match_enums.flow`)

### Verify (`verify/`)
Proof corpus for `flow-verify` (theorems, circuits, derived claims). Not the
primary showcase — see [verify/circuits/full_adder.proof.md](verify/circuits/full_adder.proof.md).


### WASM (`wasm/`)
- `hello_wasm.flow` - Fib smoke for Flow→C→WASM (`./flow run` / `./flow wasm …`; emcc optional)
- See [wasm/README.md](wasm/README.md) and `docs/language/wasm.md`

### Packages (`packages/`)
- `hello_lib/` + `use_hello_lib/` - Path-dep consumer (`flow.toml` → `flow_packages/`)
- See [packages/README.md](packages/README.md)

### UI (`ui/`)
- `layout_hello.flow` - stdlib `ui_layout` row boxes (no window)
- Windowed: `./flow demo ui-layout`

### Networking (`net/`)
- `http_hello.flow` - Thin HTTP route/status slice (no live sockets; see `apps/flow-http/http.flow`)

### Concurrency (`concurrency/`)
- `channels.flow` - send/recv/close
- `pipeline.flow` - producer → transform → consumer

## Verified Compile Status

See [STATUS.md](STATUS.md) for a machine-generated compile status table covering
every `.flow` file under `examples/`, `apps/`, and `benchmarks/` (pass/fail plus
failure category). Regenerate it with:

```bash
python3 scripts/verify_examples.py
```

A few examples known to compile *and run* successfully:

| Example | Command |
|---------|---------|
| XOR Neural Network | `./flow run examples/ml/models/mlp_xor.flow` |
| Sort Benchmark | `./flow run benchmarks/micro/sort_benchmark.flow` |
| Benchmark Runner | `./flow run benchmarks/runner.flow` |
| Generics Demo | `./flow run examples/generics_traits/generics_demo.flow` |
| Autodiff XOR | `./flow run examples/ml/autodiff/nn_xor.flow` |
| Stats GD | `./flow run examples/stats/regression_gd.flow` |
| Result pipeline | `./flow run examples/basics/result_pipeline.flow` |

## Adding New Examples

1. Create a `.flow` file in the appropriate directory
2. Include a `main() -> i32` function
3. Test with `./flow run path/to/example.flow`
4. Update this README (and the canonical entrypoints table when adding a domain)


