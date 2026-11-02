# Sofia-class scientific computing in Flow — initial native kernels

This directory begins an **independent Flow-native implementation** of the
scientific-computing capabilities demonstrated by Fermioniq's Sofia. It is
**not Fermioniq Sofia**, does not include their engine's source, and does not
claim to reproduce their three showcase movies or results yet.

Sources and targets:
- [Sofia docs (public)](https://github.com/fermioniq/sofia-docs) — documented
  domains, fields, symbolic PDEs, discretisation, IR, time integrators and code generation.
- [Sofia showcase](https://fermioniq.github.io/sofia-showcase-page/) — three
  independent numerical reference cases (8 October 2026).
- Existing Flow scientific syntax: `examples/evolution/heat_diffusion.flow`,
  `docs/language/physics-dsl.md`, and `lib/stdlib/dynamics/pde.flow`.

## Implemented in this PR

| Numerical component | Native Flow module | Self-check |
|---|---|---|
| Conservative 2D shallow-water equations | `lib/stdlib/science/sofia_shallow_water.flow` | `tests/lang/test_sofia_shallow_water.flow` |
| Fused D3Q19 periodic pull-stream / BGK collision | `lib/stdlib/science/sofia_lattice_boltzmann.flow` | `tests/lang/test_sofia_lattice_boltzmann.flow` |
| 3D periodic pressure-Poisson projection (Jacobi) | `lib/stdlib/science/sofia_incompressible.flow` | `tests/lang/test_sofia_incompressible.flow` |

These are standalone numerical kernels with no Python, SymPy, NumPy, Warp,
Blender or external solver dependencies. All fields use contiguous caller-owned
`f64` arrays; distinct input and output buffers are required. CPU operation
is intended in this initial slice. The checked-in regression programs check
mass conservation, non-negative depths, lattice mass, and pressure-projection
divergence reduction. Run with:

```text
./flow run tests/lang/test_sofia_shallow_water.flow
./flow run tests/lang/test_sofia_lattice_boltzmann.flow
./flow run tests/lang/test_sofia_incompressible.flow
```

Until the Flow CI checks pass, compilation and runtime correctness remain
**unverified**. Numerical smoke tests are not independent benchmark validation.

## Relationship to Fermioniq's three reference cases

### Waal River / `free_surface`

The published case uses a 1700 × 340 grid at 50 m, discharge Q=10,165 m³/s,
7,000 passive tracers, and reference comparison to a validated rerun and
D-Flow FM. Our Flow kernel currently solves **flat-bed, strictly-wet,
periodic** 2D shallow-water equations using first-order Rusanov fluxes.
It proves conservation only on a synthetic wave. It does *not* model the
Waal's DEM/bathymetry, flooding, inflow/outflow hydrograph, bottom friction,
wetting/drying, or georeferenced tracer advection.

To reproduce that case: add well-balanced bed-source coupling, hydrostatic
reconstruction, robust dry-state transitions, Manning friction, discharge
boundaries, terrain ingestion, high-resolution tracer advection, and
convergence tests at the original geometry and grid resolution.

### Amsterdam Science Park / `lattice_boltzmann`

The published case uses D3Q19 LES on roughly 80 M cells, 2 m spacing,
3D BAG building heights, and an NVIDIA GH200, validated with Taylor–Green
viscosity within 0.5%, reported peak Mach 0.12 and mass drift 9e-5.
Our Flow D3Q19 kernel implements the **single-relaxation-time BGK**
conservation core with periodic streaming. It does *not* yet implement
obstacle bounce-back, inlet/outlet, wall functions, local eddy viscosity,
multi-relaxation-time collision, GH200 kernel dispatch or the 3D BAG import.
Those are nontrivial accuracy and performance dependencies, not rendering
details.

To reproduce: implement obstacle masks at native 2 m coordinates, stable LES
collision models, geospatial geometry loading, physical boundary conditions,
backend-specific GPU kernel lowering, long-run stability gates and precise
Taylor–Green / channel-flow manufactured benchmarks, before a production run.

### AhmedML aerodynamic body / `incompressible_flow`

The published case uses 56 M cells, 4 mm near-body resolution, wall-modelled
LES, a 61° AhmedML rear slant, and reported mean drag coefficient 0.231
versus reference 0.238. Our Flow module is a periodic-grid **pressure
projection primitive**, not a full Navier–Stokes or LES solver.
There are no solid walls, convective/diffusive momentum step, viscosity
model, boundary-layer resolution, mesh adaptation, or drag integration.

To reproduce: implement conservative advection, viscous stresses,
wall-modelled LES, cut cells or immersed boundaries, scalable Poisson
multigrid, near-body mesh grading, traction/pressure drag integration,
and convergence studies with the AhmedML geometry and reference conditions.

## From this numerical core to a full Flow-native Sofia equivalent

The intended public library should own the **entire** computational path
in Flow, not shell out to Python: typed domain and coordinates (structured
and particle), symbolic fields and staggering, field algebra and
dimension/unit checking, discrete differential operators and
interpolation, explicit/implicit time integration, boundary-condition IR,
automatic differentiation/Jacobians, transformations, geometry/SDF, solver
composition, a non-Python staging/optimisation IR, MLIR/LLVM and GPU codegen,
runtime memory ownership and scheduling, deterministic output/checkpoint
formats, and scientific validation.

Important semantic decisions: define discrete conservation and boundary
operators before syntax sugar; reject inconsistent locations/units rather
than silently interpolating; keep solver state distinct from render state;
force explicit tolerances, precision and timestep constraints; attach
machine-readable conservation and convergence tests to each reference case.

### Acceptance gates

1. Flow source and every documented example compile under the checked-in
   self-hosted Flow compiler on Linux and macOS.
2. Small-grid conservation, manufactured-solution, grid-convergence,
   obstacle, turbulence and shock/dry-front tests pass.
3. GPU results agree with CPU within declared precision tolerances;
   float32/float64 trajectories are separately qualified.
4. All required upstream public input datasets, licences, provenance,
   runtime parameters and reproducible seeds are versioned or pinned.
5. The three complete reference geometries and regimes are independently
   validated against their published numerical checks, with plotted error
   history and hardware/resource measurements.
6. Only after numerical parity: reproduce the particle/streamline
   visualization, geospatial alignment, and movie export.

For the Sofia implementation details not published in the docs, this
project must use independently specified methods and disclose differences.
No claim of full Sofia API parity or GH200 benchmark reproduction should
be made from these initial kernels.
