"""The shared documentation block extractor and the example checker."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from check_doc_examples import _harness, _try_compile, verify  # noqa: E402
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
    lang, flags, opts = parse_info('flow expect-error host=python')
    assert lang == "flow"
    assert flags == frozenset({"expect-error"})
    assert opts == {"host": "python"}


def test_quoted_ignore_reason_survives_spaces():
    _, _, opts = parse_info('flow ignore="needs a GPU device"')
    assert opts["ignore"] == "needs a GPU device"


def test_legacy_run_and_interactive_still_parse():
    # The tutorial runner has always accepted these.
    assert parse_info("flow run")[1] == frozenset({"run"})
    assert parse_info("flow interactive")[1] == frozenset({"interactive"})


@pytest.mark.parametrize(
    "info",
    ["flow expect_error", "flow nonsense", "flow mode=fast", "flow ignore="],
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
    # A translation unit does not need a `main` to parse and type-check, so a
    # bare declaration verifies as written. The decl-wrap rung only earns its
    # keep in the deep tier, where linking does need one.
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
    ok, err = _try_compile(_harness("println(1)", "stmt-wrap"), guard_noop=True)
    assert ok, err


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
