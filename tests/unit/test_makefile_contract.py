from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"


def test_makefile_delegates_build_commands_to_flow_cli():
    text = MAKEFILE.read_text()

    assert "python3 -m flow.transpiler" not in text
    assert "/opt/homebrew/opt/llvm" not in text
    assert "$(FLOW) run" in text
    assert "$(FLOW) compile" in text
    assert "$(FLOW) mlir" in text
    assert "$(FLOW) test --compiler --strict --tier2" in text


def test_makefile_does_not_restore_a_second_test_manifest():
    text = MAKEFILE.read_text()

    assert "tests/test_simple.flow" not in text
    assert "tests/test_control.flow" not in text
    assert "test-stdlib: test" in text
