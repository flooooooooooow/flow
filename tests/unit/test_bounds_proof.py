"""The bounds prover: what it discharges, what it refuses, and what it must never do.

The cases that matter are the ones where being wrong is silent. A check removed from an
access that needed it corrupts memory, and a guard hoisted out of a loop that would never
have reached the bad index aborts a program that was correct. Both have a test here.
"""

import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from flow.bounds_proof import (  # noqa: E402
    HOIST,
    PROVEN,
    REFUTED,
    UNKNOWN,
    Affine,
    BoundsProver,
    Facts,
    Sym,
)
from flow.parser import FunctionDecl, Lexer, Parser  # noqa: E402


def verdicts(source: str):
    """Map function name -> list of verdict kinds, in source order."""
    out = {}
    for decl in Parser(Lexer(source), source).parse():
        if not isinstance(decl, FunctionDecl) or not getattr(decl, "body", None):
            continue
        prover = BoundsProver()
        prover.run(decl)
        if prover.verdicts:
            out[decl.name] = [v.kind for v in prover.verdicts.values()]
    return out


def one(source: str, name: str) -> str:
    kinds = verdicts(source)[name]
    assert len(kinds) == 1, f"expected a single access in {name}, got {kinds}"
    return kinds[0]


PRELUDE = "extern { function malloc(size: i64) -> ptr<f64> }\n"


# --- the affine domain --------------------------------------------------------------

def test_equal_symbols_cancel():
    """`len - len` must reach zero, or no obligation ever closes."""
    n = Affine.of_sym(Sym("v:n"))
    assert (n - n).is_const()
    assert (n - n).const == 0


def test_product_of_two_symbols_is_one_term():
    rows, cols = Affine.of_sym(Sym("v:rows")), Affine.of_sym(Sym("v:cols"))
    product = rows.mul(cols)
    assert product.degree() == 2
    assert len(product.terms) == 1
    # and it cancels against itself, which is what makes `len >= rows*cols` decidable
    assert (product - product).is_const()


def test_facts_decide_a_linear_implication():
    n, length = Affine.of_sym(Sym("v:n")), Affine.of_sym(Sym("v:len"))
    facts = Facts([length - n])                      # len >= n
    assert facts.implies(length - n)                 # trivially
    assert not facts.implies(n - length - Affine.of_const(1))
    assert Facts([n, -n - Affine.of_const(1)]).infeasible()   # n >= 0 and n <= -1


# --- what gets discharged -----------------------------------------------------------

def test_bound_is_the_spans_own_length_needs_nothing():
    src = PRELUDE + textwrap.dedent("""
        function f(xs: span<f64>) -> f64 {
            let mut t: f64 = 0.0
            for i in 0 to xs.len { t = t + xs[i] }
            return t
        }
    """)
    assert one(src, "f") == PROVEN


def test_separate_count_becomes_a_guard():
    src = PRELUDE + textwrap.dedent("""
        function f(xs: span<f64>, n: i32) -> f64 {
            let mut t: f64 = 0.0
            for i in 0 to n { t = t + xs[i] }
            return t
        }
    """)
    assert one(src, "f") == HOIST


def test_row_major_index_is_covered():
    """`values[row * width + column]` is the shape every numeric kernel has."""
    src = PRELUDE + textwrap.dedent("""
        struct Grid { rows: i32, cols: i32, values: span<f64> }
        function f(g: Grid) -> f64 {
            let mut t: f64 = 0.0
            for r in 0 to g.rows {
                for c in 0 to g.cols { t = t + g.values[r * g.cols + c] }
            }
            return t
        }
    """)
    assert one(src, "f") == HOIST


def test_let_bound_index_is_expanded():
    """The index names a local; its definition is what carries the loop variables."""
    src = PRELUDE + textwrap.dedent("""
        function f(xs: span<f64>, n: i32, width: i32) -> f64 {
            let mut t: f64 = 0.0
            for r in 0 to n {
                let slot: i32 = r * width
                t = t + xs[slot]
            }
            return t
        }
    """)
    assert one(src, "f") == HOIST


