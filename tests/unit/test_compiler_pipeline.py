"""End-to-end compiler pipeline smoke — parse → typecheck → mono → C → clang."""

from tests.unit.compiler_helpers import (
    parse,
    typecheck,
    to_c,
    needs_clang,
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


# test_pipeline_runs and test_pipeline_control_and_calls compiled and ran
# PIPELINE_SRC and an abs/loop program. Both now run as Flow programs:
# tests/lang/test_structs.flow and tests/lang/test_functions.flow.
