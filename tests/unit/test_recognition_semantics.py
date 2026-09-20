"""Tests for recognition-relative denotational semantics."""

import pytest

from flow.parser import FlowDecl, FlowSyntaxError, Lexer, Parser, StructDecl
from flow.recognition import (
    RecognitionError,
    assert_recognition_preserved,
    compare_recognition,
    declared_domains,
    recognition_manifest,
    recognition_signature,
)


BASE = """
flow Controller {
    state x : f64 = 0.0
    input u : f64
    output y : f64 = x
    param k : f64 = 2.0

    solver { dt 1 ms method euler }
    x evolves as k * u

    always {
        x < 100.0
    }

    recognize {
        numerical
        realtime
        causal
        safety
        memory
    }
}
"""


def parse_raw(code: str):
    return Parser(Lexer(code), source=code).parse(expand_flows=False)


def parse_lowered(code: str):
    return Parser(Lexer(code), source=code).parse()


def flow_of(code: str) -> FlowDecl:
    return next(d for d in parse_raw(code) if isinstance(d, FlowDecl))


class TestRecognitionSyntax:
    def test_recognize_block_is_ast_metadata(self):
        flow = flow_of(BASE)
        assert flow.recognition is not None
        assert flow.recognition.domains == [
            "numerical",
            "realtime",
            "causal",
            "safety",
            "memory",
        ]

    def test_commas_are_optional(self):
        code = BASE.replace(
            """numerical
        realtime
        causal
        safety
        memory""",
            "numerical, realtime, causal, safety, memory",
        )
        flow = flow_of(code)
        assert declared_domains(flow) == (
            "numerical",
            "realtime",
            "causal",
            "safety",
            "memory",
        )

    def test_recognize_stays_contextual(self):
        code = """
function recognize(x: i32) -> i32 {
    return x + 1
}

function main() -> i32 {
    let recognize: i32 = 2
    return recognize
}
"""
        decls = parse_lowered(code)
        assert not any(isinstance(d, FlowDecl) for d in decls)

    def test_duplicate_domain_rejected(self):
        code = BASE.replace(
            """numerical
        realtime
        causal
        safety
        memory""",
            "numerical numerical",
        )
        with pytest.raises(FlowSyntaxError, match="appears twice"):
            parse_raw(code)

    def test_unknown_domain_rejected_during_semantic_validation(self):
        code = BASE.replace("memory", "metaphysical")
        with pytest.raises(FlowSyntaxError, match="unknown recognition domain"):
            parse_lowered(code)


class TestDenotation:
    def test_lowering_retains_recognition_manifest(self):
        decls = parse_lowered(BASE)
        struct = next(d for d in decls if isinstance(d, StructDecl))
        assert isinstance(struct.flow_decl, FlowDecl)
        assert tuple(struct.recognition_manifest) == (
            "numerical",
            "realtime",
            "causal",
            "safety",
            "memory",
        )
        assert struct.recognition_manifest == recognition_manifest(struct.flow_decl)

    def test_signatures_are_deterministic(self):
        flow = flow_of(BASE)
        assert recognition_signature(flow, "numerical") == recognition_signature(
            flow, "numerical"
        )

    def test_one_change_can_be_visible_to_one_recognizer_only(self):
        before = flow_of(BASE)
        after = flow_of(BASE.replace("x evolves as k * u", "x evolves as k * u + 1.0"))

        numerical = compare_recognition(before, after, ["numerical"])
        memory = compare_recognition(before, after, ["memory"])

        assert [drift.domain for drift in numerical] == ["numerical"]
        assert memory == ()

    def test_contract_rejects_semantic_drift(self):
        before = flow_of(BASE)
        after = flow_of(BASE.replace("x evolves as k * u", "x evolves as -k * u"))

        with pytest.raises(RecognitionError, match="numerical"):
            assert_recognition_preserved(before, after, ["numerical"])

    def test_contract_accepts_preserved_projection(self):
        before = flow_of(BASE)
        after = flow_of(BASE.replace("x evolves as k * u", "x evolves as k * u + 1.0"))

        assert_recognition_preserved(before, after, ["memory"])
