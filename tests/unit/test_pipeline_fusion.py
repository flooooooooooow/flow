"""Tests for compile-time pipeline fusion of adjacent |> stages."""
import os
import tempfile
import warnings
import pytest

from flow.transpiler import resolve_modules
from flow.type_checker import TypeChecker
from flow.c_generator import flow_to_c
from flow.monomorphize import monomorphize
from flow.pipeline_fusion import fuse_pipelines
from flow.parser import parse_flow_code, FunctionCall, Lambda

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _parse_and_fuse(source: str):
    """Parse source, run fusion, return declarations."""
    decls = parse_flow_code(source)
    return fuse_pipelines(decls)


def _to_c(source: str) -> str:
    """Full pipeline: parse, resolve imports, fuse, monomorphize, generate C."""
    cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        with tempfile.NamedTemporaryFile(suffix=".flow", mode="w", delete=False) as f:
            f.write(source)
            path = f.name
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            decls = resolve_modules(path)
    finally:
        os.chdir(cwd)
        os.unlink(path)
    decls = fuse_pipelines(decls)
    decls = monomorphize(decls)
    return flow_to_c(decls)


def test_map_map_fusion():
    """map_f32(map_f32(buf, n, f), n, g) fuses to single map_f32 call."""
    source = """
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> map_f32(4, |x: f32| -> f32 { return x * 2.0 })
                                   |> map_f32(4, |x: f32| -> f32 { return x + 1.0 })
        return 0
    }
    """
    c_code = _to_c(source)
    # Should have exactly one map_f32 call site (the fused one)
    map_call_sites = [l for l in c_code.split("\n")
                      if "map_f32_ptr_f32" in l and "= (float*)(map_f32" in l]
    assert len(map_call_sites) == 1, f"Expected 1 map_f32 call, got {len(map_call_sites)}: {map_call_sites}"


def test_scale_scale_fusion():
    """scale_f32(scale_f32(buf, n, a), n, b) fuses to scale_f32(buf, n, a*b)."""
    source = """
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> scale_f32(4, 2.0) |> scale_f32(4, 3.0)
        return 0
    }
    """
    c_code = _to_c(source)
    # Should have a*b in the generated code
    assert "2.0 * 3.0" in c_code or "6.0" in c_code, "scale fusion should produce a*b"
    scale_calls = [l for l in c_code.split("\n")
                   if "scale_f32" in l and "= (float*)(scale_f32" in l]
    assert len(scale_calls) == 1, f"Expected 1 scale_f32 call, got {len(scale_calls)}"


def test_offset_offset_fusion():
    """offset_f32(offset_f32(buf, n, a), n, b) fuses to offset_f32(buf, n, a+b)."""
    source = """
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> offset_f32(4, 1.0) |> offset_f32(4, 2.0)
        return 0
    }
    """
    c_code = _to_c(source)
    assert "1.0 + 2.0" in c_code or "3.0" in c_code, "offset fusion should produce a+b"


def test_no_fusion_for_different_functions():
    """map_f32(scale_f32(...)) should NOT fuse (different functions)."""
    source = """
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> scale_f32(4, 2.0) |> map_f32(4, |x: f32| -> f32 { return x + 1.0 })
        return 0
    }
    """
    c_code = _to_c(source)
    # Both calls should remain
    assert "scale_f32" in c_code
    assert "map_f32" in c_code


def test_fusion_preserves_correctness_map():
    """Fused map pipeline produces the same result as unfused."""
    source = """
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> map_f32(4, |x: f32| -> f32 { return x * 2.0 })
                                   |> map_f32(4, |x: f32| -> f32 { return x + 1.0 })
        let total: f32 = sum_f32(out, 4)
        println(total)
        return 0
    }
    """
    c_code = _to_c(source)
    # Write and compile
    import subprocess
    with tempfile.NamedTemporaryFile(suffix=".c", mode="w", delete=False) as f:
        f.write(c_code)
        c_path = f.name
    bin_path = c_path.replace(".c", "")
    result = subprocess.run(
        ["clang", "-std=c11", "-lm", c_path, "-o", bin_path],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"clang failed: {result.stderr}"
    result = subprocess.run([bin_path], capture_output=True, text=True)
    # [1,2,3,4] * 2 = [2,4,6,8], + 1 = [3,5,7,9], sum = 24
    assert "24" in result.stdout, f"Expected 24, got: {result.stdout}"
    os.unlink(c_path)
    os.unlink(bin_path)


def test_fusion_preserves_correctness_scale():
    """Fused scale pipeline produces the same result as unfused."""
    source = """
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> scale_f32(4, 2.0) |> scale_f32(4, 3.0)
        let total: f32 = sum_f32(out, 4)
        println(total)
        return 0
    }
    """
    c_code = _to_c(source)
    import subprocess
    with tempfile.NamedTemporaryFile(suffix=".c", mode="w", delete=False) as f:
        f.write(c_code)
        c_path = f.name
    bin_path = c_path.replace(".c", "")
    result = subprocess.run(
        ["clang", "-std=c11", "-lm", c_path, "-o", bin_path],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"clang failed: {result.stderr}"
    result = subprocess.run([bin_path], capture_output=True, text=True)
    # [1,2,3,4] * 2 * 3 = [6,12,18,24], sum = 60
    assert "60" in result.stdout, f"Expected 60, got: {result.stdout}"
    os.unlink(c_path)
    os.unlink(bin_path)


def test_triple_map_fusion():
    """Three adjacent map_f32 calls fuse to one."""
    source = """
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> map_f32(4, |x: f32| -> f32 { return x + 1.0 })
                                   |> map_f32(4, |x: f32| -> f32 { return x * 2.0 })
                                   |> map_f32(4, |x: f32| -> f32 { return x - 3.0 })
        return 0
    }
    """
    c_code = _to_c(source)
    map_calls = [l for l in c_code.split("\n")
                 if "map_f32_ptr_f32" in l and "= (float*)(map_f32" in l]
    assert len(map_calls) == 1, f"Expected 1 map_f32 call after triple fusion, got {len(map_calls)}"
