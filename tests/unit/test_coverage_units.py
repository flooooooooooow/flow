"""Coverage tests for units of measure (flow-test-coverage).

Extends tests/unit/test_units.py with cases it does not touch: unit
values flowing through function calls and struct fields, long
composition chains, cancellation to dimensionless through a function
boundary, mixed unit/scalar comparisons, and the located text of the
errors those rejections produce.
"""

from flow.c_generator import flow_to_c
from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


PRELUDE = """
unit Meter
unit Second
unit Velocity = Meter / Second
unit Accel = Meter / Second^2
"""


def check(code: str):
    return TypeChecker().check(parse_flow_code(code)).errors


class TestUnitsThroughFunctions:
    def test_unit_parameters_and_return(self):
        code = PRELUDE + """
        function speed(d: Meter, t: Second) -> Velocity {
            return d / t
        }
        function main() -> i32 {
            let v: Velocity = speed(100.0 as Meter, 8.0 as Second)
            return 0
        }
        """
        assert check(code) == []

    def test_composition_chain_through_two_divisions(self):
        # Meter / Second / Second composes to the Accel exponent vector.
        code = PRELUDE + """
        function accel_of(d: Meter, t: Second) -> Accel {
            return d / t / t
        }
        function main() -> i32 {
            let a: Accel = accel_of(1.0 as Meter, 2.0 as Second)
            return 0
        }
        """
        assert check(code) == []

    def test_cancellation_to_dimensionless_through_return(self):
        code = PRELUDE + """
        function ratio(a: Meter, b: Meter) -> f64 {
            return a / b
        }
        function main() -> i32 {
            let r: f64 = ratio(4.0 as Meter, 2.0 as Meter)
            let scaled: f64 = r * 3.0
            return 0
        }
        """
        assert check(code) == []

    def test_return_dimension_mismatch_names_both_units(self):
        code = PRELUDE + """
        function bad(d: Meter, t: Second) -> Accel {
            return d / t
        }
        """
        errors = check(code)
        assert len(errors) == 1
        # Meter/Second has a declared canonical unit here, so the message
        # names it rather than printing the exponent vector.
        assert "returns Velocity" in errors[0]
        assert "should return Accel" in errors[0]

    def test_wrong_unit_argument_is_rejected(self):
        code = PRELUDE + """
        function takes_m(d: Meter) -> Meter { return d }
        function main() -> i32 {
            let t: Second = 1.0 as Second
            let d: Meter = takes_m(t)
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "takes_m" in errors[0]
        assert "Second" in errors[0]


class TestUnitsThroughStructFields:
    JOURNEY = PRELUDE + """
    struct Journey {
        distance: Meter,
        elapsed: Second,
    }
    """

    def test_fields_keep_their_units(self):
        code = self.JOURNEY + """
        function main() -> i32 {
            let j: Journey = Journey {
                distance: 100.0 as Meter,
                elapsed: 8.0 as Second
            }
            let v: Velocity = j.distance / j.elapsed
            return 0
        }
        """
        assert check(code) == []

    def test_field_of_wrong_dimension_rejected_in_arithmetic(self):
        code = self.JOURNEY + """
        function main() -> i32 {
            let j: Journey = Journey {
                distance: 100.0 as Meter,
                elapsed: 8.0 as Second
            }
            let x = j.distance + j.elapsed
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "dimensional error: Meter + Second" in errors[0]

    def test_field_units_erase_to_typedefs_in_c(self):
        code = self.JOURNEY + """
        function main() -> i32 {
            let j: Journey = Journey {
                distance: 100.0 as Meter,
                elapsed: 8.0 as Second
            }
            return 0
        }
        """
        c = flow_to_c(parse_flow_code(code))
        assert "typedef double Meter;" in c
        struct_body = c.split("struct Journey {", 1)[1].split("};", 1)[0]
        assert "Meter distance;" in struct_body
        assert "Second elapsed;" in struct_body


class TestMixedComparisons:
    def test_unit_vs_scalar_comparison_rejected_with_location(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let b: bool = d > 1.0
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "line 9:" in errors[0]
        assert "dimensional error" in errors[0]
        assert "comparison requires both operands to have the same dimension" in errors[0]

    def test_unit_vs_other_unit_comparison_rejected_with_location(self):
        code = PRELUDE + """
        function main() -> i32 {
            let d: Meter = 1.0 as Meter
            let t: Second = 2.0 as Second
            let b: bool = d > t
            return 0
        }
        """
        errors = check(code)
        assert len(errors) == 1
        assert "line 10:" in errors[0]
        assert "dimensional error: Meter > Second" in errors[0]

    def test_same_unit_comparison_through_function_results(self):
        code = PRELUDE + """
        function speed(d: Meter, t: Second) -> Velocity {
            return d / t
        }
        function main() -> i32 {
            let fast: Velocity = speed(100.0 as Meter, 5.0 as Second)
            let slow: Velocity = speed(100.0 as Meter, 50.0 as Second)
            let quicker: bool = fast > slow
            return 0
        }
        """
        assert check(code) == []
