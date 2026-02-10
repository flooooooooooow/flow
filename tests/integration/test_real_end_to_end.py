"""
End-to-end tests that validate the complete FLOW compilation pipeline.
These tests work with actual .flow files in the test suite.
"""

import pytest
import subprocess
import tempfile
import os
from pathlib import Path


class TestRealEndToEnd:
    """Test with actual FLOW files and real compilation."""

    def test_core_example_compilation(self):
        """Test that core examples actually compile."""
        core_dir = Path(__file__).parent.parent / "core"
        example_file = core_dir / "test_simple.flow"

        if example_file.exists():
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "flow.transpiler",
                    str(example_file),
                    "-o",
                    "/tmp/test_output.mlir",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent,
            )

            assert result.returncode == 0, f"Compilation failed: {result.stderr}"
            assert "Generated MLIR written to" in result.stderr

    def test_basic_math_compilation(self):
        """Test basic math operations compile."""
        flow_code = """
        function factorial(n: i32) -> i32 {
            if n <= 1 {
                return 1
            } else {
                return n * factorial(n - 1)
            }
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".flow", delete=False) as f:
            f.write(flow_code)
            input_file = f.name

        try:
            # Test compilation
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "flow.transpiler",
                    input_file,
                    "-o",
                    input_file.replace(".flow", ".mlir"),
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent,
            )

            assert result.returncode == 0
            assert "Parsed 1 functions" in result.stderr

            # Verify MLIR was generated
            output_file = input_file.replace(".flow", ".mlir")
            assert os.path.exists(output_file)

            with open(output_file, "r") as f:
                mlir_content = f.read()
                assert "func.func @factorial" in mlir_content
                assert "arith.muli" in mlir_content or "arith.subi" in mlir_content

        finally:
            # Cleanup
            for f in [input_file, input_file.replace(".flow", ".mlir")]:
                if os.path.exists(f):
                    os.remove(f)

    def test_c_backend_generation(self):
        """Test C backend generation."""
        flow_code = """
        function add(a: i32, b: i32) -> i32 {
            return a + b
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".flow", delete=False) as f:
            f.write(flow_code)
            input_file = f.name

        try:
            # Test C generation
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "flow.transpiler",
                    input_file,
                    "--c",
                    "-o",
                    input_file.replace(".flow", ".c"),
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent,
            )

            assert result.returncode == 0
            assert "Generated C" in result.stderr or "Generated" in result.stderr

            # Verify C code was generated
            output_file = input_file.replace(".flow", ".c")
            assert os.path.exists(output_file)

            with open(output_file, "r") as f:
                c_content = f.read()
                assert "add" in c_content

        finally:
            # Cleanup
            for f in [input_file, input_file.replace(".flow", ".c")]:
                if os.path.exists(f):
                    os.remove(f)

    def test_error_handling(self):
        """Test that errors are properly handled."""
        flow_code = """
        function broken( -> i32 {
            return 42
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".flow", delete=False) as f:
            f.write(flow_code)
            input_file = f.name

        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "flow.transpiler",
                    input_file,
                    "-o",
                    input_file.replace(".flow", ".mlir"),
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent,
            )

            # Should fail gracefully
            assert result.returncode != 0
            assert len(result.stderr) > 0

        finally:
            # Cleanup
            if os.path.exists(input_file):
                os.remove(input_file)


class TestCLIIntegration:
    """Test the enhanced flow CLI."""

    def test_flow_help_command(self):
        """Test flow help command."""
        result = subprocess.run(["./flow", "help"], capture_output=True, text=True)

        assert result.returncode == 0
        assert "test-python" in result.stdout
        assert "test-all" in result.stdout

    def test_flow_python_test_command(self):
        """Test flow Python test command."""
        result = subprocess.run(
            ["./flow", "test-python"], capture_output=True, text=True
        )

        # Should run pytest (may fail if tests don't pass)
        assert "test session starts" in result.stdout or "pytest" in result.stderr
