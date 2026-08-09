# Flow, Vision

> A programming language where the primary abstraction is the evolution of systems through time.
>
> **Product thesis:** Flow is a language for describing **physical computational systems**, RF, embedded, SDR, FPGA-adjacent, and satellite engineering first. Not "safer C," and not a
> Rust substitute: a compile-time model of units, rates, timing, memory topology, hardware, and
> fault behaviour. See [docs/vision/physical-systems.md](docs/vision/physical-systems.md).

This document is the founding vision for Flow: the reason the language exists and the destination the roadmap points at. For what is implemented *today*, see [Where Flow Is Today](#where-flow-is-today) at the end, the [README](README.md), and the [ROADMAP](ROADMAP.md). Domain beachhead architecture: [physical-systems.md](docs/vision/physical-systems.md). Grammar cards: [docs/vision/north-star.md](docs/vision/north-star.md).

---

## Vision

Modern programming languages are built around **computation**.

Flow is built around **evolution**.

Instead of describing sequences of instructions, Flow describes how systems evolve through time. Programs are mathematical systems with explicit state, dynamics, timing, constraints, and guarantees.

The compiler transforms these descriptions into deterministic, production-ready implementations suitable for embedded systems, robotics, aerospace, industrial automation, DSP, scientific computing, digital twins, and high-performance simulation.

**Evolution** is the abstraction. **Physical computational systems** are the product beachhead: an RF receiver is not merely code, the compiler should know its units, sample rates, numeric precision, memory movement, timing contracts, and target hardware, and from one description produce simulation, analysis, and heterogeneous deployment (MCU / DSP / FPGA / host).

Flow unifies:

- General-purpose programming
- Dynamical systems
- Control systems
- Signal processing / SDR
- Hybrid systems
- Embedded software
- Real-time systems
- FPGA-adjacent / heterogeneous systems
- Scientific computing
- Formal verification
- Digital twins (sim and hardware share programs)

## Problem

Today's engineering workflow is fragmented.

- Python performs analysis.
- MATLAB designs controllers.
- Simulink creates block diagrams.
- Modelica models physical systems.
- GNU Radio graphs signal processing.
- Verilog / VHDL / SystemVerilog describe hardware.
- C/C++ deploys embedded software.
- Rust provides memory safety.
- Vendor HALs, device trees, and DSLs configure the rest.
- Verification is handled elsewhere.

Every transition loses information. The mathematical model becomes disconnected from the deployed software. An RF/satellite engineer can cross all of those worlds in one project.

Flow removes those boundaries. **The mathematical model is the executable program.** The long-term objective is to unify MATLAB/Simulink + GNU Radio + C/C++/Rust + HDL + hardware configuration under one compile-time model, while keeping C-like predictability and zero-cost escape hatches.

## Philosophy

Programming should describe behavior, not implementation.

A programmer should write:

```flow
flow Pendulum {
    angle : Angle
    velocity : AngularVelocity

    angle evolves as velocity
    velocity evolves as
        -(gravity / length) * sin(angle)
}
```

instead of:

```c
while (running) {
    velocity += ...
    angle += ...
}
```

Flow answers five questions:

1. What exists?
2. How does it evolve?
3. When does it evolve?
4. Under what constraints?
5. What guarantees must always hold?

## Core Principles

### Evolution is fundamental

Evolution replaces control flow as the central abstraction. Programs describe how systems change.

### Time is explicit

Time never exists implicitly.

```flow
continuous
every 1 ms
after 50 us
within 2 s
```

### State is explicit

Everything evolves from state.

```flow
state angle
state velocity
state current
```

### Dynamics are first-class

Continuous evolution:

```flow
angle evolves as velocity
```

Discrete evolution:

```flow
counter becomes counter + 1
```

### Systems compose

```flow
flow Robot {
    motor : Motor
    controller : PID

    connect {
        controller.output -> motor.input
    }
}
```

Composition replaces procedural orchestration.

### Correctness belongs in the language

```flow
always {
    pressure <= 10 bar
}

never {
    valve.open
    pump.off
}

within 20 ms {
    actuator.updated
}
```

## Language Structure

Every program consists of one or more flows.

```
Flow
├── State
├── Inputs
├── Outputs
├── Parameters
├── Dynamics
├── Events
├── Constraints
├── Guarantees
├── Representations
└── Deployment
```

## Core Language

### State

```flow
state angle : Angle
state velocity : AngularVelocity
```

### Inputs

```flow
input voltage : Voltage
```

### Outputs

```flow
output torque : Torque
```

### Parameters

```flow
param mass : Kilogram
param damping > 0
```

### Continuous dynamics

```flow
angle evolves as velocity
velocity evolves as
    force / mass
```

### Discrete dynamics

```flow
every tick {
    counter becomes counter + 1
}
```

### Events

```flow
when temperature > 100 C {
    emit Overheated
}
```

### Constraints

```flow
always {
    current <= 10 A
}
```

### Temporal guarantees

```flow
after disturbance
angle < 2 deg
within 200 ms
```

## Real-Time Programming

Realtime behavior is native.

```flow
flow MotorController {
    realtime

    every 50 us {
        ...
    }
}
```

The compiler guarantees:

- deterministic scheduling
- bounded execution
- bounded stack
- bounded memory
- deadline satisfaction

## Memory Model

Realtime flows prohibit:

- heap allocation
- garbage collection
- blocking operations
- dynamic dispatch
- unbounded recursion
- unbounded loops

Static structures are preferred.

```flow
history samples : RingBuffer<1024>
```

## Scheduling

Scheduling belongs inside the language.

```flow
task sensors
every 1 ms

task controller
every 1 ms
after sensors

task telemetry
every 50 ms
```

## Numeric Model

Numeric behavior is explicit.

```flow
numeric {
    fixed<32,16>
    saturating
}
```

The compiler verifies overflow, precision, and execution cost.

## Units

Units belong to the type system.

```
Meter  Second  Newton  Volt  Ampere  Radian
```

This fails to compile:

```flow
length + voltage
```

## Continuous Flows

```flow
flow Pendulum {
    angle : Angle
    velocity : AngularVelocity

    angle evolves as velocity
    velocity evolves as
        -(gravity / length) * sin(angle)
}
```

## Hybrid Systems

```flow
flow Ball {
    height : Meter
    velocity : Meter / Second

    height evolves as velocity
    velocity evolves as -gravity

    when height reaches 0 {
        velocity becomes
            -0.8 * velocity
    }
}
```

## Composition

```flow
flow Robot {
    plant : Motor
    controller : PID

    connect {
        controller.output -> plant.input
        plant.speed -> controller.feedback
    }
}
```

## Mathematical Representations

Every flow has one canonical description. Different mathematical representations are compiler transformations.

```flow
flow Pendulum {
    ...
    represent nonlinear
    represent linear
    represent koopman
    represent transfer_function
    represent frequency
}
```

### Koopman representation

```flow
represent koopman {
    basis {
        angle
        velocity
        cos(angle)
    }
    evolves linearly
}
```

The programmer specifies intent. The compiler constructs the representation.

## Analysis

Analysis is part of the language.

```flow
analyze Pendulum {
    poles
    zeros
    stability
    controllability
    observability
}
```

## Control

Controllers become compiler transformations.

```flow
control Pendulum {
    objective {
        minimize error
    }
}
```

Possible implementations include PID, LQR, MPC, and observers.

## Verification

Properties become executable.

```flow
guarantee {
    stable
    passive
    causal
    realtime
}
```

Compilation fails if guarantees cannot be proven.

## Deployment

Deployment belongs inside the source.

```flow
deploy {
    cpu Cortex-M7
    period 100 us
    deadline 80 us
    solver RK4
}
```

## General-Purpose Programming

Flow is a systems language. It supports modules, packages, interfaces, generics, algebraic data types, pattern matching, asynchronous programming, networking, files, testing, and metaprogramming.

The same language builds firmware, simulations, desktop applications, cloud services, and robotics software.

## Compiler Responsibilities

The Flow compiler is responsible for:

- lowering mathematical systems
- scheduling execution
- static memory allocation
- realtime verification
- dimensional analysis
- numerical verification
- stability analysis
- controller synthesis
- representation generation
- optimization
- deterministic code generation

## Target Domains

**Beachhead:** RF · SDR · Embedded · FPGA-adjacent · Satellite / aerospace  

**Also:** Robotics · Automotive · Industrial automation · Medical devices · Signal processing · Audio · Scientific computing · Machine learning · Digital twins · Autonomous systems · Research

## Long-Term Vision

Flow treats software as the description of an evolving system rather than a sequence of instructions. Simulation, verification, optimization, deployment, control synthesis, and execution all derive from a single source of truth.

The long-term goal is to establish Flow as the production language for **physical computational systems**: engineers describe units, rates, timing, memory topology, hardware resources, numeric precision, and fault behaviour once, and the compiler participates in the engineering, not only the translation.

Dynamics (`evolves as`) remains the core abstraction; the RF/embedded/satellite vertical is how that abstraction becomes de facto in industry. Full architecture: [docs/vision/physical-systems.md](docs/vision/physical-systems.md).

---

## Where Flow Is Today

An honest mapping from vision pillars to the current implementation (2026-08):

| Vision pillar | Status today |
|---|---|
| General-purpose core (functions, generics, ADTs, pattern matching, traits) | **Shipped**, statically-typed language compiling to C via `./flow` |
| Dynamical systems / `evolves as` | **Shipped (seed)**, `flow` blocks, Euler step, `every`, hybrid `when`; see north-star cards |
| Analysis (controllability, spectral, gramians) | **Seed**, `sense on <plant>` over `dsys` |
| Control synthesis | **Seed**, GA gain search (`ga evolve on`) |
| Automatic differentiation | **Shipped** |
| Algebraic effects | **Shipped**, see `docs/effects-showcase.md` |
| Units / dimensional analysis | **Shipped**, SI units; RF pack + quantity suffixes in W0 |
| Explicit time (`every`, durations) | **Shipped** for flow blocks; scheduling/`task` still open |
| Hybrid events | **Shipped** (zero-crossing form) |
| Real-time safety | **Partial**, `@rt_safe`, lifetime domains; WCET/`guarantee` blocks still open |
| Physical-systems beachhead (RF/IQ/rates/memory attrs) | **W0 in progress**, see physical-systems.md |
| `always` / `never` / temporal guarantees | Not yet |
| Flow composition (`connect`) | Not yet |
| Representations (linear, Koopman, …) | Design (north-star) |
| FPGA / CDC / deploy partitions | Later |
| Fixed-point, MMIO/SVD, certification profiles | Later |

Gaps and sequencing: [ROADMAP.md](ROADMAP.md), [physical-systems.md](docs/vision/physical-systems.md), Helm board. Strategy: grow the evolution seed and the RF wedge together, one language, not a fork.
