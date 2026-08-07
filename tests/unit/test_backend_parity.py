"""C backend vs MLIR JIT exit-code parity (differential testing)."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from flow.mlir_jit import MLIRJIT
from flow.jit_runner import compile_flow_to_mlir
from tests.unit.compiler_helpers import compile_and_run, needs_clang, to_c


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


def _run_c_capture(source: str) -> tuple[int, str]:
    """Transpile -> clang -> run; return (exit code, stdout)."""
    c_code = to_c(source)
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        bin_path = os.path.join(td, "prog")
        Path(c_path).write_text(c_code)
        build = subprocess.run(
            ["clang", "-w", "-O0", "-o", bin_path, c_path],
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, f"clang failed:\n{build.stderr}\n---\n{c_code}"
        run = subprocess.run([bin_path], capture_output=True, text=True)
        return run.returncode, run.stdout


def _run_mlir_capture(source: str, capsys) -> tuple[int, str]:
    """Run through the MLIR JIT; return (exit code, program stdout).

    MLIRJIT forwards the child's stdout to sys.stdout, so capsys sees it. JIT
    diagnostics are prefixed with a status emoji and are filtered out.
    """
    capsys.readouterr()  # drop anything buffered so far
    rc = _run_mlir(source)
    captured = capsys.readouterr()
    lines = [
        ln
        for ln in captured.out.splitlines()
        if not ln.startswith(("⚠️", "❌", "MLIR "))
    ]
    return rc, "".join(ln + "\n" for ln in lines)


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
    # Hits the elementwise-for vectorizer (vector<4xi32> body + scalar tail);
    # 9 elements so the remainder loop runs too.
    "array_elementwise_for": """
function main() -> i32 {
    let mut xs: array<i32, 9> = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    let mut ys: array<i32, 9> = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    for i in 0 to 9 {
        ys[i] = xs[i] * 3 + ys[i]
    }
    let mut s: i32 = 0
    let mut j: i32 = 0
    while j < 9 {
        s = s + ys[j]
        j = j + 1
    }
    if s == 585 {
        return 0
    }
    return 1
}
""",
    "match_catch_all": """
function bucket(n: i32) -> i32 {
    match n {
        7 => { return 1 }
        default { return 2 }
    }
}
function main() -> i32 {
    if bucket(7) + bucket(8) + bucket(9) == 5 {
        return 0
    }
    return 1
}
""",
    "match_falls_through": """
function main() -> i32 {
    let n: i32 = 3
    let mut hit: i32 = 0
    match n {
        1 => { hit = 1 }
        3 => { hit = 3 }
    }
    if hit == 3 {
        return 0
    }
    return 1
}
""",
    "while_break": """
function main() -> i32 {
    let mut i: i32 = 0
    let mut s: i32 = 0
    while i < 100 {
        if i == 5 {
            break
        }
        s = s + i
        i = i + 1
    }
    if s == 10 && i == 5 {
        return 0
    }
    return 1
}
""",
    "while_continue": """
function main() -> i32 {
    let mut i: i32 = 0
    let mut s: i32 = 0
    while i < 10 {
        i = i + 1
        if i == 3 {
            continue
        }
        s = s + i
    }
    if s == 52 {
        return 0
    }
    return 1
}
""",
    "for_break": """
