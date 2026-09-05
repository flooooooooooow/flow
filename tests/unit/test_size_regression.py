import pytest
import os
import subprocess
import shutil

@pytest.mark.skipif(not shutil.which("strip") or not shutil.which("size"), reason="requires strip and size")
def test_hello_world_size_regression(tmp_path):
    env = dict(os.environ, FLOW_HOST='python')
    
    # Compile hello world
    prog = "examples/basics/hello_world.flow"
    subprocess.run(["./flow", "compile", prog], env=env, check=True)
    
    bin_path = "build/hello_world"
    
    # Strip binary
    subprocess.run(["strip", bin_path], check=True)
    
    size = os.stat(bin_path).st_size
    
    # Check that hello world binary is relatively small, e.g. under 200KB.
    # The current stripped size is around 80KB.
    # We set a generous upper limit to avoid flaky failures, but enough to catch huge regressions.
    max_size = 200 * 1024 
    
    assert size < max_size, f"hello_world stripped binary size {size} exceeds {max_size} bytes limit"
