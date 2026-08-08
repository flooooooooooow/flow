"""Mathematical prose in proofs."""

from flow.claim_address import parse_claim_address
from flow.math_prose import (
    addr_coordinate_display,
    flow_expr_to_latex,
    flow_expr_to_mathematical_english,
    mathematical_case_condition,
    tier_opening_mathematical,
)


class TestMathProse:
    def test_no_type_abbreviations_in_opening(self):
        addr = parse_claim_address("«Nat» «addition» «zero is the left identity»")
        text = tier_opening_mathematical("definition", addr)
        assert "Nat" not in text
        assert "natural numbers" in text

    def test_bool_disjunction_english(self):
        s = flow_expr_to_mathematical_english("a or b == b or a")
        assert "disjunction" in s
        assert "Bool" not in s
        assert " or " not in s

    def test_multi_or_shield_restores_in_reverse(self):
        # Regression: with 2+ `or`s the second shield consumes the first
        # marker as an operand; restoring forward leaked the marker. The
        # reverse-order restore must rebuild the full nesting.
        s = flow_expr_to_mathematical_english("x or y or z")
        assert s == "the disjunction of the disjunction of x and y and z"
        assert "DISJ" not in s

    def test_case_condition_holds(self):
        assert mathematical_case_condition("a == true") == "a holds"

    def test_coordinate_display(self):
        addr = parse_claim_address("«Bool» «disjunction» «order does not matter»")
        d = addr_coordinate_display(addr)
        assert "Bool" not in d
        assert "boolean" in d.lower()

    def test_sin_double_prime_renders_without_broken_subscripts(self):
        latex = flow_expr_to_latex("sin_double_prime_at_zero == 0")
        assert r"\sin''(0)" in latex
        assert "sin_double_prime" not in latex

    def test_euclid_snake_case_renders_as_text_not_subscripts(self):
        latex = flow_expr_to_latex("AB_plus_AD_greater_than_BD")
        assert latex == r"\text{AB plus AD greater than BD}"

    def test_geometry_mixed_tokens_finalize_cleanly(self):
        latex = flow_expr_to_latex("triangle_ABC == half_parallelogram_ABCD")
        assert r"\triangle ABC" in latex
        assert r"half parallelogram ABCD" in latex

    def test_sin_derivative_english_is_readable(self):
        english = flow_expr_to_mathematical_english("sin_double_prime_at_zero == 0")
        assert "second derivative of sine at zero" in english
        assert "_" not in english