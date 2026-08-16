"""Tail-call optimization must never swallow extern / @cEmbed shim calls.

Regression tests for https://github.com/flooooooooooow/flow/issues/517.

The TCO pass rewrites a self-recursive call in tail position into parameter
reassignment inside a ``for(;;)`` loop. It identified self-calls by a loose
prefix match (``fn_name + "_"``), so an extern shim whose declared name
started with the wrapper's name (e.g. ``foo_get_c`` inside ``foo_get``) was
mistaken for recursion and compiled into an infinite ``for(;;) { }`` loop that
never called the shim. Self-calls are now recognized by exact equality against
the function's own names (unmangled source name and mangled C name).
"""

from tests.unit.compiler_helpers import to_c, compile_and_run


def _body(c: str, fn: str) -> str:
    """Extract the body of a generated C function ('' if not found)."""
    import re

    m = re.search(r"\b%s\([^)]*\) \{(.*?)\n\}" % fn, c, re.S)
    return m.group(1) if m else ""


def test_extern_shim_tail_call_emits_real_call():
    """#517: ``return foo_get_c(i)`` must stay a real call, not a loop."""
    c = to_c(
        """
@cEmbed("static inline int32_t foo_get_c_c(int32_t i) { return i + 1; }")
extern {
    function foo_get_c_c(i: i32) -> i32
}

export function foo_get(i: i32) -> i32 {
    return foo_get_c_c(i)
}
"""
    )
    body = _body(c, r"foo_get_i32")
    assert "foo_get_c_c(i)" in body, f"shim call missing:\n{body}"
    assert "for (;;)" not in body, f"shim call miscompiled as TCO loop:\n{body}"


def test_shim_tail_call_runs_correctly():
    """The wrapper actually calls the shim and returns its value."""
    code = compile_and_run(
        """
@cEmbed("static inline int32_t bar_get_c_c(int32_t i) { return i * 3; }")
extern {
    function bar_get_c_c(i: i32) -> i32
}

export function main() -> i32 {
    return bar_get_c_c(7)
}
"""
    )
    assert code == 21, f"expected shim to return 21, got {code}"


def test_genuine_tail_recursion_still_tco():
    """Real self-recursion in tail position must still become a loop."""
    c = to_c(
        """
export function countdown(n: i32) -> i32 {
    if n <= 0 {
        return 0
    } else {
        return countdown(n - 1)
    }
}
"""
    )
    body = _body(c, r"countdown_i32")
    assert "for (;;)" in body, f"genuine recursion lost its TCO loop:\n{body}"
    assert "continue;" in body


def test_deep_tail_recursion_runs_without_stack_overflow():
    """TCO keeps a 1M-deep recursion constant-stack."""
    code = compile_and_run(
        """
export function down_to(n: i32) -> i32 {
    if n <= 0 {
        return 0
    } else {
        return down_to(n - 1)
    }
}

export function main() -> i32 {
    return down_to(1000000)
}
""",
        extra_cflags=["-O1"],
    )
    assert code == 0, f"deep recursion should finish with 0, got {code}"


def test_mangled_self_call_in_tail_position():
    """A call referencing the function's mangled C name is still a self-call."""
    c = to_c(
        """
export function step(n: i32) -> i32 {
    if n <= 0 {
        return 0
    } else {
        return step(n - 2)
    }
}
"""
    )
    body = _body(c, r"step_i32")
    assert "for (;;)" in body, f"mangled self-call lost its TCO loop:\n{body}"
