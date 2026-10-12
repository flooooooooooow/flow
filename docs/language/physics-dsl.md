# Physics DSL (`@physics`)

Flow provides an experimental declarative surface for defining physical systems and particle constraints using the `@physics` attribute. Like `dsys`, it is parsed and expanded directly by the core compiler (`compiler/src/physics_dsl.flow`) into standard struct definitions and update loops.

The DSL is meant for declarative, easily readable descriptions of particle systems and simple physics constraints rather than a full rigid-body solver.

## Current capabilities

The `@physics` block translates declarative statements into standard `struct` definitions, initialization functions, and update routines.
- **Entities**: Defining what a particle is using `entity Particle { ... }` with fields and default values.
- **Constants**: Specifying physical constants like `const gravity = Vec2(0, 200)`.
- **Rules**: Applying operations to particles at each timestep. Operations directly mutate variables like `velocity += gravity * dt`.
- **Constraints**: Enforcing boundaries `constraint "name" when <condition>: ...`.
- **Interactions**: Defining behavior between pairs of particles with `interact "name" between a, b when <condition>: ...`.

See [`examples/physics/particles.physics`](../../examples/physics/particles.physics) for an example.

## What it is NOT

The physics DSL is intentionally limited to particle-level constraint programming and basic Euler integration.

- **Not a generic rigid body engine**: Flow provides no native continuous collision detection, 3D polygon meshes, or complex joint solvers via `@physics`. You should write those explicitly (like `physics3d.flow`).
- **No spatial partitioning out of the box**: Currently, the generated interaction loops are naive $O(N^2)$ loops.
- **No symplectic integrators yet**: The standard expanded rules use simple semi-implicit Euler integration (`v += a*dt`, `p += v*dt`).
