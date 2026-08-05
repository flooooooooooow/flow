import Lake
open Lake DSL

package «SchurLatticeAllpass» where
  leanOptions := #[
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩
  ]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.30.0-rc2"

@[default_target]
lean_lib «SchurLatticeAllpass» where
  roots := #[`SchurLatticeAllpass]