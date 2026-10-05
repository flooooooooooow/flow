"""Claim Coordinates — permanent addressing."""

from flow.claim_address import parse_claim_address, slug_phrase


class TestClaimAddress:
    def test_guillemets(self):
        a = parse_claim_address("«Nat» «addition» «zero is the left identity»")
        assert a.carrier == "Nat"
        assert a.structure == "addition"
        assert a.law == "zero is the left identity"
        assert a.display == "Nat › addition › zero is the left identity"
        assert a.slug == "Nat.addition.zero_is_the_left_identity"

    def test_legacy_path(self):
        a = parse_claim_address("Nat/+.zero-left")
        assert a.law == "zero is the left identity"

    def test_slug_phrase(self):
        assert slug_phrase("order does not matter") == "order_does_not_matter"