"""Physical-systems W0: RF quantity suffixes, affine dBm+dB, attributes."""

from flow.attributes import attribute_errors, attrs_imply_rt_safe
from flow.parser import CastExpression, Lexer, Parser, QUANTITY_SUFFIX_UNITS, VarDecl
from flow.type_checker import TypeChecker


def parse(code):
    return Parser(Lexer(code), source=code).parse()


def check(code):
    return TypeChecker().check(parse(code)).errors


RF_PRELUDE = """
unit Second
unit Hertz = 1 / Second
unit Decibel = 1
unit dBm
unit dBW
unit Radian
unit Degree = Radian
unit Meter
"""


class TestQuantitySuffixes:
    def test_suffix_table_covers_rf(self):
        for suffix in ("Hz", "kHz", "MHz", "GHz", "dB", "dBm", "dBW", "deg", "rad"):
            assert suffix in QUANTITY_SUFFIX_UNITS

    def test_ghz_desugars_to_scaled_hertz_cast(self):
        decls = parse(RF_PRELUDE + """
        function main() -> i32 {
            let fc = 2.45GHz
            return 0
        }
        """)
        fn = decls[-1]
        stmt = fn.body.statements[0]
        assert isinstance(stmt, VarDecl)
        assert isinstance(stmt.initializer, CastExpression)
        assert stmt.initializer.target_type.name == "Hertz"
        # 2.45 * 1e9
        assert stmt.initializer.expr.value.startswith("2450000000")

    def test_spaced_suffix(self):
        errors = check(RF_PRELUDE + """
        function main() -> i32 {
            let fs: Hertz = 40 MHz
            let _x: f64 = fs as f64
            return 0
        }
        """)
        assert errors == []

    def test_frequency_plus_time_fails(self):
        errors = check(RF_PRELUDE + """
        function main() -> i32 {
            let fc: Hertz = 2.4GHz
            let delay: Second = 14.0 as Second
            let bad = fc + delay
            return 0
        }
        """)
        assert any("dimensional error" in e for e in errors)

    def test_dbm_plus_db(self):
        errors = check(RF_PRELUDE + """
        function main() -> i32 {
            let p: dBm = 20dBm + 3dB
            let _x: f64 = p as f64
            return 0
        }
        """)
        assert errors == []

    def test_dbm_plus_dbm_fails(self):
        errors = check(RF_PRELUDE + """
        function main() -> i32 {
            let bad = 20dBm + 3dBm
            return 0
        }
        """)
        assert any("dimensional error" in e or "dBm" in e for e in errors)


class TestPhysicalAttributes:
    def test_guarantee_implies_rt_safe(self):
        assert attrs_imply_rt_safe(["guarantee(no_alloc, no_block)"])
        assert attrs_imply_rt_safe(["deterministic"])
        assert not attrs_imply_rt_safe(["inline"])

    def test_aligned_requires_int(self):
        errs = attribute_errors("buf", ["aligned(64)"])
        assert errs == []
        errs = attribute_errors("buf", ["aligned(nope)"])
        assert errs

    def test_guarantee_unknown_arg(self):
        errs = attribute_errors("f", ["guarantee(no_heap)"])
        assert errs

    def test_guarantee_rejects_malloc(self):
        errors = check("""
        @guarantee(no_alloc, no_block)
        function process() -> i32 {
            let p = malloc(8)
            return 0
        }
        """)
        assert any(
            "rt_safe" in e.lower() or "malloc" in e.lower() or "heap" in e.lower()
            for e in errors
        )


class TestQuantitySuffixLineBoundary:
    def test_suffix_does_not_glue_across_newline(self):
        """`1\\nrad = ...` must not parse as a Radian quantity literal."""
        from flow.parser import Assignment, BinaryOperation, CastExpression

        decls = parse("""
        function main() -> i32 {
            let mut preset: i32 = 0
            let mut rad: f32 = 0.0
            preset = (preset % 4) + 1
            rad = 0.5
            return preset
        }
        """)
        stmt = decls[-1].body.statements[2]
        assert isinstance(stmt, Assignment)
        assert stmt.target == "preset"
        assert not isinstance(stmt.value, CastExpression)
        assert isinstance(stmt.value, BinaryOperation)


class TestRateMismatchExample:
    def test_rate_mismatch_example_typechecks_fail(self):
        """examples/rf/rate_mismatch.flow is intentionally ill-typed."""
        import subprocess
        import sys
        from pathlib import Path

        root = Path(__file__).resolve().parents[2]
        path = root / "examples" / "rf" / "rate_mismatch.flow"
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "flow.transpiler",
                str(path),
                "--c",
                "--strict",
                "-o",
                str(root / "build" / "_rate_mismatch_test.c"),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(root / "src")},
        )
        combined = (proc.stdout or "") + (proc.stderr or "")
        assert proc.returncode != 0
        assert "add_cf32_20m" in combined or "type error" in combined.lower()
