"""Tests for DSP pipeline primitives and |> chaining."""
import os
import tempfile
import warnings
import pytest

from flow.transpiler import resolve_modules
from flow.type_checker import TypeChecker
from flow.c_generator import flow_to_c
from flow.monomorphize import monomorphize

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _errors(source: str):
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
    checker = TypeChecker()
    checker.strict = True
    return checker.check(decls).errors


def _to_c(source: str) -> str:
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
    decls = monomorphize(decls)
    return flow_to_c(decls)


def test_map_f32_typechecks():
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = map_f32(buf, 4, |x: f32| -> f32 { return x * 2.0 })
        return 0
    }
    """)


def test_map_f32_with_pipe():
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> map_f32(4, |x: f32| -> f32 { return x * 2.0 })
        return 0
    }
    """)


def test_chained_pipe():
    """buf |> map |> map type-checks."""
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> map_f32(4, |x: f32| -> f32 { return x * 2.0 })
                                   |> map_f32(4, |x: f32| -> f32 { return x + 1.0 })
        return 0
    }
    """)


def test_reduce_f32_typechecks():
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let total: f32 = reduce_f32(buf, 4, 0.0, |a: f32, b: f32| -> f32 { return a + b })
        return 0
    }
    """)


def test_scan_f32_typechecks():
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = scan_f32(buf, 4, 0.0, |a: f32, b: f32| -> f32 { return a + b })
        return 0
    }
    """)


def test_filter_f32_typechecks():
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out_n: i32 = 0
        let out: ptr<f32> = filter_f32(buf, 4, |x: f32| -> bool { return x > 2.0 }, &out_n)
        return 0
    }
    """)


def test_zip_with_f32_typechecks():
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let a: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let b: array<f32, 4> = [10.0, 20.0, 30.0, 40.0]
        let out: ptr<f32> = zip_with_f32(a, b, 4, |x: f32, y: f32| -> f32 { return x + y })
        return 0
    }
    """)


def test_scale_offset_clip_pipe():
    """buf |> scale |> offset |> clip type-checks."""
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 8> = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        let out: ptr<f32> = buf |> scale_f32(8, 2.0)
                                   |> offset_f32(8, 1.0)
                                   |> clip_f32(8, 0.0, 10.0)
        return 0
    }
    """)


def test_dsp_c_codegen():
    """Verify C is generated for DSP operations."""
    c_code = _to_c("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = buf |> map_f32(4, |x: f32| -> f32 { return x * 2.0 })
        let total: f32 = sum_f32(out, 4)
        return 0
    }
    """)
    assert "map_f32" in c_code
    assert "sum_f32" in c_code
    assert "lambda" in c_code


def test_f64_primitives_typecheck():
    assert not _errors("""
    import "stdlib/dsp.flow"
    function main() -> i32 {
        let buf: array<f64, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f64> = map_f64(buf, 4, |x: f64| -> f64 { return x * 2.0 })
        let total: f64 = sum_f64(out, 4)
        return 0
    }
    """)


def test_named_function_as_arg():
    """A named function (not a lambda) can be passed to a HOF parameter."""
    assert not _errors("""
    import "stdlib/dsp.flow"
    function double(x: f32) -> f32 { return x * 2.0 }
    function main() -> i32 {
        let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
        let out: ptr<f32> = map_f32(buf, 4, double)
        return 0
    }
    """)
