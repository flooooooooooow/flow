"""Variadic externs: ellipsis parse, `is_variadic` survival, C/MLIR emission.

The `...` in `extern { function f(a: T, ...) -> R }` is an ELLIPSIS token, not
`DOTDOT`. It must round-trip through the parser, survive monomorphize (which
rebuilds FunctionDecl positionally), and reach the C and MLIR backends as a
variadic prototype.

Every "it works" claim here is backed by a clang compile and a process run.
"""

import pytest

from flow.parser import parse_flow_code, FlowSyntaxError
from flow.mlir_generator import flow_to_mlir

from .compiler_helpers import compile_and_run, to_c

# A custom-named variadic extern: `snprintf` is in the C backend's stdlib skip
# set (its prototype comes from stdio.h, so `...` would never be emitted).
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


def test_c_emits_ellipsis():
    c = to_c(PROGRAM)
    assert "int32_t my_log(char* fmt, ...)" in c


def test_mlir_emits_ellipsis():
    mlir = flow_to_mlir(parse_flow_code(PROGRAM))
    assert "...)" in mlir
    assert "@my_log" in mlir


def test_no_fixed_params_is_still_variadic():
    # A variadic extern with only `...` and no fixed params emits bare `...`.
    c = to_c("extern { function my_sink(...) -> void }\nfunction main() -> i32 { return 0 }")
    assert "void my_sink(...)" in c


def test_runtime_varargs_reach_libc():
    # `snprintf`'s write count depends on the varargs surviving to libc.
    src = """\
extern {
    function malloc(size: i64) -> ptr<u8>
    function free(p: ptr<u8>)
    function snprintf(buf: ptr<u8>, n: i64, fmt: string, ...) -> i32
}

function main() -> i32 {
    let buf: ptr<u8> = malloc(64)
    let wrote: i32 = snprintf(buf, 64, "x=%d sum=%d", 3, 40)
    free(buf)
    return wrote
}
"""
    assert compile_and_run(src) == 10