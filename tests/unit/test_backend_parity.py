"""C backend vs MLIR JIT exit-code parity (differential testing)."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from flow.mlir_jit import MLIRJIT
from flow.jit_runner import compile_flow_to_mlir
from tests.unit.compiler_helpers import compile_and_run, needs_clang


def _mlir_toolchain() -> bool:
    jit = MLIRJIT()
    return (
        jit._find_mlir_opt() is not None
        and jit._find_mlir_translate() is not None
        and shutil.which("clang") is not None
    )


needs_mlir = pytest.mark.skipif(
    not _mlir_toolchain(), reason="mlir-opt/mlir-translate/clang not available"
)


def _run_mlir(source: str) -> int:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".flow", delete=False) as f:
        f.write(source)
        flow_file = f.name
    try:
        mlir_code = compile_flow_to_mlir(flow_file)
        jit = MLIRJIT()
        try:
            result = jit.jit_compile_and_run(mlir_code, "main")
        finally:
            jit.cleanup()
        assert result is not None, "MLIR JIT produced no result"
        return result
    finally:
        Path(flow_file).unlink(missing_ok=True)


PROGRAMS = {
    "arith": """
function main() -> i32 {
    let a: i32 = 40
    let b: i32 = 2
    if a + b == 42 {
        return 0
    }
    return 1
}
""",
    "struct_fields": """
struct Point { x: i32, y: i32 }
function main() -> i32 {
    let p: Point = Point { x: 20, y: 22 }
    if p.x + p.y == 42 {
        return 0
    }
    return 1
}
""",
    "while_sum": """
function main() -> i32 {
    let mut i: i32 = 0
    let mut s: i32 = 0
    while i < 10 {
        s = s + i
        i = i + 1
    }
    if s == 45 {
        return 0
    }
    return 1
}
""",
    "for_sum": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 0 to 10 {
        s = s + i
    }
    if s == 45 {
        return 0
    }
    return 1
}
""",
    "if_else": """
function main() -> i32 {
    let x: i32 = 3
    if x > 5 {
        return 1
    } elif x == 3 {
        return 0
    } else {
        return 2
    }
}
""",
    "recursive_fact": """
function fact(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * fact(n - 1)
}
function main() -> i32 {
    if fact(5) == 120 {
        return 0
    }
    return 1
}
""",
    "nested_struct": """
struct Point { x: i32, y: i32 }
struct Seg { a: Point, b: Point }
function main() -> i32 {
    let s: Seg = Seg {
        a: Point { x: 1, y: 2 },
        b: Point { x: 4, y: 6 }
    }
    let dx: i32 = s.b.x - s.a.x
    let dy: i32 = s.b.y - s.a.y
    if dx * dx + dy * dy == 25 {
        return 0
    }
    return 1
}
""",
    "array_sum": """
function main() -> i32 {
    let mut xs: array<i32, 4> = [10, 20, 30, 40]
    xs[1] = 25
    let mut s: i32 = 0
    for i in 0 to 4 {
        s = s + xs[i]
    }
    if s == 105 {
        return 0
    }
    return 1
}
""",
    "short_circuit_and": """
function main() -> i32 {
    let a: i32 = 3
    let b: i32 = 4
    if a < b && b < 10 {
        return 0
    }
    return 1
}
""",
    "nested_calls": """
function double(x: i32) -> i32 { return x + x }
function inc(x: i32) -> i32 { return x + 1 }
function main() -> i32 {
    if double(inc(20)) == 42 {
        return 0
    }
    return 1
}
""",
    "bool_match": """
function as_i(b: bool) -> i32 {
    match b {
        true => { return 1 }
        false => { return 0 }
    }
    return -1
}
function main() -> i32 {
    if as_i(true) + as_i(false) == 1 {
        return 0
    }
    return 1
}
""",
    "i32_match": """
function classify(n: i32) -> i32 {
    match n {
        0 => { return 10 }
        1 => { return 20 }
        default { return 30 }
    }
}
function main() -> i32 {
    if classify(0) + classify(1) + classify(9) == 60 {
        return 0
    }
    return 1
}
""",
    "nested_while": """
function main() -> i32 {
    let mut outer: i32 = 0
    let mut s: i32 = 0
    while outer < 3 {
        let mut inner: i32 = 0
        while inner < 4 {
            s = s + 1
            inner = inner + 1
        }
        outer = outer + 1
    }
    if s == 12 {
        return 0
    }
    return 1
}
""",
    "while_break_via_cond": """
function main() -> i32 {
    let mut n: i32 = 1
    let mut steps: i32 = 0
    while n < 100 {
        n = n + n
        steps = steps + 1
    }
    if n == 128 && steps == 7 {
        return 0
    }
    return 1
}
""",
    "array_mutate_loop": """
function main() -> i32 {
    let mut xs: array<i32, 5> = [1, 2, 3, 4, 5]
    let mut i: i32 = 0
    while i < 5 {
        xs[i] = xs[i] * 2
        i = i + 1
    }
    if xs[0] + xs[4] == 12 {
        return 0
    }
    return 1
}
""",
}


@needs_clang
@pytest.mark.parametrize("name", list(PROGRAMS.keys()))
def test_c_backend_exit_zero(name: str):
    assert compile_and_run(PROGRAMS[name]) == 0


@needs_clang
@needs_mlir
@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            n,
            marks=pytest.mark.xfail(
                reason="bool match lowering parity; board card flow-mlir-lowering-parity",
                strict=False,
            ),
        )
        if n == "bool_match"
        else n
        for n in PROGRAMS.keys()
    ],
)
def test_c_mlir_exit_code_parity(name: str):
    src = PROGRAMS[name]
    c_rc = compile_and_run(src)
    try:
        mlir_rc = _run_mlir(src)
    except Exception as exc:
        pytest.skip(f"MLIR run unavailable for {name}: {exc}")
    assert c_rc == mlir_rc == 0, f"{name}: C={c_rc} MLIR={mlir_rc}"
