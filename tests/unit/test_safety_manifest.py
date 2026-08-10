"""Safety manifest generation tests (#271 / MISRA Phase 2).

The manifest collects safety facts from the AST, type checker, and C
generator state into a structured compliance report.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker
from flow.safety_manifest import generate_manifest


def _manifest(source: str, *, profile: str = "safety", overflow_check: bool = True):
    decls = parse_flow_code(source)
    tc = TypeChecker()
    result = tc.check(decls)
    return generate_manifest(
        decls,
        tc,
        source_file="<test>",
        profile=profile,
        overflow_check=overflow_check,
        type_errors=result.errors,
    )


def test_manifest_basic_properties():
    m = _manifest(
        """
        function main() -> i32 {
            return 0
        }
        """
    )
    assert m.function_count == 1
    assert m.profile == "safety"
    # A trivial program with no loops, no recursion, no heap
    assert m.recursive_functions == []
    assert m.heap_using_functions == []
    prop_names = {p.name for p in m.properties}
    assert "Integer overflow" in prop_names
    assert "Division by zero" in prop_names
    assert "Shift undefined behaviour" in prop_names
    assert "Dynamic allocation" in prop_names
    assert "Unbounded recursion" in prop_names


def test_manifest_detects_recursion():
    m = _manifest(
        """
        function fib(n: i32) -> i32 {
            if n <= 1 { return n }
            return fib(n - 1) + fib(n - 2)
        }
        function main() -> i32 { return fib(10) }
        """
    )
    assert "fib" in m.recursive_functions
    rec_prop = next(p for p in m.properties if p.name == "Unbounded recursion")
    assert rec_prop.status == "REQUIRES EVIDENCE"


def test_manifest_no_recursion_when_absent():
    m = _manifest(
        """
        function add(a: i32, b: i32) -> i32 { return a + b }
        function main() -> i32 { return add(1, 2) }
        """
    )
    assert m.recursive_functions == []
    rec_prop = next(p for p in m.properties if p.name == "Unbounded recursion")
    assert rec_prop.status == "PROVEN"


def test_manifest_detects_heap_usage():
    m = _manifest(
        """
        function alloc_helper() -> i32 {
            let p = malloc(40)
            return 0
        }
        function main() -> i32 { return alloc_helper() }
        """
    )
    assert "alloc_helper" in m.heap_using_functions
    assert "main" in m.heap_using_functions  # transitive
    alloc_prop = next(p for p in m.properties if p.name == "Dynamic allocation")
    assert alloc_prop.status == "REQUIRES EVIDENCE"


def test_manifest_no_heap_when_absent():
    m = _manifest(
        """
        function main() -> i32 { return 42 }
        """
    )
    assert m.heap_using_functions == []
    alloc_prop = next(p for p in m.properties if p.name == "Dynamic allocation")
    assert alloc_prop.status == "PROVEN"


def test_manifest_detects_loops():
    m = _manifest(
        """
        function sum(n: i32) -> i32 {
            let s: i32 = 0
            for i in 0..n {
                s = s + i
            }
            return s
        }
        function main() -> i32 { return sum(10) }
        """
    )
    loop_prop = next(p for p in m.properties if p.name == "Unbounded loops")
    assert loop_prop.status == "REQUIRES EVIDENCE"


def test_manifest_no_loops_when_absent():
    m = _manifest(
        """
        function main() -> i32 { return 0 }
        """
    )
    loop_prop = next(p for p in m.properties if p.name == "Unbounded loops")
    assert loop_prop.status == "PROVEN"


def test_manifest_rt_safe_function():
    m = _manifest(
        """
        @rt_safe
        function process(x: i32) -> i32 { return x * 2 }
        function main() -> i32 { return process(42) }
        """
    )
    assert "process" in m.rt_safe_functions
    rt_prop = next(p for p in m.properties if "RT-safety" in p.name)
    assert rt_prop.status == "PROVEN"


def test_manifest_overflow_proven_under_safety():
    m = _manifest(
        """
        function main() -> i32 { return 0 }
        """,
        profile="safety",
        overflow_check=True,
    )
    ovf_prop = next(p for p in m.properties if p.name == "Integer overflow")
    assert ovf_prop.status == "PROVEN"


def test_manifest_overflow_requires_evidence_default():
    m = _manifest(
        """
        function main() -> i32 { return 0 }
        """,
        profile="default",
        overflow_check=False,
    )
    ovf_prop = next(p for p in m.properties if p.name == "Integer overflow")
    assert ovf_prop.status == "REQUIRES EVIDENCE"


def test_manifest_div0_rejected():
    m = _manifest(
        """
        function main() -> i32 {
            return 10 / 0
        }
        """
    )
    div_prop = next(p for p in m.properties if p.name == "Division by zero")
    assert div_prop.status == "REJECTED"


def test_manifest_text_output():
    m = _manifest(
        """
        function main() -> i32 { return 0 }
        """
    )
    text = m.to_text()
    assert "Flow Safety Manifest" in text
    assert "Summary" in text
    assert "Proven:" in text


def test_manifest_json_output():
    m = _manifest(
        """
        function main() -> i32 { return 0 }
        """
    )
    data = json.loads(m.to_json())
    assert data["profile"] == "safety"
    assert data["functions"] == 1
    assert "properties" in data
    assert "summary" in data
    assert data["summary"]["proven"] >= 4
