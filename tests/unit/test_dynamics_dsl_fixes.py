import pytest

import flow._dynamics_dsl_fixes as fixes
import flow.dynamics_dsl as dsl


def test_validate_raw_dsys_skips_synthesized_represents() -> None:
    # Synthesized represents create names like "{flow_name}_lin"
    rep = dsl.RepresentLinearDecl(
        flow_name="arm",
        at_point={"x": 1.0},
    )
    # The system name "arm_lin" is synthesized so _validate_raw_dsys should skip validation
    # even if dimensions are invalid (n=0, p=0)
    sys = dsl.DsysDecl(
        name="arm_lin",
        mode="discrete",
        dt=0.1,
        n=0,
        m=0,
        p=0,
        A=[],
        B=[],
        C=[],
    )
    program = dsl.DynamicsProgram(
        systems={"arm_lin": sys},
        represents=[rep],
    )
    # Should not raise SyntaxError
    fixes._validate_raw_dsys(program)


def test_validate_raw_dsys_invalid_dimensions() -> None:
    # Test n <= 0
    sys_n = dsl.DsysDecl(
        name="bad_n", mode="discrete", dt=0.1, n=0, m=1, p=1, A=[], B=[], C=[]
    )
    prog_n = dsl.DynamicsProgram(systems={"bad_n": sys_n})
    with pytest.raises(SyntaxError, match=r"dsys 'bad_n': n must be positive, got 0"):
        fixes._validate_raw_dsys(prog_n)

    # Test m < 0
    sys_m = dsl.DsysDecl(
        name="bad_m", mode="discrete", dt=0.1, n=1, m=-1, p=1, A=[], B=[], C=[]
    )
    prog_m = dsl.DynamicsProgram(systems={"bad_m": sys_m})
    with pytest.raises(SyntaxError, match=r"dsys 'bad_m': m must be non-negative, got -1"):
        fixes._validate_raw_dsys(prog_m)

    # Test p <= 0
    sys_p = dsl.DsysDecl(
        name="bad_p", mode="discrete", dt=0.1, n=1, m=1, p=0, A=[], B=[], C=[]
    )
    prog_p = dsl.DynamicsProgram(systems={"bad_p": sys_p})
    with pytest.raises(SyntaxError, match=r"dsys 'bad_p': p must be positive, got 0"):
        fixes._validate_raw_dsys(prog_p)


def test_validate_raw_dsys_schematic_form_without_matrices() -> None:
    # Declarations with no matrices (A, B, C empty) should be preserved without checking matrix lengths
    sys = dsl.DsysDecl(
        name="schematic", mode="discrete", dt=0.1, n=2, m=1, p=1, A=[], B=[], C=[]
    )
    prog = dsl.DynamicsProgram(systems={"schematic": sys})
    fixes._validate_raw_dsys(prog)


def test_validate_raw_dsys_wrong_matrix_lengths() -> None:
    # Matrix A mismatch
    sys_a = dsl.DsysDecl(
        name="sys", mode="discrete", dt=0.1, n=2, m=1, p=1, A=[1.0], B=[0.0, 0.0], C=[1.0, 0.0]
    )
    prog_a = dsl.DynamicsProgram(systems={"sys": sys_a})
    with pytest.raises(SyntaxError, match=r"dsys 'sys': A needs 4 entries for n = 2, got 1"):
        fixes._validate_raw_dsys(prog_a)

    # Matrix B mismatch
    sys_b = dsl.DsysDecl(
        name="sys", mode="discrete", dt=0.1, n=2, m=1, p=1, A=[1.0, 0.0, 0.0, 1.0], B=[0.0], C=[1.0, 0.0]
    )
    prog_b = dsl.DynamicsProgram(systems={"sys": sys_b})
    with pytest.raises(SyntaxError, match=r"dsys 'sys': B needs 2 entries for n = 2, m = 1, got 1"):
        fixes._validate_raw_dsys(prog_b)

    # Matrix C mismatch
    sys_c = dsl.DsysDecl(
        name="sys", mode="discrete", dt=0.1, n=2, m=1, p=1, A=[1.0, 0.0, 0.0, 1.0], B=[0.0, 0.1], C=[1.0]
    )
    prog_c = dsl.DynamicsProgram(systems={"sys": sys_c})
    with pytest.raises(SyntaxError, match=r"dsys 'sys': C needs 2 entries for p = 1, n = 2, got 1"):
        fixes._validate_raw_dsys(prog_c)


def test_parse_dynamics_dsl_validates_dsys() -> None:
    source = """
dsys invalid {
    discrete
    dt 1.0
    n 2 m 1 p 1
    A 1.0
    B 0.0 0.0
    C 1.0 0.0
}
"""
    with pytest.raises(SyntaxError, match=r"dsys 'invalid': A needs 4 entries for n = 2, got 1"):
        fixes._parse_dynamics_dsl(source)


def test_inject_dynamics_setup_empty_setup() -> None:
    flow_src = "function main() -> i32 { return 0 }"
    result = fixes._inject_dynamics_setup(flow_src, "   \n")
    assert result == flow_src


def test_inject_dynamics_setup_with_existing_main() -> None:
    flow_src = "function main() -> i32 {\n    return 0\n}"
    setup = "let x = 1"
    result = fixes._inject_dynamics_setup(flow_src, setup)
    assert "function main() -> i32 {\nlet x = 1\n\n    return 0\n}" == result


def test_inject_dynamics_setup_without_main() -> None:
    flow_src = "let g = 10"
    setup = "let x = 1"
    result = fixes._inject_dynamics_setup(flow_src, setup)
    expected = "let g = 10\n\nfunction main() -> i32 {\nlet x = 1\n    return 0\n}\n"
    assert result == expected


def test_install_monkey_patches_dsl() -> None:
    original_installed = fixes._INSTALLED
    fixes._INSTALLED = False
    try:
        fixes.install()
        assert dsl.parse_dynamics_dsl == fixes._parse_dynamics_dsl
        assert dsl.inject_dynamics_setup == fixes._inject_dynamics_setup
        assert fixes._INSTALLED is True

        # Test idempotency - second call should do nothing and remain installed
        fixes.install()
        assert fixes._INSTALLED is True
    finally:
        fixes._INSTALLED = original_installed
