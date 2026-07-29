# verify.SchurLattice

*Schur–lattice all-pass synthesis: finite controllability route.*

**Source.** Gray–Markel lattice filters; Schur/Levinson stability disk.

## Theorem 1 — Reflection in the stability disk

**Coordinate.** SchurLattice · reflection · bounded coefficient · **Theorem**

> **Goal.** $|k| < 1$ is enforced by `schur_reflection_bounded`.

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Clamp checks reject $k \ge 0.999$ and $k \le -0.999$. | | |
| ② | Hence bounded reflections lie in $(-1,1)$. | ② | $|k| < 1$ |

## Theorem 2 — Givens energy preservation

**Coordinate.** SchurLattice · Givens · orthogonal composition · **Theorem**

> **Goal.** $c^2 + s^2 = 1$ implies orthogonal energy preservation.

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | `givens_energy_preserved` tests $c^2+s^2 \approx 1$. | | |
| ② | Matches Lean `givens₂_orthogonal`. | ② | $GG^\top = I$ |

## Theorem 3 — Finite controllability observer map

**Coordinate.** SchurLattice · controllability · observer lift · **Theorem**

> **Goal.** `schur_lattice_from_denominator` returns reflections and observer taps without infinite Gramian.

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Build $A$ from Givens product, $B=e_1$, $\mathcal{C}=[B,AB,\ldots]$. | | |
| ② | Map $c_{\mathrm{can}}=e_n$ through $\mathcal{C}$. | ② | $w^\top = c_{\mathrm{can}}^\top \mathcal{C}$ |

Lean proofs: `formal/SchurLatticeAllpass/`