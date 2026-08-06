# Evolutionary Biology Gallery

Seven population-genetics simulations written in Flow. Every clip below is
recorded from the real compiled program through the headless recorder. Every
program also measures the thing it is demonstrating, prints the measurement
beside the closed form, and returns a nonzero exit code if the comparison
fails, so these are regression tests that happen to draw pictures.

This is the biology half of [VISION.md](../vision.md): a system that evolves
through time is better written as a statement of how it evolves than as a
loop that steps it. The domain README lives at
[examples/evoleco](../../examples/evoleco/README.md).

Run any example natively:

```bash
./flow gfx examples/evoleco/<name>.flow
```

Record one headlessly, no display needed:

```bash
FLOW_HOST=python ./flow record examples/evoleco/wright_fisher.flow \
  --frames 120 --skip 2 --gif docs/demos/evoleco/wright_fisher.gif
```

Regenerate every GIF on this page:

```bash
python3 scripts/record_demos.py --group evoleco
```

`./flow run` does not link a graphics backend, so it cannot build these; use
`record` for the headless run and `gfx` for the window. The measurements are
all made before the window opens and do not depend on how many frames are
recorded.

## Population genetics

| | | |
|:---:|:---:|:---:|
| ![Wright-Fisher](./evoleco/wright_fisher.gif) | ![Hardy-Weinberg](./evoleco/hardy_weinberg.gif) | ![Selection locus](./evoleco/selection_locus.gif) |
| **Wright-Fisher**. Neutral drift; H decays as (1-1/(2N))^t and absorption tracks 4 N ln 2<br>`wright_fisher.flow` | **Hardy-Weinberg**. Genotype bars recover p^2 : 2pq : q^2 in one generation<br>`hardy_weinberg.flow` | **Selection locus**. Allele frequency follows the discrete logistic closed form<br>`selection_locus.flow` |
| ![Mutation-selection](./evoleco/mutation_selection.gif) | ![Bottleneck](./evoleco/bottleneck.gif) | ![Island migration](./evoleco/island_migration.gif) |
| **Mutation-selection**. Deleterious allele equilibrates near u/s<br>`mutation_selection.flow` | **Bottleneck**. Census crash; heterozygosity matches the product over N_t<br>`bottleneck.flow` | **Island migration**. Fst settles near 1/(1+4 N m K/(K-1))<br>`island_migration.flow` |
| ![Moran process](./evoleco/moran_process.gif) | | |
| **Moran process**. Neutral fixation probability is 1/N; selective rho gated too<br>`moran_process.flow` | | |
