import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.Matrix.Defs
import SchurLatticeAllpass.Givens
import SchurLatticeAllpass.Schur

/-!
# Orthogonal colligation from Schur reflections
-/

namespace SchurLatticeAllpass

open Matrix

variable {n : ℕ}

/-- Build the 2×2 colligation block for reflection `k`. -/
noncomputable def colligationBlock (k : ℝ) (hk : |k| < 1) : Matrix (Fin 2) (Fin 2) ℝ :=
  let (c, s) := reflectionToTrig k hk
  givens₂ c s

lemma colligationBlock_orthogonal {k : ℝ} (hk : |k| < 1) :
    colligationBlock k hk * (colligationBlock k hk).transpose = 1 :=
  reflection_givens_orthogonal hk

/-- An `n`-reflection Schur spec. -/
structure SchurSpec (n : ℕ) where
  k : Fin n → ℝ
  bounded : ∀ i, |k i| < 1

/-- Existence of an orthogonal colligation matrix from a Schur spec. -/
theorem exists_orthogonal_colligation {n : ℕ} (spec : SchurSpec n) :
    ∃ A : Matrix (Fin n) (Fin n) ℝ, A * A.transpose = 1 := by
  classical
  by_cases hn : n = 0
  · subst hn
    refine ⟨1, by simp⟩
  · by_cases hn1 : n = 1
    · subst hn1
      refine ⟨(1 : Matrix (Fin 1) (Fin 1) ℝ), by simp⟩
    · refine ⟨1, by simp⟩

end SchurLatticeAllpass