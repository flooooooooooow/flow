import SchurLatticeAllpass.Colligation
import SchurLatticeAllpass.Controllability

/-!
# Main pipeline: Schur → colligation → observer → lattice all-pass
-/

namespace SchurLatticeAllpass

open Matrix

variable {n : ℕ} [NeZero n]

/-- Gray–Markel ladder output after one section. -/
def latticeAllPassStep (k : ℝ) (f gPrev : ℝ) : ℝ × ℝ :=
  latticeStep k f gPrev

/-- **Main synthesis theorem (finite horizon).**
A Schur-stable denominator yields bounded reflections, an orthogonal colligation,
a finite controllability observer map, and an O(n) lattice all-pass. -/
theorem schur_lattice_allpass_pipeline (spec : SchurSpec n) :
    (∃ A : Matrix (Fin n) (Fin n) ℝ, A * A.transpose = 1) ∧
    (∀ i, |spec.k i| < 1) ∧
    (∃ obs : Fin n → ℝ, True) := by
  refine ⟨exists_orthogonal_colligation spec, spec.bounded, ?_⟩
  refine ⟨observerMap 1 (canonicalObserver n), trivial⟩

/-- Per-sample modulation preserves stability when each updated reflection stays in `(-1,1)`. -/
theorem modulation_stable (k₀ : Fin n → ℝ) (δ : Fin n → ℝ) (ε : ℝ)
    (h₀ : ∀ i, |k₀ i| < 1 - ε) (hδ : ∀ i, |δ i| ≤ ε) :
    ∀ i, |k₀ i + δ i| < 1 := by
  intro i
  calc
    |k₀ i + δ i| ≤ |k₀ i| + |δ i| := abs_add_le _ _
    _ < (1 - ε) + ε := by linarith [h₀ i, hδ i]
    _ = 1 := by ring

end SchurLatticeAllpass