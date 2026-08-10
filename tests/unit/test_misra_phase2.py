"""Phase 2 MISRA: @safe/@unsafe, extern, FLOW_DIAG, analyze, reproducible C."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c
from flow.type_checker import TypeChecker
from flow.misra_scan import scan_c_source


def test_flow_diag_macro_emitted():
    c = flow_to_c(parse_flow_code("function main() -> i32 { return 1 / 1 }"))
    assert "FLOW_DIAG" in c
    assert 'FLOW_DIAG("flow: division by zero\\n")' in c or "FLOW_DIAG" in c


def test_reproducible_c_emit():
    code = """
    struct Point { x: i32, y: i32 }
    function add(a: i32, b: i32) -> i32 { return a + b }
    function main() -> i32 {
        let p: Point = Point { x: 1, y: 2 }
        return add(p.x, p.y)
    }
    """
    decls = parse_flow_code(code)
    a = flow_to_c(decls)
    b = flow_to_c(parse_flow_code(code))
    assert a == b


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


def test_checked_arith_smoke_runs():
    src = (ROOT / "examples" / "basics" / "checked_arith_smoke.flow").read_text()
    with tempfile.TemporaryDirectory() as td:
        c_path = Path(td) / "t.c"
        exe = Path(td) / "t"
        c_path.write_text(flow_to_c(parse_flow_code(src)))
        subprocess.check_call(["cc", "-O0", str(c_path), "-o", str(exe)])
        r = subprocess.run([str(exe)], check=False)
        assert r.returncode == 0


def test_show_flags_safety_implicit_error():
    r = subprocess.run(
        [str(ROOT / "flow"), "show-flags", "--profile=safety"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "-Werror=implicit-function-declaration" in r.stdout
