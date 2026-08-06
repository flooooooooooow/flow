# examples/morphogenesis: pattern and growth, running live

Real-time graphics programs about how form appears. Each one starts from
something featureless (uniform noise, a single seed, a random mixture) and
ends somewhere structured, with nothing in the source describing the
structure. The rule is written down; the shape is what the rule does.

Recorded clips live in the
[morphogenesis gallery](../../docs/demos/morphogenesis.md).

This is [VISION.md](../../VISION.md) as a picture. Flow's founding claim is
that the primary abstraction of a program should be **the evolution of a
system through time** rather than a sequence of instructions, and that the
mathematical model should be the executable. Morphogenesis is the cleanest
argument available for that claim: the interesting object is never the state
at any one instant, it is the trajectory, and the models are short enough
that the whole of each one fits in a comment at the top of the file.

Wherever the model is continuous, the dynamics are stated as a `flow` block
with `evolves as` and lowered by the compiler to a `_step` function, exactly
as in [`examples/evolution`](../evolution/):

```flow
flow GrayScottCell {
    state u : f64 = 1.0
    state v : f64 = 0.0
    param lap_u : f64 = 0.0
    ...
    solver { dt 1 s  method euler }

    u evolves as du * lap_u - u * v * v + feed * (1.0 - u)
    v evolves as dv * lap_v + u * v * v - (feed + kill) * v
}
```

The grid loop hands each cell its own laplacian and steps it. Nothing else
in `gray_scott.flow` knows what a Turing pattern is.

Every example labels itself on screen with `stdlib/text.flow`: title, the
parameters currently in force, and a live measurement of the phenomenon
being claimed (fractal dimension, surface width, interface length, options
remaining, per cent of cell contacts between unlike types). Number keys
switch presets, `R` reseeds, `P` pauses, `Esc` quits. Seeding is a fixed LCG,
so every run of a preset is the same run.

## Reaction-diffusion and continuous fields

| Example | Phenomenon | Model | Run |
|---|---|---|---|
| [`gray_scott.flow`](gray_scott.flow) | Solitons, mitosis, coral, mazes, holes | Gray-Scott two-species reaction-diffusion | `./flow gfx examples/morphogenesis/gray_scott.flow` |
| [`turing_spots.flow`](turing_spots.flow) | Hexagonal lattice of activator peaks | Gierer-Meinhardt activator-inhibitor | `./flow gfx examples/morphogenesis/turing_spots.flow` |
| [`turing_stripes.flow`](turing_stripes.flow) | The same system as ridges, not dots | Gierer-Meinhardt with activator saturation | `./flow gfx examples/morphogenesis/turing_stripes.flow` |
| [`belousov.flow`](belousov.flow) | Four interlocking rotating spiral waves | Barkley two-variable excitable medium | `./flow gfx examples/morphogenesis/belousov.flow` |
| [`swift_hohenberg.flow`](swift_hohenberg.flow) | Rolls with grain boundaries, or peaks | Swift-Hohenberg, a fourth-order pattern equation | `./flow gfx examples/morphogenesis/swift_hohenberg.flow` |
| [`cahn_hilliard.flow`](cahn_hilliard.flow) | Bicontinuous domains coarsening forever | Cahn-Hilliard conserved (Model B) dynamics | `./flow gfx examples/morphogenesis/cahn_hilliard.flow` |
| [`brusselator.flow`](brusselator.flow) | Hexagonal lattice at the predicted lambda | Prigogine-Lefever autocatalytic RD | `./flow gfx examples/morphogenesis/brusselator.flow` |
| [`gierer_meinhardt.flow`](gierer_meinhardt.flow) | Activator-inhibitor spots; wavelength vs k_max | Gierer-Meinhardt without saturation | `./flow gfx examples/morphogenesis/gierer_meinhardt.flow` |
| [`schnakenberg.flow`](schnakenberg.flow) | Cubic autocatalysis; wavelength vs k_max | Schnakenberg RD | `./flow gfx examples/morphogenesis/schnakenberg.flow` |
| [`fitzhugh_waves.flow`](fitzhugh_waves.flow) | Spiral tips with measured period | Barkley / FitzHugh-Nagumo 2D medium | `./flow gfx examples/morphogenesis/fitzhugh_waves.flow` |
| [`kuramoto_sivashinsky.flow`](kuramoto_sivashinsky.flow) | Spatiotemporal chaos; dissipation band | 1D Kuramoto-Sivashinsky | `./flow gfx examples/morphogenesis/kuramoto_sivashinsky.flow` |
| [`allen_cahn.flow`](allen_cahn.flow) | Droplet shrinks as R^2 = R0^2 - 2t | Allen-Cahn mean-curvature flow | `./flow gfx examples/morphogenesis/allen_cahn.flow` |
| [`heat_morph.flow`](heat_morph.flow) | Noise dissolves, boundaries sharpen | Perona-Malik anisotropic diffusion | `./flow gfx examples/morphogenesis/heat_morph.flow` |

## Growth and aggregation

