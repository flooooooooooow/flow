"""The shared documentation block extractor and the example checker."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from check_doc_examples import _compile, _harness, verify  # noqa: E402
from docs_blocks import (  # noqa: E402
    Block,
    InfoStringError,
    iter_blocks,
    parse_info,
    tutorial_lessons,
)


def blocks(text: str) -> list[Block]:
    return list(iter_blocks(text, "test.md"))


# --------------------------------------------------------------------------
# Fence scanning
# --------------------------------------------------------------------------

def test_consecutive_blocks_do_not_bleed_into_each_other():
    # The regex both old extractors used could start at a closing fence and
    # run to the next opening one, capturing the prose between as code.
    text = "```flow\nfirst\n```\n\nprose in between\n\n```flow\nsecond\n```\n"
    found = blocks(text)
    assert [b.code for b in found] == ["first", "second"]


def test_prose_between_blocks_is_never_a_block():
    text = "```bash\nls\n```\n\nnot code at all\n\n```bash\npwd\n```\n"
    assert [b.code for b in blocks(text)] == ["ls", "pwd"]


def test_longer_fence_can_contain_a_shorter_one():
    text = "````markdown\n```flow\ninner\n```\n````\n"
    found = blocks(text)
    assert len(found) == 1
    assert found[0].lang == "markdown"
    assert "```flow" in found[0].code


def test_line_numbers_point_at_the_opening_fence():
    text = "intro\n\n```flow\ncode\n```\n"
    assert blocks(text)[0].line == 3


def test_headings_are_attached_to_following_blocks():
    text = "## Section\n\n### Title\n\n```flow\ncode\n```\n"
    found = blocks(text)[0]
    assert found.section == "Section"
    assert found.title == "Title"


def test_untagged_block_has_empty_lang():
    assert blocks("```\nplain\n```\n")[0].lang == ""


# --------------------------------------------------------------------------
# Info strings
# --------------------------------------------------------------------------

def test_bare_language_tag():
    assert parse_info("flow") == ("flow", frozenset(), {})


def test_flags_and_options():
    lang, flags, opts = parse_info('flow expect-error ignore="why"')
    assert lang == "flow"
    assert flags == frozenset({"expect-error"})
    assert opts == {"ignore": "why"}


def test_quoted_ignore_reason_survives_spaces():
    _, _, opts = parse_info('flow ignore="needs a GPU device"')
    assert opts["ignore"] == "needs a GPU device"


def test_legacy_run_and_interactive_still_parse():
    # The tutorial runner has always accepted these.
    assert parse_info("flow run")[1] == frozenset({"run"})
    assert parse_info("flow interactive")[1] == frozenset({"interactive"})


@pytest.mark.parametrize(
    "info",
    [
        "flow expect_error",
        "flow nonsense",
        "flow mode=fast",
        "flow ignore=",
        # Designed but not implemented: must not parse while it does nothing.
        "flow host=python",
        "flow from=examples/book/01_hello.flow",
    ],
)
def test_unknown_info_words_are_rejected(info):
    # A typo must fail loudly; silently treating it as an ordinary block
    # would verify code the author meant to exempt.
    with pytest.raises(InfoStringError):
        parse_info(info)


# --------------------------------------------------------------------------
# Harness and the no-op guard
# --------------------------------------------------------------------------

COMPLETE = """
function main() -> i32 {
    return 0
}
"""


def test_complete_program_verifies_standalone():
    result = verify(Block(path="p.md", line=1, info="flow", lang="flow", code=COMPLETE))
    assert result.status == "verified"
    assert result.mode == "standalone"


def test_declaration_fragment_needs_no_entry_point():
    # A Flow translation unit needs no entry point to parse, type-check or
    # generate C, so a bare declaration verifies as written. This is why the
    # decl-wrap rung was removed: it never rescued anything.
    code = "struct Point {\n    x: i32,\n    y: i32\n}"
    result = verify(Block(path="p.md", line=1, info="flow", lang="flow", code=code))
    assert result.status == "verified"
    assert result.mode == "standalone"


def test_statement_fragment_is_wrapped_in_a_body():
    code = "let mut total: i32 = 0\ntotal = total + 1"
    result = verify(Block(path="p.md", line=1, info="flow", lang="flow", code=code))
    assert result.status == "verified"
    assert result.mode == "stmt-wrap"


@pytest.mark.parametrize(
    "code",
    [
        "angle evolves as velocity",  # parses as a variable, then a cast
        "state angle\nstate velocity",  # parses as four bare variables
        "continuous\nevery 1 ms",
        "length + voltage",
    ],
)
def test_prose_shaped_fragments_are_not_counted_as_verified(code):
    # These all parse once wrapped in a main, and all mean nothing like what
    # the surrounding prose says. Counting them would make the check worthless.
    result = verify(Block(path="p.md", line=1, info="flow", lang="flow", code=code))
    assert result.status == "unverified"
    assert "no-op" in result.detail


def test_the_no_op_guard_leaves_real_statements_alone():
    csource, stage, detail = _compile(
        _harness("println(1)", "stmt-wrap"), guard_noop=True, mode="stmt-wrap"
    )
    assert csource is not None, f"{stage}: {detail}"


def test_a_no_op_hidden_inside_an_if_is_still_caught():
    # The guard has to recurse; a bare identifier nested in a block is just as
    # meaningless as one at the top level.
    result = verify(
        Block(path="p.md", line=1, info="flow", lang="flow",
              code="if true {\n    continuous\n    every 1 ms\n}")
    )
    assert result.status == "unverified"


def test_a_block_that_compiles_to_nothing_is_not_verified():
    # `theorem` declarations and unused generics are erased before codegen, so
    # the C is empty and clang is trivially happy.
    result = verify(
        Block(path="p.md", line=1, info="flow", lang="flow",
              code="# just a comment, nothing else")
    )
    assert result.status == "unverified"
    assert result.stage == "vacuous"


def test_undefined_names_are_caught_by_the_strict_checker():
    # In lenient mode the checker does not resolve names and this reaches clang.
    result = verify(
        Block(path="p.md", line=1, info="flow", lang="flow",
              code="function f() -> i32 {\n    return undefined_thing\n}")
    )
    assert result.status == "unverified"


def test_dynamics_dsl_blocks_go_through_the_source_expanders():
    # `dsys` is expanded by module_resolver before parsing. Without the
    # expander the checker calls working documentation broken.
    code = "dsys plant {\n    discrete\n    dt 0.1\n    n 2 m 1 p 1\n}"
    csource, stage, detail = _compile(code, guard_noop=False)
    assert stage != "parse", f"expander not applied: {detail}"


def test_ignore_needs_no_compilation_and_keeps_its_reason():
    result = verify(
        Block(
            path="p.md",
            line=1,
            info="flow",
            lang="flow",
            code="total gibberish {{{",
            opts={"ignore": "vision sketch"},
        )
    )
    assert result.status == "ignored"
    assert result.row()["reason"] == "vision sketch"


def test_expect_error_passes_only_when_the_block_really_fails():
    bad = Block(
        path="p.md", line=1, info="flow expect-error", lang="flow",
        code="let x: i32 = {{{", flags=frozenset({"expect-error"}),
    )
    assert verify(bad).status == "expected-error"


def test_expect_error_on_valid_code_is_a_failure():
    # Otherwise the tag becomes a way to silence a block that actually works,
    # and the docs drift without anyone noticing.
    good = Block(
        path="p.md", line=1, info="flow expect-error", lang="flow",
        code=COMPLETE, flags=frozenset({"expect-error"}),
    )
    result = verify(good)
    assert result.status == "unverified"
    assert "compiles" in result.detail


# --------------------------------------------------------------------------
# Parity with what the wiki build produces today
# --------------------------------------------------------------------------

def test_tutorial_extraction_matches_the_shipped_lesson_rule():
    lessons = tutorial_lessons()
    assert len(lessons) > 200
    assert all(lesson.has_main for lesson in lessons)
    assert all(lesson.path.startswith("docs/tutorials/") for lesson in lessons)
    assert not any(lesson.path.endswith("README.md") for lesson in lessons)


# --------------------------------------------------------------------------
# The ratchet
# --------------------------------------------------------------------------

def _ledger(tmp_path, rows):
    import json

    path = tmp_path / "ledger.json"
    path.write_text(json.dumps({"generated": "2026-01-01", "totals": {}, "blocks": rows}))
    return path


def test_a_new_failing_example_is_a_regression(tmp_path, monkeypatch):
    import check_doc_examples as chk

    monkeypatch.setattr(chk, "LEDGER", _ledger(tmp_path, []))
    bad = Block(path="p.md", line=1, info="flow", lang="flow", code="function f( -> i32 {")
    assert chk.check_ledger([chk.verify(bad)]) == 1


def test_an_example_already_in_the_ledger_is_grandfathered(tmp_path, monkeypatch):
    import check_doc_examples as chk

    bad = Block(path="p.md", line=1, info="flow", lang="flow", code="function f( -> i32 {")
    monkeypatch.setattr(
        chk, "LEDGER",
        _ledger(tmp_path, [{"key": bad.key, "path": "p.md", "line": 1,
                            "status": "unverified"}]),
    )
    assert chk.check_ledger([chk.verify(bad)]) == 0


def test_editing_a_grandfathered_example_revokes_it(tmp_path, monkeypatch):
    """The property the whole ratchet rests on.

    Rows are keyed by a hash of the block, so any edit produces a key the
    ledger has never seen and the new text has to compile on its own.
    """
    import check_doc_examples as chk

    old = Block(path="p.md", line=1, info="flow", lang="flow", code="function f( -> i32 {")
    monkeypatch.setattr(
        chk, "LEDGER",
        _ledger(tmp_path, [{"key": old.key, "path": "p.md", "line": 1,
                            "status": "unverified"}]),
    )
    edited = Block(path="p.md", line=1, info="flow", lang="flow",
                   code="function f( -> i32 {  # touched")
    assert chk.check_ledger([chk.verify(edited)]) == 1


def test_paying_off_debt_is_reported_not_punished(tmp_path, monkeypatch, capsys):
    # An unrelated pull request must not fail because someone else fixed a doc
    # example; that teaches people to regenerate the ledger without reading it.
    import check_doc_examples as chk

    good = Block(path="p.md", line=1, info="flow", lang="flow", code=COMPLETE)
    monkeypatch.setattr(
        chk, "LEDGER",
        _ledger(tmp_path, [{"key": good.key, "path": "p.md", "line": 1,
                            "status": "unverified"}]),
    )
    assert chk.check_ledger([chk.verify(good)]) == 0
    assert "now compile" in capsys.readouterr().out


def test_a_missing_ledger_is_a_failure(tmp_path, monkeypatch):
    import check_doc_examples as chk

    monkeypatch.setattr(chk, "LEDGER", tmp_path / "absent.json")
    assert chk.check_ledger([]) == 1


# --------------------------------------------------------------------------
# preamble=
# --------------------------------------------------------------------------

def test_a_preamble_supplies_declarations_the_chapter_already_showed(tmp_path, monkeypatch):
    import check_doc_examples as chk

    (tmp_path / "ctx.flow").write_text("struct Sample {\n    value: f64\n}\n")
    monkeypatch.setattr(chk, "ROOT", tmp_path)
    block = Block(
        path="p.md", line=1, info="flow", lang="flow",
        code="function first_value(s: Sample) -> f64 {\n    return s.value\n}",
        opts={"preamble": "ctx.flow"},
    )
    assert chk.verify(block).status == "verified"


def test_the_preamble_sits_outside_the_harness(tmp_path, monkeypatch):
    """A struct must not end up nested inside a synthesized main."""
    import check_doc_examples as chk

    (tmp_path / "ctx.flow").write_text("struct Sample {\n    value: f64\n}\n")
    monkeypatch.setattr(chk, "ROOT", tmp_path)
    block = Block(
        path="p.md", line=1, info="flow", lang="flow",
        code="let s: Sample = Sample { value: 1.0 }",  # statements, needs stmt-wrap
        opts={"preamble": "ctx.flow"},
    )
    result = chk.verify(block)
    assert result.status == "verified", result.detail
    assert result.mode == "stmt-wrap"


def test_a_missing_preamble_is_a_failure(tmp_path, monkeypatch):
    import check_doc_examples as chk

    monkeypatch.setattr(chk, "ROOT", tmp_path)
    block = Block(
        path="p.md", line=1, info="flow", lang="flow", code=COMPLETE,
        opts={"preamble": "nope.flow"},
    )
    result = chk.verify(block)
    assert result.status == "unverified"
    assert result.stage == "preamble"
