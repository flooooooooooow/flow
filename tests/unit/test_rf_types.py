"""Tests for RF/SDR types: IQ alias, IQSample distinct type, Signal struct."""
import os
import tempfile
import pytest

from flow.transpiler import resolve_modules
from flow.type_checker import TypeChecker
from flow.c_generator import flow_to_c
from flow.monomorphize import monomorphize

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _errors(source: str):
    """Type-check source with module resolution (imports work)."""
    cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        with tempfile.NamedTemporaryFile(suffix=".flow", mode="w", delete=False) as f:
            f.write(source)
            path = f.name
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            declarations = resolve_modules(path)
    finally:
        os.chdir(cwd)
        os.unlink(path)
    checker = TypeChecker()
    checker.strict = True
    return checker.check(declarations).errors


def _to_c(source: str) -> str:
    """Transpile source to C with module resolution."""
    cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        with tempfile.NamedTemporaryFile(suffix=".flow", mode="w", delete=False) as f:
            f.write(source)
            path = f.name
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            declarations = resolve_modules(path)
    finally:
        os.chdir(cwd)
        os.unlink(path)
    declarations = monomorphize(declarations)
    return flow_to_c(declarations)


def test_iq_type_alias():
    """IQ is a transparent alias for c64."""
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let z: IQ = iq(1.0, 2.0)
        return 0
    }
    """)


def test_iq_sample_distinct_type():
    """IQSample is a distinct type from c64."""
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let s: IQSample = iq_sample(1.0, 2.0)
        return 0
    }
    """)


def test_iq_sample_requires_cast_from_c64():
    """c64 cannot be assigned to IQSample without an explicit cast."""
    errs = _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let z: c64 = c64(1.0, 2.0)
        let s: IQSample = z
        return 0
    }
    """)
    assert any("IQSample" in e or "Cannot" in e or "mismatch" in e for e in errs), errs


def test_iq_sample_cast_from_c64():
    """c64 can be explicitly cast to IQSample."""
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let z: c64 = c64(1.0, 2.0)
        let s: IQSample = z as IQSample
        return 0
    }
    """)


def test_signal_struct():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let sig: Signal = signal_new(1024, 1000000)
        signal_set(sig, 0, c64(1.0, 0.0))
        let val: c64 = signal_get(sig, 0)
        signal_free(sig)
        return 0
    }
    """)


def test_signal_rate_and_length():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let sig: Signal = signal_new(256, 48000)
        let rate: u32 = signal_rate(sig)
        let len: i32 = signal_length(sig)
        signal_free(sig)
        return 0
    }
    """)


def test_signal_mix_same_rate():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let a: Signal = signal_new(64, 44100)
        let b: Signal = signal_new(64, 44100)
        let mixed: Signal = signal_mix(a, b)
        signal_free(a)
        signal_free(b)
        signal_free(mixed)
        return 0
    }
    """)


def test_signal_scale():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let sig: Signal = signal_new(64, 44100)
        signal_scale(sig, 0.5)
        signal_free(sig)
        return 0
    }
    """)


def test_iq_constructors():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let z1: IQ = iq(1.0, 2.0)
        let z2: IQ = iq_from_real(3.0)
        let s1: IQSample = iq_sample(1.0, 2.0)
        let s2: IQSample = iq_sample_from_iq(z1)
        return 0
    }
    """)


def test_rf_c_codegen():
    """Verify the generated C has the right typedefs."""
    c_code = _to_c("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let z: IQ = iq(1.0, 2.0)
        let s: IQSample = iq_sample(1.0, 2.0)
        return 0
    }
    """)
    assert "complex.h" in c_code
    assert "float complex" in c_code
    assert "IQ" in c_code
    assert "IQSample" in c_code
