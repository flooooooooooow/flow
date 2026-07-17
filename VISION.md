# Flow — Vision

> A programming language where the primary abstraction is the evolution of systems through time.

This document is the founding vision for Flow: the reason the language exists and the destination the roadmap points at. For what is implemented *today*, see [Where Flow Is Today](#where-flow-is-today) at the end, the [README](README.md), and the [ROADMAP](ROADMAP.md).

---

## Vision

Modern programming languages are built around **computation**.

Flow is built around **evolution**.

Instead of describing sequences of instructions, Flow describes how systems evolve through time. Programs are mathematical systems with explicit state, dynamics, timing, constraints, and guarantees.

The compiler transforms these descriptions into deterministic, production-ready implementations suitable for embedded systems, robotics, aerospace, industrial automation, DSP, scientific computing, digital twins, and high-performance simulation.

Flow unifies:

- General-purpose programming
- Dynamical systems
- Control systems
- Signal processing
- Hybrid systems
- Embedded software
- Real-time systems
- Scientific computing
- Formal verification

## Problem

Today's engineering workflow is fragmented.

- Python performs analysis.
- MATLAB designs controllers.
- Simulink creates block diagrams.
- Modelica models physical systems.
- C/C++ deploys embedded software.
- Rust provides memory safety.
- Verification is handled elsewhere.

Every transition loses information. The mathematical model becomes disconnected from the deployed software.

Flow removes those boundaries. **The mathematical model is the executable program.**

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

Robotics · Aerospace · Automotive · Industrial automation · Medical devices · Embedded systems · Signal processing · Audio · Scientific computing · Machine learning · Digital twins · Autonomous systems · Research

## Long-Term Vision

Flow treats software as the description of an evolving system rather than a sequence of instructions. Simulation, verification, optimization, deployment, control synthesis, and execution all derive from a single source of truth.

The long-term goal is to establish Flow as the first production-ready programming language whose primary abstraction is dynamics instead of control flow, enabling engineers to describe physical, computational, and cyber-physical systems in one unified language.

---

## Where Flow Is Today

An honest mapping from vision pillars to the current implementation (2026-07):

| Vision pillar | Status today |
|---|---|
| General-purpose core (functions, generics, ADTs, pattern matching, traits) | **Shipped** — statically-typed language compiling to C via `./flow` |
| Dynamical systems | **Seed exists** — `dsys` declarative surface syntax for linear systems (`examples/dynamics/`), stdlib dynamics module |
| Analysis (controllability, spectral, gramians) | **Seed exists** — `sense on <plant>` blocks over `dsys` systems |
| Control synthesis | **Seed exists** — GA-based gain search over rollout horizons (`ga evolve on`) |
| Automatic differentiation | **Shipped** — native autodiff |
| Algebraic effects | **Shipped** — see `docs/effects-showcase.md` |
| `evolves as` continuous dynamics, ODE solvers as codegen | Not yet — the flagship gap |
| Units in the type system / dimensional analysis | Not yet |
| Explicit time (`every 1 ms`, `after`, `within`), scheduling | Not yet |
| Hybrid events (`when x reaches 0 { x becomes ... }`) | Not yet |
| `always` / `never` / temporal guarantees | Not yet |
| Flow composition (`connect { a.out -> b.in }`) | Not yet |
| Representations (linear, Koopman, transfer function) | Not yet |
| Realtime memory model, deployment blocks, fixed-point numerics | Not yet |

The gaps are tracked as vision epics on the project board. The strategy is to grow the existing `dsys`/dynamics seed toward the `flow { evolves as }` model rather than build a second language beside the current one.
