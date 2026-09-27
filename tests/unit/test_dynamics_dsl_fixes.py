"""Tests for src/flow/_dynamics_dsl_fixes.py."""

import pytest

import flow._dynamics_dsl_fixes as fixes
from flow.dynamics_dsl import (
    DsysDecl,
    DynamicsProgram,
    RepresentLinearDecl,
)


class TestValidateRawDsys:
    def test_valid_dsys_passes(self) -> None:
        program = DynamicsProgram()
        program.systems["sys1"] = DsysDecl(
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
        fixes._validate_raw_dsys(program)

    def test_synthesized_dsys_skipped(self) -> None:
        program = DynamicsProgram()
        rep = RepresentLinearDecl(flow_name="Plant")
        program.represents.append(rep)
        # Synthesized name is Plant_lin. Invalid dimensions on system should be skipped.
        program.systems["Plant_lin"] = DsysDecl(
            name="Plant_lin",
            mode="discrete",
            dt=0.1,
            n=-1,
            m=-1,
            p=-1,
            A=[],
            B=[],
            C=[],
        )
        fixes._validate_raw_dsys(program)

    def test_schematic_dsys_without_matrices_passes(self) -> None:
        program = DynamicsProgram()
        program.systems["schematic"] = DsysDecl(
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
        fixes._validate_raw_dsys(program)

    def test_invalid_n_raises(self) -> None:
        program = DynamicsProgram()
        program.systems["bad_n"] = DsysDecl(
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
        with pytest.raises(SyntaxError, match="dsys 'bad_n': n must be positive, got 0"):
            fixes._validate_raw_dsys(program)

    def test_invalid_m_raises(self) -> None:
        program = DynamicsProgram()
        program.systems["bad_m"] = DsysDecl(
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
        with pytest.raises(SyntaxError, match="dsys 'bad_m': m must be non-negative, got -1"):
            fixes._validate_raw_dsys(program)

    def test_invalid_p_raises(self) -> None:
        program = DynamicsProgram()
        program.systems["bad_p"] = DsysDecl(
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
        with pytest.raises(SyntaxError, match="dsys 'bad_p': p must be positive, got 0"):
            fixes._validate_raw_dsys(program)

    def test_matrix_a_wrong_length(self) -> None:
        program = DynamicsProgram()
        program.systems["sys_a"] = DsysDecl(
            name="sys_a",
            mode="discrete",
            dt=0.1,
            n=2,
            m=1,
            p=1,
            A=[1.0, 0.0],  # expected 4
            B=[0.0, 1.0],
            C=[1.0, 0.0],
        )
        with pytest.raises(
            SyntaxError,
            match=r"dsys 'sys_a': A needs 4 entries for n = 2, got 2",
        ):
            fixes._validate_raw_dsys(program)

    def test_matrix_b_wrong_length(self) -> None:
        program = DynamicsProgram()
        program.systems["sys_b"] = DsysDecl(
            name="sys_b",
            mode="discrete",
            dt=0.1,
            n=2,
            m=2,
            p=1,
            A=[1.0, 0.0, 0.0, 1.0],
            B=[0.0, 1.0],  # expected 2*2=4
            C=[1.0, 0.0],
        )
        with pytest.raises(
            SyntaxError,
            match=r"dsys 'sys_b': B needs 4 entries for n = 2, m = 2, got 2",
        ):
            fixes._validate_raw_dsys(program)

    def test_matrix_c_wrong_length(self) -> None:
        program = DynamicsProgram()
        program.systems["sys_c"] = DsysDecl(
            name="sys_c",
            mode="discrete",
            dt=0.1,
            n=2,
            m=1,
            p=2,
            A=[1.0, 0.0, 0.0, 1.0],
            B=[0.0, 1.0],
            C=[1.0, 0.0],  # expected 2*2=4
        )
        with pytest.raises(
            SyntaxError,
            match=r"dsys 'sys_c': C needs 4 entries for p = 2, n = 2, got 2",
        ):
            fixes._validate_raw_dsys(program)


class TestInjectDynamicsSetup:
    def test_empty_setup_returns_original_source(self) -> None:
        source = "function main() -> i32 { return 0 }"
        assert fixes._inject_dynamics_setup(source, "   ") == source

    def test_injects_into_existing_main(self) -> None:
        source = "function main() -> i32 {\n    return 0\n}"
        setup = "    let x: i32 = 1"
        result = fixes._inject_dynamics_setup(source, setup)
        assert result == "function main() -> i32 {\n    let x: i32 = 1\n\n    return 0\n}"

    def test_injects_into_existing_main_with_params(self) -> None:
        source = "function main(args: array<string>) -> i32 {\n    return 0\n}"
        setup = "    let x: i32 = 1"
        result = fixes._inject_dynamics_setup(source, setup)
        assert "function main(args: array<string>) -> i32 {\n" + setup in result

    def test_creates_synthetic_main_when_missing(self) -> None:
        source = "let global_var: i32 = 42"
        setup = "    let x: i32 = 1"
        result = fixes._inject_dynamics_setup(source, setup)
        expected = (
            source
            + "\n\nfunction main() -> i32 {\n"
            + setup
            + "\n    return 0\n}\n"
        )
        assert result == expected


class TestInstall:
    def test_install_monkey_patches_and_is_idempotent(self) -> None:
        import flow.dynamics_dsl as dsl

        assert fixes._INSTALLED is True
        assert dsl.parse_dynamics_dsl.__name__ == "_parse_dynamics_dsl"
        assert dsl.inject_dynamics_setup.__name__ == "_inject_dynamics_setup"

        # Calling install() again should be a no-op
        fixes.install()
        assert fixes._INSTALLED is True
