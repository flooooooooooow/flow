from flow.mlir_generator import MLIRGenerator
from flow.parser import parse_flow_code


def test_generic_array_constructor_lowers_to_dynamic_memref_allocation() -> None:
    code = """
export function alloc_sum() -> f32 {
    let mut values: array<f32> = array<f32>(2)
    values[0] = 1.5
    values[1] = 2.25
    return values[0] + values[1]
}
"""
    mlir = MLIRGenerator("alloc_sum.flow").generate_module(parse_flow_code(code))

    assert "func.call @array_f32" not in mlir
    assert "memref.alloc(" in mlir
    assert "memref<?xf32>" in mlir
