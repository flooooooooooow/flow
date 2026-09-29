import pytest
import subprocess
import os
import shutil

@pytest.mark.skipif(
    any(shutil.which(tool) is None for tool in ("mlir-opt", "mlir-translate", "clang")),
    reason="requires LLVM/MLIR command-line tools",
)
def test_mlir_math_intrinsic_override(tmp_path):
    """
    Test that a user-defined function named identically to a math intrinsic
    is called correctly, instead of lowering to the math dialect.
    Regression test for #874.
    """
    code = """
function exp(x: f32) -> f32 {
    return 42.0;
}

function main() -> i32 {
    let result = exp(0.0);
    if result == 42.0 {
        return 0;
    }
    return 1;
}
"""
    file_path = tmp_path / "math_override.flow"
    file_path.write_text(code)
    
    env = os.environ.copy()
    flow = os.path.join(os.path.dirname(__file__), "..", "..", "flow")

    # Test C backend
    c_res = subprocess.run([flow, "run", str(file_path), "--backend=c", "--json"], cwd=".", env=env, capture_output=True, text=True)
    assert c_res.returncode == 0, f"C backend failed math override test\\nstdout: {c_res.stdout}\\nstderr: {c_res.stderr}"
    
    # Test MLIR backend
    mlir_res = subprocess.run([flow, "run", str(file_path), "--backend=mlir", "--json"], cwd=".", env=env, capture_output=True, text=True)
    assert mlir_res.returncode == 0, f"MLIR backend failed math override test\\nstdout: {mlir_res.stdout}\\nstderr: {mlir_res.stderr}"
