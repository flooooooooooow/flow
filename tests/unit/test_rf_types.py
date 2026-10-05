"""Tests for RF/SDR types: IQ alias, IQSample distinct type, Signal<R> struct.

Signal<R> uses a phantom type parameter R to tag the sample rate at compile
time. signal_mix<R> requires both inputs to have the same R, so mixing
signals at different rates is a compile-time error.
"""
import os
import tempfile
import warnings
import pytest

from flow.parser import Lexer, Parser
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            declarations = resolve_modules(path)
    finally:
        os.chdir(cwd)
        os.unlink(path)
    declarations = monomorphize(declarations)
    return flow_to_c(declarations)


def test_iq_type_alias():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let z: IQ = iq(1.0, 2.0)
        return 0
    }
    """)


def test_iq_sample_distinct_type():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let s: IQSample = iq_sample(1.0, 2.0)
        return 0
    }
    """)


def test_iq_sample_requires_cast_from_c64():
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
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let z: c64 = c64(1.0, 2.0)
        let s: IQSample = z as IQSample
        return 0
    }
    """)


def test_signal_generic_struct():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let sig: Signal<Hz1000> = signal_new<Hz1000>(1024, 1000)
        signal_set<Hz1000>(sig, 0, c64(1.0, 0.0))
        let val: c64 = signal_get<Hz1000>(sig, 0)
        signal_free<Hz1000>(sig)
        return 0
    }
    """)


def test_signal_rate_and_length():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let sig: Signal<Hz48000> = signal_new<Hz48000>(256, 48000)
        let rate: u32 = signal_rate<Hz48000>(sig)
        let len: i32 = signal_length<Hz48000>(sig)
        signal_free<Hz48000>(sig)
        return 0
    }
    """)


def test_signal_mix_same_rate():
    """signal_mix with same rate type compiles."""
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let a: Signal<Hz44100> = signal_new<Hz44100>(64, 44100)
        let b: Signal<Hz44100> = signal_new<Hz44100>(64, 44100)
        let mixed: Signal<Hz44100> = signal_mix<Hz44100>(a, b)
        signal_free<Hz44100>(a)
        signal_free<Hz44100>(b)
        signal_free<Hz44100>(mixed)
        return 0
    }
    """)


def test_signal_mix_different_rate_rejected():
    """signal_mix with different rate types is a compile-time error."""
    errs = _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let a: Signal<Hz44100> = signal_new<Hz44100>(64, 44100)
        let b: Signal<Hz48000> = signal_new<Hz48000>(64, 48000)
        let mixed: Signal<Hz44100> = signal_mix<Hz44100>(a, b)
        signal_free<Hz44100>(a)
        signal_free<Hz48000>(b)
        signal_free<Hz44100>(mixed)
        return 0
    }
    """)
    assert any("signal_mix" in e or "Signal" in e or "overload" in e for e in errs), errs


def test_signal_scale():
    assert not _errors("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let sig: Signal<Hz44100> = signal_new<Hz44100>(64, 44100)
        signal_scale<Hz44100>(sig, 0.5)
        signal_free<Hz44100>(sig)
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
    c_code = _to_c("""
    import "stdlib/rf.flow"
    function main() -> i32 {
        let z: IQ = iq(1.0, 2.0)
        let s: IQSample = iq_sample(1.0, 2.0)
        let sig: Signal<Hz1000> = signal_new<Hz1000>(8, 1000)
        signal_free<Hz1000>(sig)
        return 0
    }
    """)
    assert "complex.h" in c_code
    assert "float complex" in c_code
    assert "IQ" in c_code or "IQSample" in c_code
    assert "Signal" in c_code
