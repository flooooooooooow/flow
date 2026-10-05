"""Tests for the welcome bot's pure logic (no discord dependency)."""

import json
import random
from pathlib import Path

import pytest

from welcome import load_messages, pick_welcome

HERE = Path(__file__).resolve().parent
MESSAGES_FILE = HERE / "messages.json"


def test_load_messages_returns_templates() -> None:
    templates = load_messages(MESSAGES_FILE)
    assert len(templates) >= 1
    for t in templates:
        assert "{user}" in t


def test_load_messages_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_messages(tmp_path / "nope.json")


def test_load_messages_empty_list(tmp_path: Path) -> None:
    p = tmp_path / "empty.json"
    p.write_text(json.dumps({"messages": []}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_messages(p)


def test_load_messages_bad_json(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_messages(p)


def test_pick_welcome_substitutes_user_and_guild() -> None:
    templates = ["Hello {user}, welcome to the {guild} discord server!"]
    rng = random.Random(0)
    out = pick_welcome("@alice", "Flow", templates, rng=rng)
    assert out == "Hello @alice, welcome to the Flow discord server!"


def test_pick_welcome_is_deterministic_with_seed() -> None:
    templates = [
        "Hello {user}, welcome to the {guild} discord server!",
        "Welcome {user} to the {guild} discord server.",
        "{user} just joined the {guild} discord server.",
    ]
    a = pick_welcome("@bob", "Flow", templates, rng=random.Random(42))
    b = pick_welcome("@bob", "Flow", templates, rng=random.Random(42))
    assert a == b
    assert "@bob" in a
    assert "Flow" in a


def test_every_template_formats_cleanly() -> None:
    """Every shipped template must format without KeyError or missing fields."""
    templates = load_messages(MESSAGES_FILE)
    for t in templates:
        out = t.format(user="@tester", guild="Flow")
        assert "@tester" in out
        assert "Flow" in out
