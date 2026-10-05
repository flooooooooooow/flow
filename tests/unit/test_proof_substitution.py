"""Substitution instantiation for proof math column."""

from flow.proof_substitution import instantiate_premise_latex


class TestProofSubstitution:
    def test_zero_left_instantiation(self):
        latex = instantiate_premise_latex(
            "«Nat» «addition» «zero is the left identity»",
            "0",
        )
        assert latex == "0 + 0 = 0"

    def test_induction_hypothesis_instantiation(self):
        latex = instantiate_premise_latex(
            "«Nat» «addition» «zero is the right identity»",
            "k",
            claim_expr="n + 0 == n",
            params="n: Nat",
        )
        assert latex == "k + 0 = k"