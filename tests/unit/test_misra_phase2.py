"""Phase 2 MISRA: @safe/@unsafe, extern, analyze, reproducible C."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker
from flow.misra_scan import scan_c_source


# test_reproducible_c_emit is gone with the Python C backend. flowc emit is
# deterministic by construction: bootstrap_from_c.sh --verify checks the
# compiler reproduces its own C byte for byte.


def test_unsafe_required_on_extern_under_safety():
    code = """
    extern {
        function system(cmd: string) -> i32
    }
    function main() -> i32 { return 0 }
    """
    env_profile = os.environ.get("FLOW_PROFILE")
    os.environ["FLOW_PROFILE"] = "safety"
    try:
        tc = TypeChecker()
        tc.strict = True
        result = tc.check(parse_flow_code(code))
        assert any("@unsafe" in e for e in result.errors)
    finally:
        if env_profile is None:
            os.environ.pop("FLOW_PROFILE", None)
        else:
            os.environ["FLOW_PROFILE"] = env_profile


def test_unsafe_extern_ok_under_safety():
    code = """
    @unsafe
    extern {
        function memcpy(dst: ptr<void>, src: ptr<void>, n: i64) -> ptr<void>
    }
    function main() -> i32 { return 0 }
    """
    env_profile = os.environ.get("FLOW_PROFILE")
    os.environ["FLOW_PROFILE"] = "safety"
    try:
        tc = TypeChecker()
        tc.strict = True
        result = tc.check(parse_flow_code(code))
        assert not any("@unsafe" in e and "requires" in e for e in result.errors)
    finally:
        if env_profile is None:
            os.environ.pop("FLOW_PROFILE", None)
        else:
            os.environ["FLOW_PROFILE"] = env_profile


def test_safe_cannot_call_unsafe():
    code = """
    @unsafe
    function evil() -> i32 { return 0 }
    @safe
    function good() -> i32 { return evil() }
    function main() -> i32 { return good() }
    """
    tc = TypeChecker()
    tc.strict = True
    result = tc.check(parse_flow_code(code))
    assert any("Safety boundary" in e for e in result.errors)


def test_misra_scan_flags_malloc():
    findings = scan_c_source("void* p = malloc(16);\n")
    assert any(f.rule == "MISRA 21.3" for f in findings)


# test_checked_arith_smoke_runs -> tests/lang/test_basics_smokes.flow.


def test_show_flags_safety_implicit_error():
    r = subprocess.run(
        [str(ROOT / "flow"), "show-flags", "--profile=safety"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "-Werror=implicit-function-declaration" in r.stdout
