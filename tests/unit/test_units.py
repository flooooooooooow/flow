"""Tests for units of measure (docs/vision/north-star.md section 6).

Card: flow-vision-units. Covers: unit declaration parsing, accepted and
rejected arithmetic (every rejection asserts a located, helpful message),
exponent composition through * and /, dimensionless interop, and erasure
to plain f64 in the generated C.
"""

import pytest

from flow.c_generator import flow_to_c
from flow.parser import FlowSyntaxError, Lexer, Parser, UnitDecl
from flow.type_checker import TypeChecker


def parse(code):
    return Parser(Lexer(code), source=code).parse()


def check(code):
    return TypeChecker().check(parse(code)).errors


def units_of(decls):
    return {d.name: d for d in decls if isinstance(d, UnitDecl)}


PRELUDE = """
unit Meter
unit Second
unit Kilogram
unit Radian
unit Velocity = Meter / Second
unit Accel = Meter / Second^2
"""


class TestUnitDeclParsing:
    def test_base_unit_has_no_factors(self):
        units = units_of(parse("unit Meter"))
        assert units["Meter"].factors is None

    def test_derived_unit_flattens_to_factors(self):
        units = units_of(parse("unit Meter\nunit Second\nunit Velocity = Meter / Second"))
        assert units["Velocity"].factors == [("Meter", 1), ("Second", -1)]

    def test_exponent(self):
        units = units_of(parse("unit Meter\nunit Second\nunit Accel = Meter / Second^2"))
        assert units["Accel"].factors == [("Meter", 1), ("Second", -2)]

    def test_negative_exponent(self):
        units = units_of(parse("unit Second\nunit Hertz = Second^-1"))
        assert units["Hertz"].factors == [("Second", -1)]

    def test_one_over_unit(self):
        units = units_of(parse("unit Second\nunit Hertz = 1 / Second"))
        assert units["Hertz"].factors == [("Second", -1)]

    def test_dimensionless_unit(self):
        units = units_of(parse("unit Ratio = 1"))
        assert units["Ratio"].factors == []

    def test_product_of_three(self):
        code = "unit Meter\nunit Second\nunit Kilogram\nunit Newton = Kilogram * Meter / Second^2"
        units = units_of(parse(code))
        assert units["Newton"].factors == [("Kilogram", 1), ("Meter", 1), ("Second", -2)]

    def test_decl_records_line(self):
        units = units_of(parse("\nunit Meter"))
        assert units["Meter"].line == 2

    def test_unit_erases_to_f64(self):
        units = units_of(parse("unit Meter"))
        assert units["Meter"].base_type.name == "f64"

    def test_unit_stays_a_legal_identifier(self):
        code = """
        function main() -> i32 {
            let unit = 5
            return unit - 5
        }
        """
        assert check(code) == []

    def test_non_integer_exponent_is_a_syntax_error(self):
        with pytest.raises(FlowSyntaxError):
            parse("unit Meter\nunit Bad = Meter^1.5")

    def test_number_other_than_one_is_a_syntax_error(self):
        with pytest.raises(FlowSyntaxError):
            parse("unit Bad = 2")


