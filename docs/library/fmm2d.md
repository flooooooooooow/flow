# fmm2d: adaptive Fast Multipole Method (2D)

`lib/stdlib/fmm2d.flow` implements the Carrier-Greengard-Rokhlin 1988 adaptive
FMM for 2D Coulomb particle interactions in the unit square.

Paper: J. Carrier, L. Greengard, V. Rokhlin, "A Fast Adaptive Multipole
Algorithm for Particle Simulations", SIAM J. Sci. Stat. Comput. 9(4), 1988.
[PDF](https://math.nyu.edu/~greengar/cgr_88.pdf).

Demo: [`examples/numerical/fmm_adaptive.flow`](../../examples/numerical/fmm_adaptive.flow)
· [gallery](../demos/numerical.md).

## Potential

For charges `q_j` at complex positions `z_j`:

```
psi(z) = sum_j q_j * Log(z - z_j)     # complex Log
phi    = Re(psi)                       # physical potential
(Ex, Ey) = (Re(psi'), -Im(psi'))       # Lemma 2.1 force / field
```

Self-interaction is excluded. Relative field error vs the direct sum is

```
E = ||E_fmm - E_dir||_2 / ||E_dir||_2
```

## Expansions

| Op | Role |
|---|---|
| Theorem 2.1 | P2M multipole about a leaf centre |
| Lemma 2.2 | M2M shift child multipole into parent |
| Lemma 2.3 | M2L multipole to local about a distant centre |
| Lemma 2.4 | L2L shift parent local into child |

Truncation order `p` (default 8; paper tables use 17-20 for ~1e-6). Leaf
capacity `s` (default 20-24). Caps: 4096 particles, 16384 boxes, `p <= 16`.

## Adaptive tree

Unit square `[0,1]^2`. Nonempty boxes with more than `s` particles subdivide
into four. Dual-tree walk: well-separated pairs (centre distance at least
`2*(r_A+r_B)` with `r` = half-diagonal) exchange via M2L; nearby leaves use
direct particle-particle. Upward M2M and downward L2L complete Stages 2 and 7
of the paper.

## API

```flow
import "stdlib/fmm2d.flow"

fmm2d_configure(p, s)
fmm2d_set_particles(n, x, y, q)   # copies into module buffers
fmm2d_evaluate()                  # tree + FMM; writes phi, Ex, Ey
fmm2d_direct_evaluate()           # O(N^2) reference buffers
fmm2d_max_rel_error()             # alias of fmm2d_rel_field_error()
fmm2d_potential(i), fmm2d_ex(i), fmm2d_ey(i)
fmm2d_nboxes(), fmm2d_nleaves(), fmm2d_max_level()
fmm2d_box_cx/cy/half/level/leaf(b)
fmm2d_time_ms(), fmm2d_direct_time_ms()
```

## Measured (gated demo)

On a laptop build of `fmm_adaptive.flow` with `p=8`, `s=20`:

| Check | Result |
|---|---|
| N=64 uniform vs direct | relative field error ~ 3e-16 |
| Same-seed replay | bit-identical potentials |
| N=512 uniform | FMM wall time below direct; M2L active |
| Clustered vs uniform | deeper `max_level` (adaptive refinement) |

Paper accuracy at 1e-6 typically needs `p` around 17-20; the demo gates at
1e-3 with `p=8` and documents that choice.
