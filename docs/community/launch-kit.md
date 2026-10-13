# Launch and Outreach Kit

This document collects copy and announcements for Flow releases, Discord channels, and public sharing.

## Discord Announcement

Post this in `#announcements` for the Flow 2.0.0 release.

```markdown
@everyone **Flow 2.0.0 is released.**

Flow is a statically typed systems language where describing how a system evolves through time is the program.

### What is in 2.0.0

- **Self-hosted compiler**: `flowc` compiles itself end to end with byte-identical fixed points. A clean checkout builds with a C compiler alone.
- **Portable C and MLIR backends**: Compiles to portable C11 by default, with MLIR available for vector and JIT workflows.
- **Algebraic effects and capabilities**: 24 documented patterns covering dependency injection, state policies, handlers, and strict rows.
- **Physics and dynamics DSLs**: Differential equations, hybrid guards, and numerical integrators built directly into the language.
- **150+ graphical examples**: Morphogenesis, games, neural networks, planetary geology, and 3D voxels.

### Quickstart

Install via Homebrew on macOS or Linux:
```bash
brew tap flooooooooooow/flow
brew install flow
flow version
```

Or build from source:
```bash
git clone https://github.com/flooooooooooow/flow.git
cd flow
./flow gfx examples/evolution/lorenz_gfx.flow
```

Documentation: <https://flooooooooooow.github.io/flow/>
Repository: <https://github.com/flooooooooooow/flow>
Release notes: <https://github.com/flooooooooooow/flow/releases/tag/v2.0.0>
```

## Discord Server Channels

| Channel | Purpose |
|---|---|
| `#welcome` | Greets each new member with links to docs and source. |
| `#announcements` | Releases, milestones, and major announcements. |
| `#introductions` | Member introductions and active projects. |
| `#general` | Discussion of language design and physical modelling. |
| `#dev` | Compiler development, bug reports, and pull request activity. |
| `#showcase` | Sharing simulation recordings, games, and audio demos. |
| `#effects` | Algebraic effects, capability design, and handlers. |
| `#help` | Setup assistance and syntax questions. |

## Hacker News

Title:
```text
Show HN: Flow 2.0: A systems language where evolution through time is the program
```

URL:
```text
https://github.com/flooooooooooow/flow
```

Text:
```text
Flow is a statically typed systems language designed for physical models, games, and real-time simulations.

In most languages, code describes instructions that produce outputs from inputs. In Flow, the primary abstraction is continuous evolution through time:

flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}

The compiler generates state structures and integrates the system with a numerical solver, emitting portable C.

Key properties of 2.0.0:
1. Self-hosted compiler: flowc is written in Flow and builds with a standard C compiler.
2. Algebraic effects: first-class handlers, capabilities, and scoped resource management.
3. Native graphics and audio: real-time windowing, FSL shaders, and GIF recording built into the runtime.
4. Formal verification: 1,080 proof documents checking language mechanics and stdlib modules.

Docs: https://flooooooooooow.github.io/flow/
Source: https://github.com/flooooooooooow/flow
```

## Reddit

Post for r/programming and r/simulations.

Title:
```text
Flow 2.0: A systems language where continuous evolution is the core abstraction
```

Body:
```markdown
Flow is a statically typed compiled language designed for physical simulation, control, and real-time graphics.

Instead of writing numerical loops and manual integration routines, you define how states change over time:

```flow
flow Ball {
    state height: f64 = 2.0
    state velocity: f64 = 0.0
    param gravity: f64 = 9.81
    param restitution: f64 = 0.8

    height evolves as velocity
    velocity evolves as -gravity

    when height reaches 0.0 {
        velocity becomes -restitution * velocity
        height becomes 0.0
    }
}
```

The compiler transforms this description into C or MLIR with an integrated solver.

Highlights of version 2.0.0:
- Self-hosted flowc compiler with reproducible fixed-point builds.
- Algebraic effects system with capability-based handlers.
- Standard library covering autodiff, LAPACK wrappers, crypto, and DSP.
- 450+ examples including Gray-Scott morphogenesis, voxel worlds, and neural dynamics.

Documentation: https://flooooooooooow.github.io/flow/
Repository: https://github.com/flooooooooooow/flow
Discord: https://discord.gg/YK7VaHy24T
```

## X Thread

Post 1:
```text
Flow 2.0 is out.

A statically typed systems language built around continuous evolution through time.

The compiler takes ODEs and hybrid guards, generates numerical solvers, and emits portable C.

https://github.com/flooooooooooow/flow
```

Post 2:
```text
Writing a physical system in Flow:

flow Pendulum {
    state angle: f64 = 0.5
    state velocity: f64 = 0.0
    param damping: f64 = 0.3

    angle evolves as velocity
    velocity evolves as -9.81 * sin(angle) - damping * velocity
}

Runs at native speed with an RK4 solver.
```

Post 3:
```text
Flow 2.0 also includes:
- Algebraic effects and capabilities
- Self-hosted compiler with fixed-point proofs
- Native graphics, audio DSP, and shader DSL
- 450+ runnable examples

Docs: https://flooooooooooow.github.io/flow/
```

## Shipped Demos

Run these from a cloned repository:

```bash
# Chaos theory and dynamical systems
./flow gfx examples/evolution/lorenz_gfx.flow

# Morphogenesis: reaction-diffusion patterns
./flow gfx examples/morphogenesis/gray_scott.flow

# Electrophysiology: Hodgkin-Huxley action potentials
./flow gfx examples/neuro/hodgkin_huxley.flow

# Interactive arcade game
./flow gfx examples/games/breakout_gfx.flow

# 3D voxel engine
./flow gfx examples/threed/voxel_world.flow
```
