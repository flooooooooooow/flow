# Numerical Gallery

Gated numerical demos. Every clip is recorded from the real compiled program.
Measurements print before the window opens and gate the exit code.

## Fast multipole method

| | |
|:---:|:---:|
| ![Adaptive FMM](./numerical/fmm_adaptive.gif) | |
| **Adaptive FMM** (Carrier-Greengard-Rokhlin 1988). 2D Coulomb FMM on an adaptive quadtree; particles colored by charge, leaf boxes outlined. Gates accuracy vs direct, bit-identical replay, FMM vs direct timing, and adaptive depth for clustered vs uniform.<br>`examples/numerical/fmm_adaptive.flow` | |

Library: [`lib/stdlib/fmm2d.flow`](../library/fmm2d.md).

```bash
FLOW_HOST=python ./flow gfx examples/numerical/fmm_adaptive.flow
FLOW_HOST=python ./flow record examples/numerical/fmm_adaptive.flow \
  --frames 4 --out /tmp/fmm
python3 scripts/record_demos.py --group numerical
```