class TestAcceptedArithmetic:
    def test_same_dimension_add_sub(self):
        code = PRELUDE + """
        function main() -> i32 {
            let a: Meter = 1.0 as Meter
            let b: Meter = 2.0 as Meter
            let c: Meter = a + b
            let d: Meter = a - b
            return 0
        }
        """
        assert check(code) == []

    def test_divide_composes_to_declared_unit(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 100.0 as Meter
            let t: Second = 8.0 as Second
            let v: Velocity = d / t
            return 0
        }
        """
        assert check(code) == []

    def test_multiply_cancels_back(self):
        code = PRELUDE + """
        function main() -> i32 {
            let v: Velocity = 5.0 as Velocity
            let t: Second = 2.0 as Second
            let d: Meter = v * t
            return 0
        }
        """
        assert check(code) == []

    def test_same_dimension_comparison(self):
        code = PRELUDE + """
        function main() -> i32 {
            let a: Meter = 1.0 as Meter
            let b: Meter = 2.0 as Meter
            let closer: bool = a < b
            let same: bool = a == b
            return 0
        }
        """
        assert check(code) == []

    def test_unary_minus_keeps_dimension(self):
        code = PRELUDE + """
        function main() -> i32 {
            let v: Velocity = 5.0 as Velocity
            let reverse: Velocity = -v
            return 0
        }
        """
        assert check(code) == []

    def test_cast_between_same_dimension_units(self):
        code = PRELUDE + """
        unit Metre = Meter
        function main() -> i32 {
            let a: Meter = 1.0 as Meter
            let b: Metre = a as Metre
            return 0
        }
        """
        assert check(code) == []

    def test_radian_passes_into_sin(self):
        code = PRELUDE + """
        extern {
            function sin(x: f64) -> f64
        }
        function main() -> i32 {
            let angle: Radian = 1.57 as Radian
            let s: f64 = sin(angle)
            return 0
        }
        """
        assert check(code) == []


class TestRejectedArithmetic:
    """Every rejection must carry a source line and a usable explanation."""

    def test_mixed_dimension_add(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let t: Second = 2.0 as Second
            let x = d + t
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "line 12:" in errors[0]
        assert "dimensional error: Meter + Second" in errors[0]
        assert "same dimension" in errors[0]

    def test_mixed_dimension_sub(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let v: Velocity = 2.0 as Velocity
            let x = d - v
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "line 12:" in errors[0]
        assert "dimensional error: Meter - Velocity" in errors[0]

    def test_unit_plus_dimensionless_scalar(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let x = d + 1.0
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "line 11:" in errors[0]
        assert "dimensional error" in errors[0]
        # The message points at the fix: give the literal a unit with `as`.
        assert "as Meter" in errors[0]

    def test_mixed_dimension_comparison(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let t: Second = 2.0 as Second
            let x: bool = d < t
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "line 12:" in errors[0]
        assert "dimensional error: Meter < Second" in errors[0]
        assert "comparison" in errors[0]

    def test_mixed_dimension_equality(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let v: Velocity = 2.0 as Velocity
            let x: bool = d == v
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "line 12:" in errors[0]
        assert "dimensional error: Meter == Velocity" in errors[0]

    def test_mixed_dimension_modulo(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let t: Second = 2.0 as Second
            let x = d % t
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "line 12:" in errors[0]
        assert "dimensional error: Meter % Second" in errors[0]

    def test_wrong_dimension_annotation_names_canonical_unit(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let t: Second = 2.0 as Second
            let v: Second = d / t
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        # Meter/Second has a declared canonical unit, so the message uses it.
        assert "Velocity" in errors[0]
        assert "Second" in errors[0]

    def test_wrong_dimension_annotation_prints_anonymous_dims(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let t: Second = 2.0 as Second
            let x: Meter = d / t / t / t
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        # No declared unit has these dimensions; the message prints the
        # exponent vector in unit names.
        assert "Meter/Second^3" in errors[0]

    def test_cross_dimension_cast_rejected(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let t: Second = d as Second
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "Cannot cast Meter to Second" in errors[0]

    def test_sin_of_length_rejected(self):
        code = PRELUDE + """
        extern {
            function sin(x: f64) -> f64
        }
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let s: f64 = sin(d)
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "dimensional error" in errors[0]
        assert "sin()" in errors[0]
        assert "Radian" in errors[0]

    def test_unknown_unit_in_declaration(self):
        errors = check("unit Velocity = Meter / Second")
        assert len(errors) == 2  # both Meter and Second are undeclared
        assert all("unknown unit" in e for e in errors)
        assert all("line 1:" in e for e in errors)
        assert "declared before use" in errors[0]

    def test_duplicate_unit_declaration(self):
        errors = check("unit Meter\nunit Meter")
        assert len(errors) == 1
        assert "line 2:" in errors[0]
        assert "already declared" in errors[0]

    def test_shift_on_units_rejected(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let x = d << 1
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "dimensional error" in errors[0]
        assert "'<<'" in errors[0]


class TestExponentComposition:
    def test_accel_times_second_is_velocity(self):
        code = PRELUDE + """
        function main() -> i32 {
            let g: Accel = 9.81 as Accel
            let t: Second = 2.0 as Second
            let v: Velocity = g * t
            return 0
        }
        """
        assert check(code) == []

    def test_velocity_per_second_is_accel(self):
        code = PRELUDE + """
        function main() -> i32 {
            let v: Velocity = 10.0 as Velocity
            let t: Second = 2.0 as Second
            let a: Accel = v / t
            return 0
        }
        """
        assert check(code) == []

    def test_kinetic_energy_dimensions(self):
        code = PRELUDE + """
        unit Joule = Kilogram * Meter^2 / Second^2
        function main() -> i32 {
            let m: Kilogram = 2.0 as Kilogram
            let v: Velocity = 3.0 as Velocity
            let e: Joule = m * v * v
            return 0
        }
        """
        assert check(code) == []

    def test_grouping_is_associative(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let t: Second = 2.0 as Second
            let a1: Accel = d / t / t
            let a2: Accel = d / (t * t)
            return 0
        }
        """
        assert check(code) == []

    def test_anonymous_result_assigns_across_spellings(self):
        # Two derived units with the same exponent vector are interchangeable.
        code = PRELUDE + """
        unit Speed = Meter / Second
        function main() -> i32 {
            let v: Velocity = 5.0 as Velocity
            let s: Speed = v
            return 0
        }
        """
        assert check(code) == []


class TestDimensionlessInterop:
    def test_scalar_multiplication_both_sides(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 2.0 as Meter
            let a: Meter = d * 3.0
            let b: Meter = 0.5 * d
            let c: Meter = d / 2.0
            return 0
        }
        """
        assert check(code) == []

    def test_integer_scalar_multiplication(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 2.0 as Meter
            let a: Meter = d * 3
            return 0
        }
        """
        assert check(code) == []

    def test_full_cancellation_is_plain_f64(self):
        code = PRELUDE + """
        function main() -> i32 {
            let a: Meter = 2.0 as Meter
            let b: Meter = 4.0 as Meter
            let ratio: f64 = b / a
            let scaled: f64 = ratio * 2.0
            return 0
        }
        """
        assert check(code) == []

    def test_scalar_over_unit_matches_declared_inverse(self):
        code = PRELUDE + """
        unit Hertz = 1 / Second
        function main() -> i32 {
            let t: Second = 0.5 as Second
            let f: Hertz = 1.0 / t
            return 0
        }
        """
        assert check(code) == []

    def test_unit_casts_back_to_f64(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 2.0 as Meter
            let raw: f64 = d as f64
            return 0
        }
        """
        assert check(code) == []


class TestErasure:
    CODE = PRELUDE + """
    function main() -> i32 {
        let d: Meter = 100.0 as Meter
        let t: Second = 8.0 as Second
        let v: Velocity = d / t
        let d2: Meter = v * t
        return 0
    }
    """

    def test_units_erase_to_f64_typedefs(self):
        c = flow_to_c(parse(self.CODE))
        assert "typedef double Meter;" in c
        assert "typedef double Second;" in c
        assert "typedef double Velocity;" in c

    def test_no_unit_machinery_in_generated_c(self):
        c = flow_to_c(parse(self.CODE))
        # No dimension vectors, checks, or unit structs survive to C.
        assert "dims" not in c
        assert "dimension" not in c
        assert "unit" not in c.lower().replace("units erased", "")
        for unit_name in ("Meter", "Second", "Velocity"):
            assert f"struct {unit_name}" not in c

    def test_arithmetic_is_plain_c(self):
        c = flow_to_c(parse(self.CODE))
        assert "(d / t)" in c
        assert "(v * t)" in c
