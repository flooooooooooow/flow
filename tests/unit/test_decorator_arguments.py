"""Decorator arguments accept numbers and keywords, not only bare words.

`docs/language/safety-profiles.md` says every `while` under a safety profile
must carry `@max_iterations(N)`, and the parser rejected the documented form
with "Expected decorator argument, got TokenType.NUMBER". A safety-critical
annotation the front end could not parse. See issue #586.

The `name=value` form parses too, so the general decorator grammar carries
the Python export surface #592 describes rather than needing a target-specific
escape hatch. Parsing only; #592 stays open for the behaviour.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

from flow.parser import Lexer, Parser
from tests.unit.compiler_helpers import to_c

ROOT = Path(__file__).resolve().parents[2]


def parse(source: str):
    return Parser(Lexer(textwrap.dedent(source))).parse()


def test_a_numeric_argument_parses():
    decls = parse("""
        function main() -> i32 {
            let mut i: i32 = 0
            @max_iterations(1000)
            while i < 10 { i = i + 1 }
            return i
        }
    """)
    loop = next(
        st for st in decls[0].body.statements
        if type(st).__name__ == "WhileStatement"
    )
    assert loop.max_iterations == 1000


def test_a_keyword_argument_parses():
    decls = parse("""
        @python(name="py_sqrt")
        function sqrt2(x: f64) -> f64 { return x }
    """)
    assert decls, "declaration was dropped"


def test_a_string_argument_still_parses():
    decls = parse("""
        @target("wasm32")
        function only_wasm() -> i32 { return 0 }
    """)
    assert decls, "declaration was dropped"


def test_the_bound_survives_monomorphization_and_reaches_the_c_backend():
    """The parser set the bound and monomorphize dropped it rebuilding the loop,
    so the counter the safety profiles promise was never emitted."""
    c = to_c("""
        function main() -> i32 {
            let mut i: i32 = 0
            @max_iterations(1000)
            while i < 10 { i = i + 1 }
            return i
        }
    """)
    assert "__flow_while_bound_1" in c, c[-1500:]
    assert "while exceeded @max_iterations(1000)" in c


@pytest.mark.skipif(not shutil.which("cc"), reason="needs a C compiler")
def test_the_counter_stops_a_loop_that_exceeds_its_bound(tmp_path):
    src = tmp_path / "bound.flow"
    src.write_text(textwrap.dedent("""
        function main() -> i32 {
            let mut i: i32 = 0
            @max_iterations(5)
            while i < 1000000 { i = i + 1 }
            return i
        }
    """))
    run = subprocess.run(
        ["./flow", "run", str(src)],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "FLOW_HOST": "python"},
    )
    combined = run.stdout + run.stderr
    assert "while exceeded @max_iterations(5)" in combined, combined[-2000:]
