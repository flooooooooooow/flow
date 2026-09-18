"""Indentation-based multiline text blocks and `print:` syntax (#721).

Covers the `print:` (direct output) and `text:` (expression) block forms:
dedent to the block's minimum indentation, preserved blank lines, `${...}`
interpolation, literal `$${` openers, and literal quotes/backslashes.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


needs_clang = pytest.mark.skipif(
    shutil.which("clang") is None, reason="clang not available"
)


def _gen_c(source: str) -> str:
    return flow_to_c(parse_flow_code(source))


def _run_stdout(source: str) -> str:
    """Transpile with the Python host, compile with clang, return stdout."""
    c_code = _gen_c(source)
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        bin_path = os.path.join(td, "prog")
        with open(c_path, "w") as f:
            f.write(c_code)
        build = subprocess.run(
            ["clang", "-O0", "-o", bin_path, c_path, "-lm"],
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, f"clang failed:\n{build.stderr}\n---\n{c_code}"
        run = subprocess.run([bin_path], capture_output=True, text=True)
        assert run.returncode == 0, f"program exited {run.returncode}"
        return run.stdout


# --------------------------------------------------------------------------
# Parsing / codegen structure
# --------------------------------------------------------------------------

def test_print_block_parses_to_print_call():
    c = _gen_c(
        """
function main() -> i32 {
    print:
        hello world
    return 0
}
"""
    )
    assert "hello world" in c
    assert "FLOW_LOG" in c


def test_text_block_bound_to_variable():
    c = _gen_c(
        """
function main() -> i32 {
    let message: string = text:
        hello world
    print(message)
    return 0
}
"""
    )
    # The block lowers to a string; the variable is declared as a C string.
    assert "hello world" in c
    assert "message" in c


def test_normal_print_call_unchanged():
    # A regular inline print(...) must not be treated as a block.
    c = _gen_c(
        """
function main() -> i32 {
    print("hello")
    return 0
}
"""
    )
    assert '"hello"' in c


def test_text_named_variable_still_works():
    # `text:` only introduces a block when a newline follows the colon.
    # A `text` variable with an inline type annotation is unaffected.
    c = _gen_c(
        """
function main() -> i32 {
    let text: string = "plain"
    print(text)
    return 0
}
"""
    )
    assert '"plain"' in c


# --------------------------------------------------------------------------
# Runtime behavior (requires clang)
# --------------------------------------------------------------------------

@needs_clang
def test_print_block_runtime():
    out = _run_stdout(
        """
function main() -> i32 {
    print:
        Hello world.
    return 0
}
"""
    )
    assert out == "Hello world."


@needs_clang
def test_interpolation_runtime():
    out = _run_stdout(
        """
function main() -> i32 {
    let name: string = "Alice"
    let score: i32 = 42
    print:
        Hello ${name}.

        Welcome to Flow.
        Your score is ${score}.
    return 0
}
"""
    )
    assert out == "Hello Alice.\n\nWelcome to Flow.\nYour score is 42."


@needs_clang
def test_dedent_to_minimum_indentation():
    # The block's common leading indentation is stripped; relative indentation
    # deeper than the minimum is preserved.
    out = _run_stdout(
        """
function main() -> i32 {
    print:
        top
            nested
        back
    return 0
}
"""
    )
    assert out == "top\n    nested\nback"


@needs_clang
def test_blank_line_preserved():
    out = _run_stdout(
        """
function main() -> i32 {
    print:
        line one

        line three
    return 0
}
"""
    )
    assert out == "line one\n\nline three"


@needs_clang
def test_text_block_variable_runtime():
    out = _run_stdout(
        """
function main() -> i32 {
    let name: string = "Bob"
    let message: string = text:
        Hello ${name},

        Thanks,
        Flow
    print(message)
    return 0
}
"""
    )
    assert out == "Hello Bob,\n\nThanks,\nFlow"


@needs_clang
def test_literal_quotes_and_backslashes():
    out = _run_stdout(
        """
function main() -> i32 {
    print:
        He said "hello".
        C:\\Users\\foo\\bar
        JSON: {"enabled": true}
    return 0
}
"""
    )
    assert out == 'He said "hello".\nC:\\Users\\foo\\bar\nJSON: {"enabled": true}'


@needs_clang
def test_literal_dollar_brace_opener():
    out = _run_stdout(
        """
function main() -> i32 {
    print:
        JavaScript interpolation looks like $${value}
    return 0
}
"""
    )
    assert out == "JavaScript interpolation looks like ${value}"


def test_unterminated_interpolation_errors():
    with pytest.raises(SyntaxError):
        _gen_c(
            """
function main() -> i32 {
    print:
        broken ${name
    return 0
}
"""
        )


def test_empty_interpolation_errors():
    with pytest.raises(SyntaxError):
        _gen_c(
            """
function main() -> i32 {
    print:
        empty ${}
    return 0
}
"""
        )
