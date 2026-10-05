"""Extended C-vs-MLIR differential parity.

This complements ``test_backend_parity.py`` with categories that suite did not
cover (double precision, i64/u32, integer division and modulo, bitwise and
shift operators, comparison operators, capturing closures, mutual recursion,
nested aggregates, effect handlers, and loop-in-parallel nesting), plus an
explicit record of the current parity *boundary*: the small set of constructs
that the C backend compiles and runs but the MLIR JIT cannot yet lower.

Every case here was verified to agree across both backends on a machine with
the real MLIR toolchain (mlir-opt / mlir-translate / clang). The boundary test
at the bottom asserts the gap still exists; when it starts *failing*, MLIR has
gained support for that construct, and the case should move into the parity set
and ``docs/project/maturity.md`` should be updated.

All tests are skipped unless the MLIR toolchain is present (see ``needs_mlir``).
"""

from __future__ import annotations

import pytest

from tests.unit.test_backend_parity import (
    needs_mlir,
    _run_c_capture,
    _run_mlir_capture,
)


# ---------------------------------------------------------------------------
# Exit-code parity: program returns 0 on success, nonzero identifies the check.
# Each was confirmed to produce identical (exit code, stdout) on both backends.
# ---------------------------------------------------------------------------
EXIT_PROGRAMS = {
    "f64_add": """
function main() -> i32 {
    let a: f64 = 1.5
    let b: f64 = 2.5
    if a + b == 4.0 { return 0 }
    return 1
}
""",
    "f64_mul": """
function main() -> i32 {
    let a: f64 = 3.0
    let b: f64 = 4.0
    if a * b == 12.0 { return 0 }
    return 1
}
""",
    "f64_div": """
function main() -> i32 {
    let a: f64 = 1.0
    let b: f64 = 4.0
    if a / b == 0.25 { return 0 }
    return 1
}
""",
    "i64_add": """
function main() -> i32 {
    let a: i64 = 5000000000
    let b: i64 = 1
    if a + b == 5000000001 { return 0 }
    return 1
}
""",
    "u32_add": """
function main() -> i32 {
    let a: u32 = 4000000000
    let b: u32 = 1
    if a + b == 4000000001 { return 0 }
    return 1
}
""",
    "int_div_mod": """
function main() -> i32 {
    let a: i32 = 17
    if a / 5 == 3 && a % 5 == 2 { return 0 }
    return 1
}
""",
    "negatives": """
function main() -> i32 {
    let a: i32 = 0 - 5
    let b: i32 = 3
    if a + b == 0 - 2 { return 0 }
    return 1
}
""",
    "bitwise_and_or_xor": """
function main() -> i32 {
    let a: i32 = 12
    let b: i32 = 10
    if (a & b) == 8 && (a | b) == 14 && (a ^ b) == 6 { return 0 }
    return 1
}
""",
    "shifts": """
function main() -> i32 {
    let a: i32 = 1
    if (a << 4) == 16 && (16 >> 2) == 4 { return 0 }
    return 1
}
""",
    "comparisons": """
function main() -> i32 {
    let a: i32 = 5
    if a > 3 && a >= 5 && a < 10 && a <= 5 && a != 4 { return 0 }
    return 1
}
""",
    "closure_capture": """
function main() -> i32 {
    let base: i32 = 40
    let add: (i32) -> i32 = |x: i32| -> i32 { return x + base }
    if add(2) == 42 { return 0 }
    return 1
}
""",
    "struct_with_array": """
struct Box { items: array<i32, 3> }
function main() -> i32 {
    let mut b: Box = Box { items: [1, 2, 3] }
    b.items[1] = 40
    if b.items[0] + b.items[1] == 41 { return 0 }
    return 1
}
""",
    "mutual_recursion": """
function is_even(n: i32) -> i32 {
    if n == 0 { return 1 }
    return is_odd(n - 1)
}
function is_odd(n: i32) -> i32 {
    if n == 0 { return 0 }
    return is_even(n - 1)
}
function main() -> i32 {
    if is_even(10) == 1 && is_odd(7) == 1 { return 0 }
    return 1
}
""",
    "bool_not": """
function main() -> i32 {
    let t: bool = true
    if !t == false { return 0 }
    return 1
}
""",
    "for_break_inner": """
function main() -> i32 {
    let mut acc: i32 = 0
    for i in 0 to 10 step 1 {
        if i == 5 { break }
        acc = acc + i
    }
    if acc == 10 { return 0 }
    return 1
}
""",
    "for_inside_parallel": """
function main() -> i32 {
    let mut xs: array<i32, 4> = [0, 0, 0, 0]
    parallel for i in 0 to 4 step 1 {
        let mut acc: i32 = 0
        for j in 0 to 3 step 1 { acc = acc + j }
        xs[i] = acc
    }
    if xs[0] + xs[3] == 6 { return 0 }
    return 1
}
""",
}


