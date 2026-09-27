import pytest

from flow import dynamics_dsl as _dsl
from flow._dynamics_dsl_fixes import (
    _inject_dynamics_setup,
    _parse_dynamics_dsl,
    _validate_raw_dsys,
    install,
)


def test_validate_raw_dsys_valid() -> None:
    program = _dsl.DynamicsProgram()
    program.systems["sys1"] = _dsl.DsysDecl(
        name="sys1",
        mode="discrete",
        dt=0.1,
        n=2,
        m=1,
        p=1,
        A=[1.0, 0.0, 0.0, 1.0],
        B=[0.0, 1.0],
        C=[1.0, 0.0],
    )
    _validate_raw_dsys(program)


def test_validate_raw_dsys_synthesized_skipped() -> None:
    program = _dsl.DynamicsProgram()
    program.represents.append(
        _dsl.RepresentLinearDecl(flow_name="Pendulum", n=2, m=1, p=1)
    )
    # Synthesized system name is Pendulum_lin, which can have invalid dimensions or matrices in systems dict
    # without triggering _validate_raw_dsys errors.
    program.systems["Pendulum_lin"] = _dsl.DsysDecl(
        name="Pendulum_lin",
        mode="continuous",
        dt=0.01,
        n=0,
        m=-1,
        p=0,
        A=[],
        B=[],
        C=[],
    )
    _validate_raw_dsys(program)


def test_validate_raw_dsys_invalid_n() -> None:
    program = _dsl.DynamicsProgram()
    program.systems["bad_n"] = _dsl.DsysDecl(
        name="bad_n",
        mode="discrete",
        dt=0.1,
        n=0,
        m=1,
        p=1,
        A=[],
        B=[],
        C=[],
    )
    with pytest.raises(SyntaxError, match=r"dsys 'bad_n': n must be positive, got 0"):
        _validate_raw_dsys(program)


def test_validate_raw_dsys_invalid_m() -> None:
    program = _dsl.DynamicsProgram()
    program.systems["bad_m"] = _dsl.DsysDecl(
        name="bad_m",
        mode="discrete",
        dt=0.1,
        n=2,
        m=-1,
        p=1,
        A=[],
        B=[],
        C=[],
    )
    with pytest.raises(SyntaxError, match=r"dsys 'bad_m': m must be non-negative, got -1"):
        _validate_raw_dsys(program)


def test_validate_raw_dsys_invalid_p() -> None:
    program = _dsl.DynamicsProgram()
    program.systems["bad_p"] = _dsl.DsysDecl(
        name="bad_p",
        mode="discrete",
        dt=0.1,
        n=2,
        m=1,
        p=0,
        A=[],
        B=[],
        C=[],
    )
    with pytest.raises(SyntaxError, match=r"dsys 'bad_p': p must be positive, got 0"):
        _validate_raw_dsys(program)


def test_validate_raw_dsys_schematic_skipped() -> None:
    program = _dsl.DynamicsProgram()
    program.systems["schematic"] = _dsl.DsysDecl(
        name="schematic",
        mode="discrete",
        dt=0.1,
        n=2,
        m=1,
        p=1,
        A=[],
        B=[],
        C=[],
    )
    _validate_raw_dsys(program)


def test_validate_raw_dsys_wrong_matrix_length() -> None:
    # Wrong A length
    program = _dsl.DynamicsProgram()
    program.systems["bad_A"] = _dsl.DsysDecl(
        name="bad_A",
        mode="discrete",
        dt=0.1,
        n=2,
        m=1,
        p=1,
        A=[1.0],  # expected 2*2 = 4
        B=[0.0, 1.0],
        C=[1.0, 0.0],
    )
    with pytest.raises(
        SyntaxError, match=r"dsys 'bad_A': A needs 4 entries for n = 2, got 1"
    ):
        _validate_raw_dsys(program)

    # Wrong B length
    program = _dsl.DynamicsProgram()
    program.systems["bad_B"] = _dsl.DsysDecl(
        name="bad_B",
        mode="discrete",
        dt=0.1,
        n=2,
        m=1,
        p=1,
        A=[1.0, 0.0, 0.0, 1.0],
        B=[0.0],  # expected 2*1 = 2
        C=[1.0, 0.0],
    )
    with pytest.raises(
        SyntaxError, match=r"dsys 'bad_B': B needs 2 entries for n = 2, m = 1, got 1"
    ):
        _validate_raw_dsys(program)

    # Wrong C length
    program = _dsl.DynamicsProgram()
    program.systems["bad_C"] = _dsl.DsysDecl(
        name="bad_C",
        mode="discrete",
        dt=0.1,
        n=2,
        m=1,
        p=1,
        A=[1.0, 0.0, 0.0, 1.0],
        B=[0.0, 1.0],
        C=[1.0],  # expected 1*2 = 2
    )
    with pytest.raises(
        SyntaxError, match=r"dsys 'bad_C': C needs 2 entries for p = 1, n = 2, got 1"
    ):
        _validate_raw_dsys(program)


def test_parse_dynamics_dsl_wrapper() -> None:
    source = """
dsys plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.0 0.0 1.0
    B 0.0 1.0
    C 1.0 0.0
}
"""
    program, stripped = _parse_dynamics_dsl(source)
    assert "plant" in program.systems


def test_inject_dynamics_setup_empty() -> None:
    source = "function main() -> i32 { return 0 }"
    assert _inject_dynamics_setup(source, "") == source
    assert _inject_dynamics_setup(source, "   \n  ") == source


def test_inject_dynamics_setup_with_main() -> None:
    source = "function main() -> i32 {\n    return 0\n}"
    setup = "    let x: i32 = 42"
    res = _inject_dynamics_setup(source, setup)
    assert "function main() -> i32 {\n" + setup + "\n" in res


def test_inject_dynamics_setup_without_main() -> None:
    source = "let x: i32 = 10"
    setup = "    let y: i32 = 20"
    res = _inject_dynamics_setup(source, setup)
    expected = source + "\n\nfunction main() -> i32 {\n" + setup + "\n    return 0\n}\n"
    assert res == expected


def test_install_idempotent() -> None:
    install()
    install()
    assert _dsl.parse_dynamics_dsl == _parse_dynamics_dsl
    assert _dsl.inject_dynamics_setup == _inject_dynamics_setup
