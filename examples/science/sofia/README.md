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

## Native kernels and their contracts

| Numerical component | Native Flow module | Self-check |
|---|---|---|
| Uniform grids, particle-domain and field descriptors, staggered coordinates | `lib/stdlib/science/sofia_domain.flow` | `tests/lang/test_sofia_domain.flow` |
| Conservative 2D shallow-water equations | `lib/stdlib/science/sofia_shallow_water.flow` | `tests/lang/test_sofia_shallow_water.flow` |
| Hydrostatic bed reconstruction, wet/dry states, reflecting walls and Manning friction | `lib/stdlib/science/sofia_shallow_water.flow` | `tests/lang/test_sofia_sw_lake_at_rest.flow`, `test_sofia_sw_dry_bed.flow`, `test_sofia_sw_manning_precision.flow` |
| Fused D3Q19 periodic pull-stream / BGK collision | `lib/stdlib/science/sofia_lattice_boltzmann.flow` | `tests/lang/test_sofia_lattice_boltzmann.flow` |
| Masked bounce-back, Smagorinsky relaxation and Guo forcing | `lib/stdlib/science/sofia_lattice_boltzmann.flow` | `tests/lang/test_sofia_taylor_green.flow` exercises the LES entry point with zero Smagorinsky coefficient, zero forcing and no obstacles; it does not validate the nonzero options |
| 3D periodic pressure-Poisson projection (Jacobi) | `lib/stdlib/science/sofia_incompressible.flow` | `tests/lang/test_sofia_incompressible.flow` |
| 3D periodic momentum advection/diffusion | `lib/stdlib/science/sofia_incompressible.flow` | `tests/lang/test_sofia_navier_stokes.flow` |

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
./flow run tests/lang/test_sofia_navier_stokes.flow
```

Run these contracts with `./flow test-lang` (or pass individual test paths).
Read the actual check results for the revision being evaluated. Numerical
smoke tests are not independent benchmark validation. The Taylor–Green test
checks short, small-grid kinetic-energy decay in `f64`; it does not establish
the showcase's viscosity-error target in both precisions, long-run stability,
or GPU performance.

## Relationship to Fermioniq's three reference cases

### Waal River / `free_surface`

The published case uses a 1700 × 340 grid at 50 m, discharge Q=10,165 m³/s,
7,000 passive tracers, and reference comparison to a validated rerun and
D-Flow FM. Flow provides both a flat-bed periodic Rusanov step and
`sofia_sw_step_with_bed`, with hydrostatic reconstruction, wet/dry handling,
reflecting perimeter walls and semi-implicit Manning friction. Lake-at-rest,
dry-front mass/non-negativity and shallow-water friction regressions exercise
synthetic cases. It does *not* supply the Waal's DEM/bathymetry, calibrated
inflow/outflow hydrograph, validated flood map or georeferenced tracers.
Closed reflecting walls cannot represent the requested river discharge.

To reproduce: validate bed/wet-dry/friction behavior under refinement, add
discharge boundaries, terrain ingestion and tracer advection, and compare
depth, velocity and flood extent with pinned source data and an independently
obtained reference at the stated resolution.

### Amsterdam Science Park / `lattice_boltzmann`

The published case uses D3Q19 LES on roughly 80 M cells, 2 m spacing,
3D BAG building heights, and an NVIDIA GH200, validated with Taylor–Green
viscosity within 0.5%, reported peak Mach 0.12 and mass drift 9e-5.
Flow supplies the periodic BGK conservation core and
`sofia_lbm_d3q19_les_step` with solid-mask bounce-back, Smagorinsky relaxation
and Guo forcing. Those code paths do not by themselves validate obstacle
flow or turbulence. It does *not* yet supply the showcase's inlet/outlet
and wall model, multi-relaxation-time collision, GH200 dispatch or 3D BAG import.
Those are nontrivial accuracy and performance dependencies, not rendering
details.

To reproduce: load obstacle masks at native physical coordinates, validate
nonzero LES/forcing and wall paths against channel/obstacle references, add
geospatial geometry and inlet/outlet conditions, qualify both precisions,
and establish GPU lowering, long-run mass/Mach and convergence gates.

### AhmedML aerodynamic body / `incompressible_flow`

The published case uses 56 M cells, 4 mm near-body resolution, wall-modelled
LES, a 61° AhmedML rear slant, and reported mean drag coefficient 0.231
versus reference 0.238. Flow supplies periodic momentum advection/diffusion
and a pressure-Poisson projection. This is not the AhmedML wall-modelled LES
configuration. There are no solid-body boundaries, wall-modelled LES,
boundary-layer mesh grading or drag integration; the Poisson solver is a
small-grid Jacobi baseline.

To reproduce: implement wall-modelled LES, cut cells or immersed boundaries, scalable Poisson
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

The domain/field descriptors and coordinate helpers are a foundation, not a
symbolic field system: memory and staggering are integer metadata, and the
API does not enforce unit/location compatibility or perform host/device
transfers. A typed Flow expression/solver IR and its semantic contracts
remain separate work under #1650.

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