# ---------------------------------------------------------------------------
# Stdout parity: programs whose observable behaviour is printed text. Effect
# handlers land here because the interesting parity is the emitted output.
# ---------------------------------------------------------------------------
STDOUT_PROGRAMS = {
    "effect_handler_direct": """
extern { function printf(fmt: string, arg: string) -> i32 }
effect Log { info(msg: string) -> void, }
capability Console {
    effect Log,
    function info(msg: string) -> void { printf("[log] %s\\n", msg) },
}
function main() -> i32 {
    handle Log with Console { Log.info("hello") }
    return 0
}
""",
    "effect_op_returns_value": """
extern { function printf(fmt: string, arg: string) -> i32 }
effect Log { metric(name: string, value: i32) -> i32, }
capability Console {
    effect Log,
    function metric(name: string, value: i32) -> i32 {
        printf("[metric] %s\\n", name)
        return value
    },
}
function main() -> i32 {
    handle Log with Console {
        let v: i32 = Log.metric("k", 7)
        if v == 7 { return 0 }
    }
    return 1
}
""",
    "println_str": """
function main() -> i32 {
    println("hi")
    return 0
}
""",
}


@needs_mlir
@pytest.mark.parametrize("name", list(EXIT_PROGRAMS.keys()))
def test_extended_exit_parity(name: str):
    src = EXIT_PROGRAMS[name]
    c = _run_c_capture(src)
    m = _mlir_result(src)
    assert c[0] == m, f"exit-code parity mismatch for {name}: C={c[0]} MLIR={m}"


@needs_mlir
@pytest.mark.parametrize("name", list(STDOUT_PROGRAMS.keys()))
def test_extended_stdout_parity(name: str, capsys):
    src = STDOUT_PROGRAMS[name]
    c = _run_c_capture(src)
    m = _run_mlir_capture(src, capsys)
    assert c == m, f"stdout/exit parity mismatch for {name}: C={c} MLIR={m}"


# ---------------------------------------------------------------------------
# Parity boundary: constructs the C backend handles but the MLIR JIT does not
# yet lower. These pin the current frontier. If one starts PASSING on MLIR,
# this test fails: move the case into a parity set above and update
# docs/project/maturity.md's backend table.
# ---------------------------------------------------------------------------
MLIR_KNOWN_GAPS = {
    # String runtime helpers (len, concatenation) lower to calls the MLIR JIT
    # cannot resolve; the C backend links them from its preamble.
    "string_len": """
function main() -> i32 {
    let s: string = "hello"
    return len(s)
}
""",
    "string_concat": """
function main() -> i32 {
    let a: string = "foo"
    let b: string = a + "bar"
    if b == "foobar" { return 0 }
    return 1
}
""",
}


@needs_mlir
@pytest.mark.parametrize("name", list(MLIR_KNOWN_GAPS.keys()))
def test_mlir_known_gap_still_open(name: str):
    """The C backend must handle these; the MLIR JIT must NOT yet.

    A failure here in the MLIR direction is good news: it means parity closed.
    When that happens, promote the case to a parity set above and update the
    maturity doc.
    """
    src = MLIR_KNOWN_GAPS[name]
    c = _run_c_capture(src)
    assert isinstance(c[0], int), f"C backend should compile+run {name}, got {c}"
    m = _mlir_result(src)
    assert m is None, (
        f"MLIR now lowers {name!r} (produced {m!r}). Parity closed: move this "
        f"case into a parity set and update docs/project/maturity.md."
    )


def _mlir_result(src: str):
    """Run a program through the MLIR JIT, returning its exit code or None.

    None means the JIT could not produce a result (a lowering/verify error or
    an exception), which is how the boundary cases manifest.
    """
    import tempfile
    from pathlib import Path
    from flow.mlir_jit import MLIRJIT
    from flow.jit_runner import compile_flow_to_mlir

    with tempfile.NamedTemporaryFile(mode="w", suffix=".flow", delete=False) as f:
        f.write(src)
        flow_file = f.name
    try:
        try:
            mlir_code = compile_flow_to_mlir(flow_file)
        except Exception:
            return None
        if "Unsupported" in mlir_code:
            return None
        jit = MLIRJIT()
        try:
            return jit.jit_compile_and_run(mlir_code, "main")
        except Exception:
            return None
        finally:
            jit.cleanup()
    finally:
        Path(flow_file).unlink(missing_ok=True)
