# SchurLatticeAllpass (Lean 4 / Mathlib)

Formal core for the Schur-lattice all-pass synthesis pipeline.

## Build

```bash
cd docs/formal/SchurLatticeAllpass
lake update   # first time only (downloads Mathlib)
lake build
```

## Main theorems

| File | Result |
|------|--------|
| `Givens.lean` | `givens₂_orthogonal`, `orthogonal_mul` |
| `Schur.lean` | `reflection_stable_error`, `reflection_bounded_iff_stable` |
| `Colligation.lean` | `exists_orthogonal_colligation` |
| `Controllability.lean` | `observerMap` via finite $\mathcal{C}$ |
| `AllPass.lean` | `schur_lattice_allpass_pipeline`, `modulation_stable` |

Companion paper: `docs/research/schur_lattice_allpass/schur_lattice_allpass.tex`