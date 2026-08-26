from flow.mlir_generator import MLIRGenerator
from flow.parser import parse_flow_code


CLOSURE = "!llvm.struct<(!llvm.ptr, !llvm.ptr)>"


def _lower(source: str) -> str:
    return MLIRGenerator().generate_module(parse_flow_code(source))


def test_capturing_closure_uses_fat_code_and_environment_value() -> None:
    mlir = _lower(
        """
        function make_adder(delta: i32) -> (i32) -> i32 {
            return |x: i32| -> i32 {
                return x + delta
            }
        }

        function apply(f: (i32) -> i32, x: i32) -> i32 {
            return f(x)
        }

        function main() -> i32 {
            let f: (i32) -> i32 = make_adder(3)
            return apply(f, 4)
        }
        """
    )

    assert CLOSURE in mlir
    assert "func.func private @lambda_" in mlir
    assert "%env: !llvm.ptr" in mlir
    assert "builtin.unrealized_conversion_cast" in mlir
    assert "llvm.insertvalue" in mlir
    assert "llvm.extractvalue" in mlir
    assert "llvm.call %" in mlir
    assert "Undefined variable: delta" not in mlir


def test_noncapturing_lambda_uses_same_uniform_fat_closure_abi() -> None:
    mlir = _lower(
        """
        function apply(f: (i32) -> i32, x: i32) -> i32 {
            return f(x)
        }

        function main() -> i32 {
            let twice: (i32) -> i32 = |x: i32| -> i32 {
                return x * 2
            }
            return apply(twice, 6)
        }
        """
    )

    assert CLOSURE in mlir
    assert "%env: !llvm.ptr" in mlir
    assert "llvm.mlir.zero : !llvm.ptr" in mlir
    assert "llvm.call %" in mlir


def test_closure_can_capture_other_first_class_function_values() -> None:
    mlir = _lower(
        """
        function affine(scale: i32, bias: i32) -> (i32) -> i32 {
            return |x: i32| -> i32 {
                return scale * x + bias
            }
        }

        function compose(
            outer: (i32) -> i32,
            inner: (i32) -> i32
        ) -> (i32) -> i32 {
            return |x: i32| -> i32 {
                return outer(inner(x))
            }
        }

        function main() -> i32 {
            let shift: (i32) -> i32 = affine(1, 2)
            let scale: (i32) -> i32 = affine(3, 0)
            let program: (i32) -> i32 = compose(scale, shift)
            return program(4)
        }
        """
    )

    assert CLOSURE in mlir
    assert f"!llvm.struct<({CLOSURE}, {CLOSURE})>" in mlir
    assert mlir.count("llvm.call %") >= 3
    assert "MLIR closure capture of memref/vector values" not in mlir
