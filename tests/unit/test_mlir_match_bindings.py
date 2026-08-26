from flow.mlir_generator import MLIRGenerator
from flow.parser import parse_flow_code


def _lower(source: str) -> str:
    return MLIRGenerator().generate_module(parse_flow_code(source))


def test_binding_pattern_is_visible_to_guard_and_body() -> None:
    mlir = _lower(
        """
        function classify(value: i32) -> i32 {
            match value {
                x if x > 1 => { return x }
                _ => { return 0 }
            }
        }
        """
    )

    assert "Undefined variable" not in mlir
    assert "arith.cmpi sgt" in mlir
    assert "arith.andi" in mlir


def test_wildcard_pattern_is_unconditional() -> None:
    mlir = _lower(
        """
        function classify(value: i32) -> i32 {
            match value {
                0 => { return 1 }
                _ => { return 2 }
            }
        }
        """
    )

    assert "Undefined variable: _" not in mlir
    assert "arith.constant 1 : i1" in mlir


def test_exhaustive_returning_wildcard_match_terminates_join() -> None:
    mlir = _lower(
        """
        function classify(value: i32) -> i32 {
            match value {
                0 => { return 1 }
                x if x < 8 => { return 2 }
                _ => { return 3 }
            }
        }
        """
    )

    assert "llvm.unreachable" in mlir
    assert "Undefined variable" not in mlir


def test_nested_exhaustive_match_does_not_branch_after_unreachable() -> None:
    mlir = _lower(
        """
        function classify(outer: i32, inner: i32) -> i32 {
            match outer {
                0 => {
                    match inner {
                        0 => { return 1 }
                        _ => { return 2 }
                    }
                }
                _ => { return 3 }
            }
        }
        """
    )

    lines = [line.strip() for line in mlir.splitlines() if line.strip()]
    for index, line in enumerate(lines[:-1]):
        if line == "llvm.unreachable":
            assert lines[index + 1].startswith("^") or lines[index + 1] == "}"


def test_exhaustive_returning_match_drops_dead_following_statements() -> None:
    mlir = _lower(
        """
        function classify(value: i32) -> i32 {
            match value {
                0 => { return 1 }
                _ => { return 2 }
            }
            let impossible: i32 = 987654321
            return impossible
        }
        """
    )

    assert "987654321" not in mlir
    assert "llvm.unreachable" in mlir
