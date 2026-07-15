"""Tests for Claim Path epistemology."""

from flow.claim_address import parse_claim_address
from flow.claim_path import (
    assume_premise,
    check_duplicate_claims,
    claim_fingerprint,
    parse_claim_path,
    tier_opening_plain,
)


class TestClaimPath:
    def test_parse_nat_addition(self):
        cp = parse_claim_path("Nat/+.zero-left")
        assert cp.domain == "Nat"
        assert "left identity" in cp.address
        addr = parse_claim_address("Nat/+.zero-left")
        assert addr.law == "zero is the left identity"

    def test_parse_bool_or(self):
        cp = parse_claim_path("Bool/||.commutes")
        assert cp.morphism == "||"

    def test_fingerprint_collapses_synonyms(self):
        a = claim_fingerprint("n + 0 == n")
        b = claim_fingerprint("n+0=n")
        assert a == b

    def test_duplicate_detection(self):
        errors = check_duplicate_claims(
            [
                ("Nat/+.zero-right", "n + 0 == n", "a.flow"),
                ("Nat/+.identity-right", "n + 0 == n", "b.flow"),
            ]
        )
        assert len(errors) == 1
        assert "Duplicate claim" in errors[0]

    def test_tier_opening_definition(self):
        cp = parse_claim_path("Nat/+.zero-left")
        text = tier_opening_plain("definition", cp)
        assert "stipulate" in text.lower()
        assert "definition" in text.lower()

    def test_assume_premise_induction(self):
        text = assume_premise(
            "Nat/+.zero-right",
            phrase="adding zero on the right",
            is_induction_hypothesis=True,
            hyp_var="k",
        )
        assert "inductive boundary" in text
        assert "k" in text