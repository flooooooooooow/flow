# examples/evoleco: evolutionary biology, running live

Fifteen graphics programs about how populations change. Each one starts from
a known initial state (allele frequencies, a mixed strategy field, an epidemic
seed) and ends somewhere the theory predicts, with a measured quantity gated
against a closed form or a published number. They are regression tests that
happen to draw pictures — the same evidence standard as
[`morphogenesis/`](../morphogenesis/README.md) and [`neuro/`](../neuro/README.md).

This is the biology half of Flow's founding claim in [VISION.md](../../VISION.md):
a system that evolves through time is better written as a statement of how it
evolves than as a loop that steps it. Evolutionary biologists already think in
those terms (allele-frequency dynamics, replicator equations, coalescents);
here the equations *are* the program.

Recorded clips live in the
[evoleco gallery](../../docs/demos/evoleco.md).

## Population genetics

| Example | Model | What it proves |
|---|---|---|
| [`wright_fisher.flow`](wright_fisher.flow) | Wright-Fisher drift | Fixation time scales as 4 Ne; heterozygosity decays as (1 - 1/(2N))^t |
| [`hardy_weinberg.flow`](hardy_weinberg.flow) | Random mating | Genotype frequencies recover p^2 : 2pq : q^2 in one generation |
| [`selection_locus.flow`](selection_locus.flow) | Viability selection | Allele frequency follows the logistic closed form |
| [`mutation_selection.flow`](mutation_selection.flow) | Mutation-selection balance | Equilibrium p* = u/s for a deleterious allele |
| [`bottleneck.flow`](bottleneck.flow) | Census crash | Heterozygosity loss matches the product of (1 - 1/(2Nt)) |
| [`island_migration.flow`](island_migration.flow) | Wright island model | Fst settles near 1/(1 + 4 N m) |
| [`moran_process.flow`](moran_process.flow) | Moran birth-death | Neutral fixation probability is exactly 1/N |

## Evolutionary dynamics and games

| Example | Model | What it proves |
|---|---|---|
| [`fitness_landscape.flow`](fitness_landscape.flow) | NK rugged landscape | Adaptive walks reach a local peak; path length gated |
| [`quasispecies.flow`](quasispecies.flow) | Eigen quasispecies | Error threshold at u_c = ln(s)/(L-1) |
| [`hawk_dove.flow`](hawk_dove.flow) | Maynard Smith ESS | Mixed ESS at V/C; invader dies out |
| [`spatial_pd.flow`](spatial_pd.flow) | Spatial Prisoner's Dilemma | Cooperation persists above the mean-field threshold |
| [`rock_paper_scissors.flow`](rock_paper_scissors.flow) | Spatial RPS | Cyclic dominance; coexistence against mean-field extinction |
| [`replicator_dynamics.flow`](replicator_dynamics.flow) | Replicator equation | Three-strategy simplex converges to the Nash rest point |

## Ecology (visual companions)

| Example | Model | What it proves |
|---|---|---|
| [`lotka_volterra_gfx.flow`](lotka_volterra_gfx.flow) | Predator-prey | First integral conserved; Volterra averages |
| [`sir_spatial.flow`](sir_spatial.flow) | Spatial SIR | Final size vs the final-size equation |

## Running them

```bash
./flow gfx examples/evoleco/wright_fisher.flow
./flow record examples/evoleco/wright_fisher.flow --frames 90 --gif docs/demos/evoleco/wright_fisher.gif
python3 scripts/record_demos.py --group evoleco
```

Every example labels itself on screen (title, parameters, live measurement).
Number keys switch presets, `R` reseeds, `P` pauses, Esc quits. Seeding is a
fixed LCG, so a preset replays identically.
