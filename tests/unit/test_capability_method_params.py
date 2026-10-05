"""Capability method bodies must know their own parameter types."""

from __future__ import annotations

from tests.unit.compiler_helpers import to_c

SOURCE = """
effect Progress {
    on_start(idx: i32, total: i32, label: string) -> void,
}

capability ConsoleProgress {
    effect Progress,
    function on_start(idx: i32, total: i32, label: string) -> void {
        print(idx)
        print(total)
        print(label)
    },
}

function main() -> i32 {
    handle Progress with ConsoleProgress {
        Progress.on_start(1, 5, "hello")
    }
    return 0
}
"""


def _body(c_source: str, signature: str) -> str:
    """The definition, not the forward declaration that shares its signature."""
    search = 0
    while True:
        start = c_source.index(signature, search)
        line_end = c_source.index("\n", start)
        if c_source[start:line_end].rstrip().endswith("{"):
            return c_source[start : c_source.index("\n}", start)]
        search = line_end


def test_capability_method_prints_use_the_parameter_types():
    """`print(n)` on an i32 parameter must not fall back to a float format.

    The body was generated without registering the method's own parameters, so
    every argument resolved as unknown and printed through "%g". On arm64 that
    reads a double out of an int slot, so a capability method printing its
    arguments printed garbage.
    """
    c = to_c(SOURCE)
    body = _body(c, "void ConsoleProgress_on_start(int32_t idx")
    assert '"%d", idx' in body, body
    assert '"%d", total' in body, body
    assert '"%s", label' in body, body
    assert "%g" not in body, body


def test_a_plain_function_and_a_capability_method_agree():
    """The same body in either position has to generate the same formats."""
    plain = to_c("""
function on_start(idx: i32, total: i32, label: string) -> void {
    print(idx)
    print(total)
    print(label)
}

function main() -> i32 {
    on_start(1, 5, "hi")
    return 0
}
""")
    cap = to_c(SOURCE)
    plain_body = _body(plain, "void on_start_i32_i32_string(int32_t idx")
    cap_body = _body(cap, "void ConsoleProgress_on_start(int32_t idx")
    formats = lambda b: [ln.strip() for ln in b.splitlines() if "FLOW_LOG" in ln]
    assert formats(plain_body) == formats(cap_body)