def test_statically_out_of_range_is_a_compile_error():
    src = PRELUDE + textwrap.dedent("""
        function f() -> f64 {
            let raw: ptr<f64> = malloc(24)
            let xs: span<f64> = raw[0..3]
            return xs[99]
        }
    """)
    assert REFUTED in verdicts(src)["f"]


def test_statically_in_range_needs_no_check():
    src = PRELUDE + textwrap.dedent("""
        function f() -> f64 {
            let raw: ptr<f64> = malloc(24)
            let xs: span<f64> = raw[0..3]
            return xs[2]
        }
    """)
    assert PROVEN in verdicts(src)["f"]


# --- what it must refuse ------------------------------------------------------------

def test_index_from_an_opaque_call_keeps_its_check():
    src = PRELUDE + textwrap.dedent("""
        extern { function pick(n: i32) -> i32 }
        function f(xs: span<f64>, n: i32) -> f64 {
            return xs[pick(n)]
        }
    """)
    assert one(src, "f") == UNKNOWN


def test_index_written_inside_the_loop_keeps_its_check():
    """`slot` is reassigned per iteration, so no guard can stand in for the check."""
    src = PRELUDE + textwrap.dedent("""
        function f(xs: span<f64>, n: i32) -> f64 {
            let mut t: f64 = 0.0
            let mut slot: i32 = 0
            for i in 0 to n {
                slot = slot + i
                t = t + xs[slot]
            }
            return t
        }
    """)
    assert one(src, "f") == UNKNOWN


def test_refutation_needs_every_reachable_direction():
    """`for t in 0 to n` runs backwards when n < 0, and then `xs[n + t]` goes negative.

    That is a guard condition, not a compile error: the ascending run is perfectly legal.
    Reporting it as an error would reject a correct program.
    """
    src = PRELUDE + textwrap.dedent("""
        function f(xs: span<f64>, n: i32) -> f64 {
            let mut t: f64 = 0.0
            for i in 0 to n { t = t + xs[n + i] }
            return t
        }
    """)
    assert one(src, "f") == HOIST


# --- end to end ---------------------------------------------------------------------

def transpile(tmp_path: Path, source: str, env_extra=None) -> str:
    path = tmp_path / "case.flow"
    path.write_text(source)
    out = tmp_path / "case.c"
    env = {"PYTHONPATH": str(SRC), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    env.update(env_extra or {})
    done = subprocess.run(
        [sys.executable, "-m", "flow.transpiler", str(path), "--c", "--lenient", "-o", str(out)],
        capture_output=True, text=True, env=env,
    )
    assert out.exists(), done.stdout + done.stderr
    return out.read_text()


KERNEL = PRELUDE + textwrap.dedent("""
    function total(xs: span<f64>, n: i32) -> f64 {
        let mut t: f64 = 0.0
        for i in 0 to n { t = t + xs[i] }
        return t
    }
    function main() -> i32 { return 0 }
""")


def body_of(c: str, name: str) -> str:
    """The definition of a generated function, skipping its forward declaration."""
    match = re.search(rf"^double {name}\w*\([^;]*?\) \{{(.*?)^\}}", c, re.S | re.M)
    assert match, f"no definition of {name} in generated C"
    return match.group(1)


def test_generated_c_has_a_checked_and_an_unchecked_copy(tmp_path):
    c = transpile(tmp_path, KERNEL)
    body = body_of(c, "total")
    # one guard, one bare access in the fast copy, one checked access in the slow copy
    assert body.count("flow_fault_handler") == 1, body
    assert ").data[i]" in body


def test_the_pass_can_be_turned_off(tmp_path):
    plain = transpile(tmp_path, KERNEL, {"FLOW_NO_BOUNDS_PROOF": "1"})
    body = body_of(plain, "total")
    assert body.count("flow_fault_handler") == 1, "the check stays on every access"
    assert "if (((" not in body, "no guard should be emitted when the pass is off"


def test_surviving_checks_reject_a_negative_index(tmp_path):
    """The check tested only `index < len`, so a negative index read behind the span."""
    c = transpile(tmp_path, KERNEL, {"FLOW_NO_BOUNDS_PROOF": "1"})
    assert "(uint64_t)(int64_t)" in c, "the surviving check must compare unsigned"
