"""Measurable MLIR optimization pass coverage (#120, #123, #126).

IR-shape assertions always run when mlir-opt can parse FLOW's dialect mix.
"""

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.mlir_optimizer import MLIROptimizer


def _mlir_opt_path():
    path = shutil.which("mlir-opt")
    if path:
        return path
    brew = Path("/opt/homebrew/opt/llvm/bin/mlir-opt")
    return str(brew) if brew.exists() else None


OPT = MLIROptimizer(mlir_opt_path=_mlir_opt_path()) if _mlir_opt_path() else None
needs_opt = pytest.mark.skipif(
    OPT is None or not OPT._toolchain_supports_flow_mlir(),
    reason="compatible mlir-opt not available",
)


SCCP_PROGRAM = """module {
  func.func @main() -> i32 {
    %c2 = arith.constant 2 : i32
    %c3 = arith.constant 3 : i32
    %sum = arith.addi %c2, %c3 : i32
    %c5 = arith.constant 5 : i32
    %eq = arith.cmpi eq, %sum, %c5 : i32
    cf.cond_br %eq, ^bb_ok, ^bb_bad
  ^bb_ok:
    %zero = arith.constant 0 : i32
    func.return %zero : i32
  ^bb_bad:
    %one = arith.constant 1 : i32
    func.return %one : i32
  }
}
"""

INLINE_PROGRAM = """module {
  func.func private @add1(%arg0: i32) -> i32 {
    %c1 = arith.constant 1 : i32
    %0 = arith.addi %arg0, %c1 : i32
    func.return %0 : i32
  }
  func.func @main(%arg0: i32) -> i32 {
    %0 = func.call @add1(%arg0) : (i32) -> i32
    func.return %0 : i32
  }
}
"""

DCE_PROGRAM = """module {
  func.func private @dead_helper(%arg0: i32) -> i32 {
    %c1 = arith.constant 1 : i32
    %0 = arith.addi %arg0, %c1 : i32
    func.return %0 : i32
  }
  func.func @main(%arg0: i32) -> i32 {
    %c0 = arith.constant 0 : i32
    func.return %c0 : i32
  }
}
"""


@needs_opt
class TestMLIROptimizerPasses:
    def test_pipeline_includes_sccp_at_o2(self):
        pipe = OPT.build_pipeline(optimization_level="O2", enable_sccp=True)
        assert "sccp" in pipe

    def test_pipeline_includes_dce_family_at_o2(self):
        pipe = OPT.build_pipeline(optimization_level="O2", enable_dce=True)
        assert "symbol-dce" in pipe or "remove-dead-values" in pipe

    def test_pipeline_includes_inline_at_o2(self):
        pipe = OPT.build_pipeline(optimization_level="O2", enable_inline=True)
        assert "inline" in pipe

    def test_sccp_folds_constant_add(self):
        """#126: SCCP folds constant arithmetic."""
        out, code = OPT.optimize_source(SCCP_PROGRAM, optimization_level="O2")
        assert code == 0
        # After SCCP + canonicalize, the addi of two constants should vanish.
        assert "arith.addi" not in out

    def test_inline_removes_private_call(self):
        """#123: module inline pass removes private helper calls."""
        out, code = OPT.optimize_source(INLINE_PROGRAM, optimization_level="O2")
        assert code == 0
        assert "func.call @add1" not in out

    def test_symbol_dce_removes_unused_private(self):
        """#120: symbol-dce drops unused private helpers."""
        out, code = OPT.optimize_source(DCE_PROGRAM, optimization_level="O2")
        assert code == 0
        assert "@dead_helper" not in out
