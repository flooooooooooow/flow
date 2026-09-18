"""Multi-part string concatenation joins once for the whole chain (issue #747).

A chain like `a + b + c + d` used to lower to nested flow_strcat calls,
which allocate a fresh buffer per join and recopy every prefix: an n-part
join did n-1 allocations and O(n^2) copying. A pure-string chain now lowers
to a single flow_strcatn call that sums the lengths once, allocates once, and
copies each part once.

Chains that stringify a numeric operand keep the nested flow_strcat path on
purpose. Each stringified value lives in a per-expression stack buffer whose
GCC statement-expression storage may be reused across sibling call arguments,
so the nested path stays correct because it copies each buffer to the heap
before the next is formed.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _gen(source: str) -> str:
    return flow_to_c(parse_flow_code(source))


def _return_line(source: str) -> str:
    return " ".join(l.strip() for l in _gen(source).splitlines() if "return" in l)


def test_pure_string_chain_uses_single_join():
    src = """
    function build(a: string, b: string, c: string, d: string) -> string {
        return a + b + c + d
    }
    function main() -> i32 { return 0 }
    """
    ret = [l.strip() for l in _gen(src).splitlines()
           if l.strip().startswith("return flow_strcat")]
    assert ret, "expected a string-concat return"
    line = ret[0]
    # Single N-way join over all four operands.
    assert "flow_strcatn(4, a, b, c, d)" in line, line
    # The quadratic nested-join tax is gone.
    assert "flow_strcat(flow_strcat(" not in line, line


def test_two_part_chain_keeps_plain_strcat():
    src = """
    function j(a: string, b: string) -> string { return a + b }
    function main() -> i32 { return 0 }
    """
    line = _return_line(src)
    assert "flow_strcat(a, b)" in line, line
    assert "flow_strcatn" not in line, line


def test_numeric_operand_chain_keeps_nested_strcat():
    # Two stringified numbers must not share one flow_strcatn call: keep the
    # nested path so each numeric buffer is copied to the heap in turn.
    src = """
    function f() -> string { return "x=" + 1 + " y=" + 2 }
    function main() -> i32 { return 0 }
    """
    line = _return_line(src)
    assert "flow_strcatn" not in line, line
    assert "flow_strcat(flow_strcat(" in line, line


def test_strcatn_helper_emitted_once():
    src = """
    function build(a: string, b: string, c: string) -> string { return a + b + c }
    function main() -> i32 { return 0 }
    """
    c = _gen(src)
    assert c.count("static char* flow_strcatn(") == 1, "helper should be defined once"
    assert "#include <stdarg.h>" in c
