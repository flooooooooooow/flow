"""Decorator arguments accept numbers and keywords as well as bare words.

`docs/language/safety-profiles.md` says every `while` under a safety profile
must carry `@max_iterations(N)`, and the parser rejected the documented form
with "Expected decorator argument, got TokenType.NUMBER". A safety-critical
annotation the front end could not parse. See issue #586.

The `name=value` form parses too, so the general decorator grammar carries
the Python export surface #592 describes rather than needing a target-specific
escape hatch. Parsing only; #592 stays open for the behaviour.
"""

from __future__ import annotations

import textwrap

from flow.parser import Lexer, Parser


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


# test_the_bound_survives_monomorphization_and_reaches_the_c_backend ->
# tests/cgen/decorator_arguments_max_iterations.flow (checked against flowc).
# test_the_counter_stops_a_loop_that_exceeds_its_bound ->
# tests/lang/test_max_iterations_abort.flow (.exitcode 134, .expected-stderr).
