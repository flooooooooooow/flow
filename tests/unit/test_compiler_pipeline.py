"""Front-end pipeline smoke: parse, typecheck, monomorphize.

The C half of the pipeline is flowc; tests/lang/test_structs.flow and
tests/lang/test_functions.flow compile and run these programs with it.
"""

from tests.unit.compiler_helpers import parse, typecheck
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


def test_pipeline_parse_typecheck_mono():
    decls = parse(PIPELINE_SRC)
    result = typecheck(PIPELINE_SRC)
    assert result.errors == []
    mono = monomorphize(decls)
    names = {getattr(d, "name", None) for d in mono}
    assert "dist2" in names
    assert "Point" in names


# test_pipeline_runs and test_pipeline_control_and_calls compiled and ran
# PIPELINE_SRC and an abs/loop program. Both now run as Flow programs:
# tests/lang/test_structs.flow and tests/lang/test_functions.flow.