| Example | Phenomenon | Model | Run |
|---|---|---|---|
| [`dla.flow`](dla.flow) | A fractal dendrite, D near 1.65 | Diffusion-limited aggregation | `./flow gfx examples/morphogenesis/dla.flow` |
| [`eden_growth.flow`](eden_growth.flow) | Compact colony with a rough KPZ front | Eden cluster, live surface width | `./flow gfx examples/morphogenesis/eden_growth.flow` |
| [`branching_vessels.flow`](branching_vessels.flow) | A leaf with midrib and side veins | Space colonization venation | `./flow gfx examples/morphogenesis/branching_vessels.flow` |
| [`lsystem_plant.flow`](lsystem_plant.flow) | A shoot extending and branching in order | Stochastic L-system, turtle over a growing prefix | `./flow gfx examples/morphogenesis/lsystem_plant.flow` |
| [`lsystem_tree.flow`](lsystem_tree.flow) | A projected oak whose tips move in wind | Recursive 3D branching grammar | `./flow gfx examples/morphogenesis/lsystem_tree.flow` |
| [`coral_ballistic.flow`](coral_ballistic.flow) | Porous columnar reef, fill under 0.5 | Ballistic deposition, shadowing instability | `./flow gfx examples/morphogenesis/coral_ballistic.flow` |
| [`phase_field_dendrite.flow`](phase_field_dendrite.flow) | Six-fold dendrite; tip speed and arm count | Kobayashi anisotropic phase field | `./flow gfx examples/morphogenesis/phase_field_dendrite.flow` |
| [`bz_3d_slice.flow`](bz_3d_slice.flow) | Scroll wave; period from midplane probe | Barkley medium in a 32^3 cube | `./flow gfx examples/morphogenesis/bz_3d_slice.flow` |
| [`laplacian_growth.flow`](laplacian_growth.flow) | Dielectric-breakdown cluster; D_Rg near 1.7 | Niemeyer DBM with eta | `./flow gfx examples/morphogenesis/laplacian_growth.flow` |
| [`viscous_fingering.flow`](viscous_fingering.flow) | Single finger; w/W near 1/2 | Saffman-Taylor channel proxy | `./flow gfx examples/morphogenesis/viscous_fingering.flow` |
| [`mycelium.flow`](mycelium.flow) | Colony; hyphal length grows under depletion | Tip branching on a nutrient field | `./flow gfx examples/morphogenesis/mycelium.flow` |

## Cellular and discrete

| Example | Phenomenon | Model | Run |
|---|---|---|---|
| [`cyclic_ca.flow`](cyclic_ca.flow) | Noise, then debris, then spiral cores | Cyclic cellular automaton | `./flow gfx examples/morphogenesis/cyclic_ca.flow` |
| [`life_variants.flow`](life_variants.flow) | Three characters from three B/S rules | Conway, HighLife, Day-and-Night | `./flow gfx examples/morphogenesis/life_variants.flow` |
| [`hexagonal_ca.flow`](hexagonal_ca.flow) | A six-fold dendritic snow crystal | Reiter's snowflake automaton on a hex lattice | `./flow gfx examples/morphogenesis/hexagonal_ca.flow` |
| [`wfc_growth.flow`](wfc_growth.flow) | A continuous circuit filling out from a seed | Wave function collapse over a 16-tile pipe set | `./flow gfx examples/morphogenesis/wfc_growth.flow` |

## Biological pattern

| Example | Phenomenon | Model | Run |
|---|---|---|---|
| [`slime_mold.flow`](slime_mold.flow) | An arterial transport network with junctions | Physarum agents over a shared trail map | `./flow gfx examples/morphogenesis/slime_mold.flow` |
| [`cell_sorting.flow`](cell_sorting.flow) | A mixture separating into tissue layers | Differential adhesion, Metropolis exchange | `./flow gfx examples/morphogenesis/cell_sorting.flow` |
| [`somite_clock.flow`](somite_clock.flow) | Equal body segments laid down one at a time | Clock and wavefront somitogenesis | `./flow gfx examples/morphogenesis/somite_clock.flow` |

## Two examples worth reading side by side

`turing_spots.flow` and `turing_stripes.flow` are the same equations with one
coefficient changed. Run them in sequence. Nothing about the grid, the seed,
the integrator or the diffusion ratio differs; the saturation constant kappa
moves the animal from leopard to zebra. That is the point Turing's 1952 paper
was making, and it is easier to believe when the only difference on screen is
one number in the header.

## Recording frames

Every example runs headless, so a still or a GIF comes out of the same
compiled program:

```bash
./flow record examples/morphogenesis/gray_scott.flow \
  --frames 240 --skip 4 --out /tmp/frames \
  --gif docs/demos/morphogenesis/gray_scott.gif
```

`--keys "1-3:19"` holds a key over a range of frames, which is how the preset
variants are captured without a display. `--skip N` keeps every Nth presented
frame; `--fps`, `--stride` and `--width` size the GIF.

The committed clips come from `python3 scripts/record_demos.py --group
morphogenesis`, which carries a tuned frame budget per example. See the
[gallery](../../docs/demos/morphogenesis.md) for how those budgets were chosen.

## Notes on the numerics

The fourth-order models (`swift_hohenberg`, `cahn_hilliard`) have a much
smaller stable timestep than the second-order ones, and the activator-
inhibitor models need a large diffusion ratio, which also costs timestep.
Each file states its dt, its stability condition and how many steps it takes
per displayed frame, so the cost of the explicit integrator is visible rather
than hidden. Grids are 128 x 128 unless the model is expensive per cell
(`cell_sorting` is 96 x 96, `wfc_growth` is 48 x 48).
