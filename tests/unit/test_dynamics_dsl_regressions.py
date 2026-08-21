"""Regression coverage for Flow dynamics DSL diagnostics."""

import pytest

from flow.dynamics_dsl import expand_dynamics_dsl, parse_dynamics_dsl


SINGLE_LINE_MAIN = """
dsys plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon rollout finite 50

sense on plant {
    controllable -> plant_ok
    spectral -> rho_open
}

function main() -> i32 { return 0 }
"""


def test_expansion_keeps_setup_separate_from_single_line_main_body():
    expanded = expand_dynamics_dsl(SINGLE_LINE_MAIN)
    assert "# --- end dsys DSL expansion ---\n return 0 }" in expanded


@pytest.mark.parametrize(
    ("matrix_line", "message"),
    [
        ("A 0.0", "A needs 4 entries for n = 2, got 1"),
        ("B 0.0", "B needs 2 entries for n = 2, m = 1, got 1"),
        ("C 1.0", "C needs 2 entries for p = 1, n = 2, got 1"),
    ],
)
def test_dsys_rejects_wrong_matrix_lengths(matrix_line: str, message: str):
    lines = {
        "A": "A 1.0 0.1 0.0 1.0",
        "B": "B 0.0 0.1",
        "C": "C 1.0 0.0",
    }
    lines[matrix_line[0]] = matrix_line
    source = f"""
dsys bloch {{
    discrete
    dt 1.0
    n 2 m 1 p 1
    {lines['A']}
    {lines['B']}
    {lines['C']}
}}
"""

    with pytest.raises(SyntaxError, match=message.replace("=", r"\=")):
        parse_dynamics_dsl(source)
