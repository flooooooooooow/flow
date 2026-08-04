"""Escaping HOF ABI: (T)->R fat-pointer closures."""

import os
import shutil
import subprocess
import tempfile

import pytest

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c
from flow.type_checker import TypeChecker


needs_clang = pytest.mark.skipif(
    shutil.which("clang") is None, reason="clang not available"
)


def compile_and_run(source: str) -> int:
    c_code = flow_to_c(parse_flow_code(source))
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        bin_path = os.path.join(td, "prog")
        with open(c_path, "w") as f:
            f.write(c_code)
        build = subprocess.run(
            ["clang", "-o", bin_path, c_path], capture_output=True, text=True
        )
        assert build.returncode == 0, f"clang failed:\n{build.stderr}\n---\n{c_code}"
        return subprocess.run([bin_path], capture_output=True).returncode


def test_parse_fn_type():
    from flow.parser import parse_flow_code

    decls = parse_flow_code(
        """
function apply(f: (i32) -> i32, x: i32) -> i32 {
    return f(x)
}
function main() -> i32 { return 0 }
"""
    )
    apply = next(d for d in decls if getattr(d, "name", None) == "apply")
    assert apply.parameters[0].type.name == "fn_i32__i32"


def test_fn_type_typedef_emitted():
    c = flow_to_c(
        parse_flow_code(
            """
function main() -> i32 {
    let n: i32 = 5
    let add_n: (i32) -> i32 = |x: i32| -> i32 { return x + n }
    return add_n(10)
}
"""
        )
    )
    assert "typedef struct" in c and "fn_i32__i32" in c
    assert ".env =" in c
    assert "add_n.fn(add_n.env" in c


@needs_clang
def test_e2e_local_fn_type_capture():
    rc = compile_and_run(
        """
function main() -> i32 {
    let n: i32 = 5
    let add_n: (i32) -> i32 = |x: i32| -> i32 { return x + n }
    if add_n(10) == 15 {
        return 0
    }
    return 1
}
"""
    )
    assert rc == 0


@needs_clang
def test_e2e_return_escaping_closure():
    rc = compile_and_run(
        """
function make_adder(n: i32) -> (i32) -> i32 {
    return |x: i32| -> i32 { return x + n }
}

function main() -> i32 {
    let add5: (i32) -> i32 = make_adder(5)
    if add5(37) == 42 {
        return 0
    }
    return 1
}
"""
    )
    assert rc == 0


@needs_clang
def test_e2e_hof_parameter():
    rc = compile_and_run(
        """
function apply(f: (i32) -> i32, x: i32) -> i32 {
    return f(x)
}

function main() -> i32 {
    let n: i32 = 2
    let times_n: (i32) -> i32 = |x: i32| -> i32 { return x * n }
    if apply(times_n, 21) == 42 {
        return 0
    }
    return 1
}
"""
    )
    assert rc == 0


def test_strict_types_accept_fn_annotation():
    checker = TypeChecker()
    checker.strict = True
    result = checker.check(
        parse_flow_code(
            """
function main() -> i32 {
    let n: i32 = 1
    let f: (i32) -> i32 = |x: i32| -> i32 { return x + n }
    return f(0)
}
"""
        )
    )
    assert result.errors == [], result.errors
