"""
Working test for transpiler integration.
"""

import pytest
import subprocess
import tempfile
import os
from pathlib import Path


def test_simple_transpilation():
    """Test that simple FLOW code transpiles to MLIR."""
    flow_code = """
    function main() -> i32 {
        return 42
    }
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".flow", delete=False) as f:
        f.write(flow_code)
        input_file = f.name

    try:
        # Run transpiler
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

        assert result.returncode == 0, f"Transpilation failed: {result.stderr}"
        assert "Generated MLIR written to" in result.stderr

        # Check output file exists
        output_file = input_file.replace(".flow", ".mlir")
        assert os.path.exists(output_file)

        with open(output_file, "r") as f:
            mlir_content = f.read()
            assert "func.func @main" in mlir_content
            assert "42" in mlir_content

    finally:
        # Cleanup
        for f in [input_file, input_file.replace(".flow", ".mlir")]:
            if os.path.exists(f):
                os.remove(f)
