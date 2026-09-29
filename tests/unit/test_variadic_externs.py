"""Variadic externs: ellipsis parse, `is_variadic` survival, MLIR emission.

The `...` in `extern { function f(a: T, ...) -> R }` is an ELLIPSIS token.
It is distinct from `DOTDOT`. It must round-trip through the parser, survive monomorphize (which
rebuilds FunctionDecl positionally), and reach the MLIR backend as a variadic
prototype.
"""

import pytest

from flow.parser import parse_flow_code, FlowSyntaxError
from flow.mlir_generator import flow_to_mlir

PROGRAM = """\
extern {
    function my_log(fmt: string, ...) -> i32
}

function main() -> i32 {
    return my_log("a %d", 1)
}
"""


def _variadic_fn():
    decls = parse_flow_code(
        "extern { function my_log(fmt: string, ...) -> i32 }"
    )
    fns = [d for d in decls if getattr(d, "is_extern", False)]
    assert len(fns) == 1
    return fns[0]


def test_parser_sets_is_variadic():
    assert _variadic_fn().is_variadic is True


def test_parser_ellipsis_needs_fixed_prefix():
    # `function f(...)` (no fixed param) in a body function is a syntax error,
    # not a silent variadic. The grammar requires a name, then optional `, ...`.
    with pytest.raises(FlowSyntaxError):
        parse_flow_code("function f(...) -> i32 { return 0 }")


def test_mlir_emits_ellipsis():
    mlir = flow_to_mlir(parse_flow_code(PROGRAM))
    assert "...)" in mlir
    assert "@my_log" in mlir