function main() -> i32 {
    let mut s: i32 = 0
    let mut last: i32 = -1
    for i in 0 to 20 {
        if i == 4 {
            break
        }
        s = s + i
        last = i
    }
    if s == 6 && last == 3 {
        return 0
    }
    return 1
}
""",
    "for_continue": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 0 to 10 {
        if i == 3 {
            continue
        }
        s = s + i
    }
    if s == 42 {
        return 0
    }
    return 1
}
""",
    "array_f32": """
function main() -> i32 {
    let mut xs: array<f32, 4> = [1.5, 2.5, 3.0, 3.0]
    xs[2] = 0.5
    let mut s: f32 = 0.0
    let mut i: i32 = 0
    while i < 4 {
        s = s + xs[i]
        i = i + 1
    }
    if s > 7.4 && s < 7.6 {
        return 0
    }
    return 1
}
""",
    # array<i64, N> = [1, 2, 3] parses as i32 literals; the memref must still
    # be allocated with the declared element type.
    "array_i64": """
function main() -> i32 {
    let mut xs: array<i64, 3> = [1, 2, 3]
    xs[0] = 10
    if xs[0] + xs[1] + xs[2] == 15 {
        return 0
    }
    return 1
}
""",
    "array_bool": """
function main() -> i32 {
    let mut flags: array<bool, 3> = [true, false, true]
    flags[1] = true
    if flags[0] && flags[1] && flags[2] {
        return 0
    }
    return 1
}
""",
    "array_2d_flat": """
function main() -> i32 {
    let mut g: array<i32, 9> = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    let mut r: i32 = 0
    while r < 3 {
        let mut c: i32 = 0
        while c < 3 {
            g[r * 3 + c] = r * 3 + c
            c = c + 1
        }
        r = r + 1
    }
    if g[0] + g[4] + g[8] == 12 {
        return 0
    }
    return 1
}
""",
    "array_of_structs": """
struct P { x: i32, y: i32 }
function main() -> i32 {
    let mut ps: array<P, 2> = [P { x: 1, y: 2 }, P { x: 3, y: 4 }]
    ps[0].x = 10
    if ps[0].x + ps[1].y == 14 {
        return 0
    }
    return 1
}
""",
    "array_param": """
function total(xs: array<i32, 4>) -> i32 {
    let mut s: i32 = 0
    let mut i: i32 = 0
    while i < 4 {
        s = s + xs[i]
        i = i + 1
    }
    return s
}
function main() -> i32 {
    let xs: array<i32, 4> = [1, 2, 3, 4]
    if total(xs) == 10 {
        return 0
    }
    return 1
}
""",
    "match_struct_pattern": """
struct P { x: i32, y: i32 }
function main() -> i32 {
    let p: P = P { x: 3, y: 4 }
    let mut r: i32 = 0
    match p {
        P(a, b) => { r = a + b }
    }
    if r == 7 {
        return 0
    }
    return 1
}
""",
    "match_f32": """
function main() -> i32 {
    let v: f32 = 2.0
    let mut r: i32 = 0
    match v {
        1.0 => { r = 1 }
        2.0 => { r = 2 }
        default { r = 3 }
    }
    if r == 2 {
        return 0
    }
    return 1
}
""",
    "while_inside_for": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 0 to 3 {
        let mut j: i32 = 0
        while j < 4 {
            s = s + 1
            j = j + 1
        }
    }
    if s == 12 {
        return 0
    }
    return 1
}
""",
    "nested_for_break": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 0 to 3 {
        for j in 0 to 5 {
            if j == 2 {
                break
            }
            s = s + 1
        }
    }
    if s == 6 {
        return 0
    }
    return 1
}
""",
    "for_step": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 0 to 10 step 2 {
        s = s + i
    }
    if s == 20 {
        return 0
    }
    return 1
}
""",
    "for_step_descending": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 5 to 0 step -1 {
        s = s + i
    }
    if s == 15 {
        return 0
    }
    return 1
}
""",
    "for_step_break": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 0 to 10 step 2 {
        if i == 6 {
            break
        }
        s = s + i
    }
    if s == 6 {
        return 0
    }
    return 1
}
""",
    "for_step_dynamic": """
function main() -> i32 {
    let mut s: i32 = 0
    let k: i32 = 3
    for i in 0 to 10 step k {
        s = s + i
    }
    if s == 18 {
        return 0
    }
    return 1
}
""",
    "match_string": """
function pick(s: string) -> i32 {
    match s {
        "a" => { return 1 }
        default { return 2 }
    }
}
function main() -> i32 {
    if pick("a") + pick("b") == 3 {
        return 0
    }
    return 1
}
""",
    "match_list_pattern": """
function main() -> i32 {
    let xs: array<i32, 3> = [1, 2, 3]
    let mut r: i32 = 0
    match xs {
        [1, a, b] => { r = a + b }
        default { r = 99 }
    }
    if r == 5 {
        return 0
    }
    return 1
}
""",
    "parallel_for": """
