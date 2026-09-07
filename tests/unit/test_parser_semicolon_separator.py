"""A semicolon may separate statements, including after a block.

`flow-audio`'s pro54 patch writes its voice loops on one line:

    while i < 8 { if slots[i].active { voices[i].bend = b }; i = i + 1 }

The block parser only ever expected a statement to start where a statement
starts, so the semicolon following `}` was handed to the expression parser and
came back as "Unexpected token in expression: TokenType.SEMICOLON". The whole
patch failed to compile on that one line.
"""

import pytest

from flow.parser import parse_flow_code


SEPARATED = [
    (
        "after a block",
        """
function main() -> i32 {
    let mut n: i32 = 0
    let mut i: i32 = 0
    while i < 8 { if i > 2 { n = n + 1 }; i = i + 1 }
    return n
}
""",
    ),
    (
        "between two plain statements",
        """
function main() -> i32 {
    let mut a: i32 = 0
    let mut b: i32 = 0
    a = 1; b = 2
    return a + b
}
""",
    ),
    (
        "after an indexed assignment",
        """
function main() -> i32 {
    let mut xs: array<i32, 4> = [0; 4]
    let mut i: i32 = 0
    while i < 4 { xs[i] = i; i = i + 1 }
    return xs[3]
}
""",
    ),
    (
        "trailing at the end of a block",
        """
function main() -> i32 {
    let n: i32 = 1;
    return n
}
""",
    ),
    (
        "doubled",
        """
function main() -> i32 {
    let mut n: i32 = 0
    n = 1;; n = n + 1
    return n
}
""",
    ),
    (
        "alone in a block",
        """
function main() -> i32 {
    if true { ; }
    return 0
}
""",
    ),
]


@pytest.mark.parametrize(
    "label,source", SEPARATED, ids=[label for label, _ in SEPARATED]
)
def test_semicolon_separates_statements(label, source):
    program = parse_flow_code(source)
    assert program is not None


def test_semicolon_does_not_swallow_the_following_statement():
    """Stepping over the separator must not drop what comes after it."""
    program = parse_flow_code(
        """
function main() -> i32 {
    let mut n: i32 = 0
    if true { n = n + 1 }; n = n + 10
    return n
}
"""
    )
    kinds = [type(s).__name__ for s in program[0].body.statements]
    # The assignment after the semicolon is the statement this regression
    # used to lose.
    assert kinds == ["VarDecl", "IfStatement", "Assignment", "ReturnStatement"]
