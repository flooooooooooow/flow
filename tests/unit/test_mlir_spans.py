from flow.mlir_generator import MLIRGenerator
from flow.parser import parse_flow_code


def test_mlir_lowers_span_slice_len_and_indexing() -> None:
    source = """
    function sum(values: span<f32>) -> f32 {
        let mut total: f32 = 0.0
        let mut i: i32 = 0
        while i < values.len {
            total = total + values[i]
            i = i + 1
        }
        return total
    }

    function main() -> i32 {
        let values: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let total: f32 = sum(values[1..3])
        if total == 5.0 { return 0 }
        return 1
    }
    """

    ast = parse_flow_code(source)
    mlir = MLIRGenerator().generate_module(ast)

    assert "!llvm.struct<(!llvm.ptr, i64)>" in mlir
    assert "llvm.getelementptr" in mlir
    assert "llvm.extractvalue" in mlir
    assert "llvm.insertvalue" in mlir


def test_mlir_lowers_mutable_span_store() -> None:
    source = """
    function clear(values: span<mut i32>) -> void {
        values[0] = 0
    }

    function main() -> i32 {
        let mut values: array<i32, 2> = [7, 9]
        clear(values[0..2])
        return values[0]
    }
    """

    ast = parse_flow_code(source)
    mlir = MLIRGenerator().generate_module(ast)

    assert "llvm.store" in mlir
    assert "!llvm.struct<(!llvm.ptr, i64)>" in mlir
