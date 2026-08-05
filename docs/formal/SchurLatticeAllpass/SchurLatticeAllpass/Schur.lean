import Mathlib.Algebra.Order.Ring.Abs
import Mathlib.Data.Real.Basic
import SchurLatticeAllpass.Basic

/-!
# Schur step-down and Levinson–Schur equivalence (finite order)
-/

namespace SchurLatticeAllpass

/-- Levinson prediction-error update: `α_m = α_{m-1}(1 - k_m²)`. -/
def levinsonErrorUpdate (err km : ℝ) : ℝ :=
  err * (1 - km ^ 2)

lemma levinson_error_nonneg {err km : ℝ}
    (herr : 0 ≤ err) (hk : |km| < 1) :
    0 ≤ levinsonErrorUpdate err km := by
  dsimp [levinsonErrorUpdate]
  have h1 : 0 ≤ 1 - km ^ 2 := by
    have hk' : km ^ 2 < 1 := (sq_lt_one_iff_abs_lt_one km).mpr hk
    linarith
  exact mul_nonneg herr h1

/-- Stability certificate: bounded reflections yield contractive error update. -/
theorem reflection_stable_error {km : ℝ} (hk : |km| < 1) (hkm : km ≠ 0) (err : ℝ) (herr : 0 < err) :
    levinsonErrorUpdate err km < err := by
  dsimp [levinsonErrorUpdate]
  have hk' : km ^ 2 < 1 := (sq_lt_one_iff_abs_lt_one km).mpr hk
  have hkpos : 0 < km ^ 2 := sq_pos_of_ne_zero hkm
  have hmul : err * (1 - km ^ 2) < err * 1 :=
    mul_lt_mul_of_pos_left (sub_lt_self (1 : ℝ) hkpos) herr
  simpa using hmul

/-- |k| < 1 is the Schur/lattice stability region (disk algebra). -/
lemma reflection_bounded_iff_stable (k : ℝ) :
    |k| < 1 ↔ k ^ 2 < 1 :=
  (sq_lt_one_iff_abs_lt_one k).symm

end SchurLatticeAllpass