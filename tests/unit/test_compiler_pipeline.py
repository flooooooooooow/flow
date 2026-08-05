"""End-to-end compiler pipeline smoke — parse → typecheck → mono → C → clang."""

from tests.unit.compiler_helpers import (
    parse,
    typecheck,
    to_c,
    needs_clang,
    compile_and_run,
    compile_c_only,
)
from flow.monomorphize import monomorphize


PIPELINE_SRC = """
struct Point { x: i32, y: i32 }

function dist2(p: Point) -> i32 {
    return p.x * p.x + p.y * p.y
}

function main() -> i32 {
    let p: Point = Point { x: 3, y: 4 }
    if dist2(p) == 25 {
        return 0
    }
    return 1
}
"""


def test_pipeline_parse_typecheck_mono_c():
    decls = parse(PIPELINE_SRC)
    result = typecheck(PIPELINE_SRC)
    assert result.errors == []
    mono = monomorphize(decls)
    c = to_c(PIPELINE_SRC)
    assert "dist2" in c
    assert "Point" in c
    assert mono


@needs_clang
def test_pipeline_clang_syntax_only():
    compile_c_only(PIPELINE_SRC)


@needs_clang
def test_pipeline_runs():
    assert compile_and_run(PIPELINE_SRC) == 0


@needs_clang
def test_pipeline_control_and_calls():
    src = """
function abs_i(x: i32) -> i32 {
    if x < 0 {
        return 0 - x
    }
    return x
}

function main() -> i32 {
    let mut s: i32 = 0
    for i in 0 to 5 {
        s = s + abs_i(i - 2)
    }
    # abs(-2)+abs(-1)+abs(0)+abs(1)+abs(2) = 2+1+0+1+2 = 6
    if s == 6 {
        return 0
    }
    return 1
}
"""
    assert compile_and_run(src) == 0
