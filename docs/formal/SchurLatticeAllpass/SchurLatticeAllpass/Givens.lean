import Mathlib.Algebra.Order.Ring.Abs
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.Matrix.Defs
import SchurLatticeAllpass.Basic

/-!
# Givens rotations and orthogonal colligations
-/

namespace SchurLatticeAllpass

open Matrix

/-- Planar Givens rotation `G(c,s) = ![![c,-s],[s,c]]`. -/
def givens₂ (c s : ℝ) : Matrix (Fin 2) (Fin 2) ℝ :=
  !![c, -s; s, c]

/-- Cosine/sine parametrization from a bounded reflection `k = sin θ`. -/
noncomputable def reflectionToTrig (k : ℝ) (_hk : |k| < 1) : ℝ × ℝ :=
  (Real.sqrt (1 - k ^ 2), k)

lemma givens₂_orthogonal {c s : ℝ} (h : c ^ 2 + s ^ 2 = 1) :
    givens₂ c s * (givens₂ c s).transpose = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [givens₂, Matrix.mul_apply, Fin.sum_univ_two, Matrix.transpose_apply]
  all_goals ring_nf <;> linarith [h]

lemma reflection_givens_orthogonal {k : ℝ} (hk : |k| < 1) :
    let (c, s) := reflectionToTrig k hk
    givens₂ c s * (givens₂ c s).transpose = 1 := by
  dsimp [reflectionToTrig]
  have hk' : k ^ 2 < 1 := (sq_lt_one_iff_abs_lt_one k).mpr hk
  have hc : (Real.sqrt (1 - k ^ 2)) ^ 2 + k ^ 2 = 1 := by
    rw [Real.sq_sqrt (sub_nonneg.mpr (le_of_lt hk'))]
    ring
  exact givens₂_orthogonal hc

/-- Product of orthogonal matrices is orthogonal (colligation composition). -/
theorem orthogonal_mul {n : ℕ} [NeZero n] (A B : Matrix (Fin n) (Fin n) ℝ)
    (hA : A * A.transpose = 1) (hB : B * B.transpose = 1) :
    (A * B) * (A * B).transpose = 1 := by
  calc
    (A * B) * (A * B).transpose = A * B * B.transpose * A.transpose := by
      simp [Matrix.mul_assoc, Matrix.transpose_mul]
    _ = A * (B * B.transpose) * A.transpose := by rw [← Matrix.mul_assoc]
    _ = A * 1 * A.transpose := by rw [hB]
    _ = A * A.transpose := by simp [Matrix.mul_assoc]
    _ = 1 := hA

end SchurLatticeAllpass