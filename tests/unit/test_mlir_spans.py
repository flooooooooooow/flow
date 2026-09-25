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


def _defs(body: str) -> dict:
    import re

    out = {}
    for line in body.splitlines():
        m = re.match(r"\s*(%\d+) = (.*)", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def test_address_of_a_span_element_is_the_element_not_a_copy() -> None:
    """`&xs[i]` and `&xs.data[i]` must address the span's own storage.

    Both shapes reached the spill fallback in _generate_address_of, which loads
    the element and hands out the address of a fresh alloca. A callee writing
    through that pointer updated the copy and the span kept its old contents.
    `&xs.data[i]` also walked f32 slots for a span of f64, so an eight byte
    write went into a four byte allocation.
    """
    import re

    source = """
    extern {
        function __sincos(x: f64, s: ptr<f64>, c: ptr<f64>) -> void
    }

    function viadata(s: span<mut f64>, c: span<mut f64>, n: i32) -> void {
        for i in 0 to n { __sincos(i as f64, &s.data[i], &c.data[i]) }
    }

    function direct(s: span<mut f64>, c: span<mut f64>, n: i32) -> void {
        for i in 0 to n { __sincos(i as f64, &s[i], &c[i]) }
    }
    """
    mlir = MLIRGenerator().generate_module(parse_flow_code(source))

    for name in ("viadata", "direct"):
        body = mlir.split(f"@{name}", 1)[1].split("func.func", 1)[0]
        call = [l for l in body.splitlines() if "@__sincos" in l]
        assert call, f"{name}: no call emitted\n{body}"

        args = re.findall(r"%\d+", call[0].split("(", 1)[1])
        defs = _defs(body)
        for arg in args[1:3]:
            rhs = defs.get(arg, "")
            assert rhs.startswith("llvm.getelementptr"), (
                f"{name}: {arg} is {rhs!r}, expected a gep off the pair"
            )
            assert rhs.rstrip().endswith("f64"), (
                f"{name}: {arg} geps at {rhs!r}, expected f64 slots"
            )
