import pytest

from flow.dynamics_dsl import expand_dynamics_dsl, parse_dynamics_dsl


def test_dsys_expansion_preserves_single_line_main_body() -> None:
    source = """
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

    expanded = expand_dynamics_dsl(source)

    assert "# --- end dsys DSL expansion ---\n return 0 }" in expanded


def test_dsys_rejects_wrong_matrix_length_before_codegen() -> None:
    source = """
dsys bloch {
    discrete
    dt 1.0
    n 2 m 1 p 1
    A 0.0
    B 0.0 0.0
    C 1.0 0.0
}
"""

    with pytest.raises(
        SyntaxError,
        match=r"dsys 'bloch': A needs 4 entries for n = 2, got 1",
    ):
        parse_dynamics_dsl(source)


def test_dsys_rejects_non_positive_dimensions() -> None:
    source = """
dsys invalid {
    discrete
    dt 1.0
    n 0 m 1 p 1
    A 0.0
    B 0.0
    C 0.0
}
"""

    with pytest.raises(
        SyntaxError,
        match=r"dsys 'invalid': n must be positive, got 0",
    ):
        parse_dynamics_dsl(source)
