"""Tests for flow know lookup."""

import os

from flow.know import lookup_claim


ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


class TestKnow:
    def test_lookup_zero_right(self):
        entry = lookup_claim("«Nat» «addition» «zero is the right identity»", ROOT)
        assert entry is not None
        assert "zero is the right identity" in entry.theorem.claim_path
        assert entry.theorem.meta.tier == "derived"

    def test_lookup_qualified_path(self):
        entry = lookup_claim("Nat/+.zero-left", ROOT)
        assert entry is not None
        assert "left identity" in entry.theorem.claim_path