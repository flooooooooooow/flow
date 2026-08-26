from flow.mlir_generator import MLIRGenerator
from flow.parser import parse_flow_code


def test_mlir_lowers_literal_or_pattern() -> None:
    source = """
    function classify(x: i32) -> i32 {
        match x {
            1 | 2 | 3 => { return 7 }
            default { return 9 }
        }
    }
    """

    ast = parse_flow_code(source)
    mlir = MLIRGenerator().generate_module(ast)

    assert "func.func @classify" in mlir
    assert "cf.cond_br" in mlir
    assert mlir.count("arith.cmpi eq") >= 3
