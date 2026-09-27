"""Tests for flow._dynamics_dsl_fixes correctness guards."""

import pytest

from flow import dynamics_dsl as _dsl
from flow._dynamics_dsl_fixes import (
    _inject_dynamics_setup,
    _parse_dynamics_dsl,
    _validate_raw_dsys,
    install,
)


def create_dsys_decl(
    name="sys1",
    mode="discrete",
    dt=0.1,
    n=2,
    m=1,
    p=1,
    A=None,
    B=None,
    C=None,
):
    return _dsl.DsysDecl(
        name=name,
        mode=mode,
        dt=dt,
        n=n,
        m=m,
        p=p,
        A=A if A is not None else [1.0, 0.0, 0.0, 1.0],
        B=B if B is not None else [0.0, 1.0],
        C=C if C is not None else [1.0, 0.0],
    )


class TestValidateRawDsys:
    def test_valid_dsys_passes(self):
        program = _dsl.DynamicsProgram()
        program.systems["plant"] = create_dsys_decl(
            n=2, m=1, p=1, A=[1.0, 0.0, 0.0, 1.0], B=[0.0, 1.0], C=[1.0, 0.0]
        )
        _validate_raw_dsys(program)

    def test_synthesized_system_skipped(self):
        program = _dsl.DynamicsProgram()
        program.represents.append(_dsl.RepresentLinearDecl(flow_name="Pendulum"))
        # Pendulum_lin is synthesized; invalid dimensions should be skipped
        program.systems["Pendulum_lin"] = create_dsys_decl(
            name="Pendulum_lin", n=-1, m=-1, p=-1, A=[], B=[], C=[]
        )
        _validate_raw_dsys(program)

    def test_invalid_n_raises(self):
        program = _dsl.DynamicsProgram()
        program.systems["bad_n"] = create_dsys_decl(n=0)
        with pytest.raises(SyntaxError, match="dsys 'bad_n': n must be positive, got 0"):
            _validate_raw_dsys(program)

    def test_invalid_m_raises(self):
        program = _dsl.DynamicsProgram()
        program.systems["bad_m"] = create_dsys_decl(m=-1)
        with pytest.raises(SyntaxError, match="dsys 'bad_m': m must be non-negative, got -1"):
            _validate_raw_dsys(program)

    def test_invalid_p_raises(self):
        program = _dsl.DynamicsProgram()
        program.systems["bad_p"] = create_dsys_decl(p=-1)
        with pytest.raises(SyntaxError, match="dsys 'bad_p': p must be positive, got -1"):
            _validate_raw_dsys(program)

    def test_schematic_dsys_without_matrices_passes(self):
        program = _dsl.DynamicsProgram()
        program.systems["schematic"] = create_dsys_decl(
            n=2, m=1, p=1, A=[], B=[], C=[]
        )
        _validate_raw_dsys(program)

    def test_wrong_A_length_raises(self):
        program = _dsl.DynamicsProgram()
        program.systems["bad_A"] = create_dsys_decl(
            n=2, m=1, p=1, A=[1.0, 0.0], B=[0.0, 1.0], C=[1.0, 0.0]
        )
        with pytest.raises(SyntaxError, match="dsys 'bad_A': A needs 4 entries for n = 2, got 2"):
            _validate_raw_dsys(program)

    def test_wrong_B_length_raises(self):
        program = _dsl.DynamicsProgram()
        program.systems["bad_B"] = create_dsys_decl(
            n=2, m=1, p=1, A=[1.0, 0.0, 0.0, 1.0], B=[0.0], C=[1.0, 0.0]
        )
        with pytest.raises(SyntaxError, match="dsys 'bad_B': B needs 2 entries for n = 2, m = 1, got 1"):
            _validate_raw_dsys(program)

    def test_wrong_C_length_raises(self):
        program = _dsl.DynamicsProgram()
        program.systems["bad_C"] = create_dsys_decl(
            n=2, m=1, p=1, A=[1.0, 0.0, 0.0, 1.0], B=[0.0, 1.0], C=[1.0]
        )
        with pytest.raises(SyntaxError, match="dsys 'bad_C': C needs 2 entries for p = 1, n = 2, got 1"):
            _validate_raw_dsys(program)


class TestInjectDynamicsSetup:
    def test_empty_setup_returns_source(self):
        src = "function main() -> i32 { return 0 }"
        assert _inject_dynamics_setup(src, "") == src
        assert _inject_dynamics_setup(src, "   \n") == src

    def test_inject_into_existing_main(self):
        src = "function main() -> i32 {\n    return 0\n}\n"
        setup = "    let x = 1"
        res = _inject_dynamics_setup(src, setup)
        assert res == "function main() -> i32 {\n    let x = 1\n\n    return 0\n}\n"

    def test_inject_when_main_missing(self):
        src = "function foo() -> void {}"
        setup = "    let x = 1"
        res = _inject_dynamics_setup(src, setup)
        assert "function main() -> i32 {" in res
        assert "let x = 1" in res
        assert "return 0" in res


class TestParseDynamicsDSL:
    def test_parse_valid_source(self):
        src = """
dsys plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.0 0.0 1.0
    B 0.0 1.0
    C 1.0 0.0
}
function main() -> i32 { return 0 }
"""
        program, stripped = _parse_dynamics_dsl(src)
        assert "plant" in program.systems
        assert "dsys plant" not in stripped

    def test_parse_invalid_dsys_raises(self):
        src = """
dsys bad {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.0
    B 0.0 1.0
    C 1.0 0.0
}
function main() -> i32 { return 0 }
"""
        with pytest.raises(SyntaxError, match="dsys 'bad': A needs 4 entries"):
            _parse_dynamics_dsl(src)


class TestInstallFixes:
    def test_install_is_idempotent_and_patches_dsl(self):
        install()
        assert _dsl.parse_dynamics_dsl == _parse_dynamics_dsl
        assert _dsl.inject_dynamics_setup == _inject_dynamics_setup
        # Call install second time
        install()
        assert _dsl.parse_dynamics_dsl == _parse_dynamics_dsl
