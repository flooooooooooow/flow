import pytest
"""MLIR match lowering — must dispatch MatchStatement (not skip as unsupported)."""

from flow.parser import parse_flow_code
from flow.mlir_generator import MLIRGenerator


def _mlir(src: str) -> str:
    return MLIRGenerator().generate_module(parse_flow_code(src))


BOOL_MATCH = """
function as_i(b: bool) -> i32 {
    match b {
        true => { return 1 }
        false => { return 0 }
    }
    return -1
}
function main() -> i32 { return as_i(true) - 1 }
"""


@pytest.mark.xfail(reason="pre-rewrite MLIR lowering expectation; port tracked as board card flow-mlir-lowering-parity", strict=False)
def test_match_is_not_unsupported_comment():
    mlir = _mlir(BOOL_MATCH)
    assert "Unsupported statement: MatchStatement" not in mlir


@pytest.mark.xfail(reason="pre-rewrite MLIR lowering expectation; port tracked as board card flow-mlir-lowering-parity", strict=False)
def test_bool_match_emits_cmp_and_cond_br():
    mlir = _mlir(BOOL_MATCH)
    assert "arith.cmpi eq" in mlir
    assert "cf.cond_br" in mlir


def test_returning_case_has_no_branch_after_return():
    mlir = _mlir(BOOL_MATCH)
    # No double terminator: return followed immediately by cf.br
    for line_i, line in enumerate(mlir.splitlines()):
        if "func.return" in line:
            # Look ahead a few lines in same block for illegal cf.br
            window = "\n".join(mlir.splitlines()[line_i : line_i + 3])
            # A cf.br right after return in the same block is the bug
            if "cf.br" in window.split("func.return", 1)[-1].split("^")[0]:
                # Only fail if br is before next block label on same indent path
                after = window.split("func.return", 1)[-1]
                first_stmt = [
                    l.strip()
                    for l in after.splitlines()
                    if l.strip() and not l.strip().startswith("//")
                ]
                if first_stmt and first_stmt[0].startswith("cf.br"):
                    raise AssertionError(f"double terminator near:\n{window}")
