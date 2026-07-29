import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.Matrix.Defs
import SchurLatticeAllpass.Basic

/-!
# Finite controllability basis and observer map
-/

namespace SchurLatticeAllpass

variable {n : ℕ} [NeZero n]

/-- Standard colligation input `B = e₁`. -/
def colligationInput : Matrix (Fin n) (Fin 1) ℝ :=
  fun i _ => if i = 0 then 1 else 0

/-- Column `i` of the finite controllability matrix: `A^i B`. -/
noncomputable def controllabilityColumn (A : Matrix (Fin n) (Fin n) ℝ) (i : ℕ) :
    Matrix (Fin n) (Fin 1) ℝ :=
  (A ^ i) * colligationInput

/-- Finite controllability matrix `𝒞 = [B AB … A^{n-1}B]`. -/
noncomputable def controllabilityMatrix (A : Matrix (Fin n) (Fin n) ℝ) :
    Matrix (Fin n) (Fin n) ℝ :=
  Matrix.of fun row col => (controllabilityColumn A col row 0)

/-- Map canonical numerator observer through the finite controllability basis. -/
noncomputable def observerMap (A : Matrix (Fin n) (Fin n) ℝ) (cCan : Fin n → ℝ) :
    Fin n → ℝ :=
  fun i =>
    (Finset.univ : Finset (Fin n)).sum fun j =>
      cCan j * controllabilityMatrix A j i

end SchurLatticeAllpass