function main() -> i32 {
    let mut xs: array<i32, 4> = [0, 0, 0, 0]
    parallel for i in 0 to 4 {
        xs[i] = i
    }
    if xs[0] + xs[3] == 3 {
        return 0
    }
    return 1
}
""",
    "for_range_dots": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 0..5 {
        s = s + i
    }
    if s == 10 {
        return 0
    }
    return 1
}
""",
    "nested_while_carried": """
function main() -> i32 {
    let mut outer: i32 = 0
    let mut total: i32 = 0
    while outer < 4 {
        let mut inner: i32 = 0
        while inner < 3 {
            total = total + outer
            inner = inner + 1
        }
        outer = outer + 1
    }
    if total == 18 {
        return 0
    }
    return 1
}
""",
    "module_static": """
let mut counter: i32 = 41
function main() -> i32 {
    counter = counter + 1
    if counter == 42 {
        return 0
    }
    return 1
}
""",
    "for_break": """
function main() -> i32 {
    let mut found: i32 = 0
    for i in 0 to 10 {
        if i == 3 {
            found = 1
            break
        }
    }
    if found == 1 {
        return 0
    }
    return 1
}
""",
    "for_continue": """
function main() -> i32 {
    let mut s: i32 = 0
    for i in 0 to 5 {
        if i == 2 {
            continue
        }
        s = s + i
    }
    # 0+1+3+4 = 8
    if s == 8 {
        return 0
    }
    return 1
}
""",
    "enum_tag_match": """
enum Color {
    Red,
    Green,
    Blue
}
function classify(c: Color) -> i32 {
    match c.tag {
        Color_Red => { return 1 }
        Color_Green => { return 2 }
        Color_Blue => { return 3 }
    }
    return -1
}
function main() -> i32 {
    let c: Color = Color { tag: Color_Green }
    if classify(c) == 2 {
        return 0
    }
    return 1
}
""",
    "lambda_nocapture": """
function main() -> i32 {
    let add1: (i32) -> i32 = |x: i32| -> i32 { return x + 1 }
    let y: i32 = add1(41)
    if y == 42 {
        return 0
    }
    return 1
}
""",
}


# The C-only "does it exit 0" half of this matrix now lives in tests/lang/
# as runnable .flow programs (test_arithmetic, test_arrays, test_array_types,
# test_control_flow, test_functions, test_loops, test_match,
# test_match_patterns, test_parallel_for, test_structs). What stays here is
# the differential part: the same program through the MLIR JIT must agree
# with the C backend, which no single-backend .flow test can express.


@needs_clang
@needs_mlir
@pytest.mark.parametrize("name", list(PROGRAMS.keys()))
def test_c_mlir_exit_code_parity(name: str):
    src = PROGRAMS[name]
    c_rc = compile_and_run(src)
    # The toolchain guard above already skipped when mlir-opt/mlir-translate
    # are missing, so any exception here is a real lowering failure.
    mlir_rc = _run_mlir(src)
    assert c_rc == mlir_rc == 0, f"{name}: C={c_rc} MLIR={mlir_rc}"


# Programs whose observable behaviour is stdout, not just the exit code.
STDOUT_PROGRAMS = {
    "defer_lifo": """
extern {
    function printf(fmt: string, val: i32) -> i32
}
function work() -> i32 {
    let mut acc: i32 = 0
    defer printf("cleanup-a\\n", 0)
    defer printf("cleanup-b\\n", 0)
    acc = acc + 41
    printf("body\\n", 0)
    return acc
}
function main() -> i32 {
    if work() == 41 {
        return 0
    }
    return 1
}
""",
    "defer_in_loop_body": """
extern {
    function printf(fmt: string, val: i32) -> i32
}
function main() -> i32 {
    let mut i: i32 = 0
    while i < 3 {
        defer printf("tick %d\\n", i)
        i = i + 1
    }
    if i == 3 {
        return 0
    }
    return 1
}
""",
    "defer_before_early_return": """
extern {
    function printf(fmt: string, val: i32) -> i32
}
function f(n: i32) -> i32 {
    defer printf("cleanup\\n", 0)
    if n > 0 {
        printf("positive\\n", 0)
        return 1
    }
    return 0
}
function main() -> i32 {
    return f(1) - 1
}
""",
    "break_skips_tail": """
extern {
    function printf(fmt: string, val: i32) -> i32
}
function main() -> i32 {
    let mut i: i32 = 0
    while i < 10 {
        if i == 2 {
            break
        }
        printf("i=%d\\n", i)
        i = i + 1
    }
    if i == 2 {
        return 0
    }
    return 1
}
""",
}


@needs_clang
@needs_mlir
@pytest.mark.parametrize("name", list(STDOUT_PROGRAMS.keys()))
def test_c_mlir_stdout_parity(name: str, capsys):
    src = STDOUT_PROGRAMS[name]
    c_rc, c_out = _run_c_capture(src)
    mlir_rc, mlir_out = _run_mlir_capture(src, capsys)
    assert c_rc == 0, f"{name}: C exited {c_rc}"
    assert c_rc == mlir_rc, f"{name}: C={c_rc} MLIR={mlir_rc}"
    assert c_out == mlir_out, f"{name}: C stdout {c_out!r} != MLIR {mlir_out!r}"
