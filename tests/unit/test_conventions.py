"""Tests for project-level conventions (#415)."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.conventions import (
    AvoidPattern,
    BuildSettings,
    Conventions,
    check_file,
    find_flow_toml,
    load_conventions,
)


def test_find_flow_toml():
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "flow.toml").write_text("[package]\nname = \"test\"\n")
        sub = tmpdir / "src" / "deep"
        sub.mkdir(parents=True)
        result = find_flow_toml(sub)
        assert result is not None
        assert result.name == "flow.toml"


def test_find_flow_toml_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        result = find_flow_toml(Path(tmp))
        assert result is None


def test_load_conventions_empty():
    with tempfile.TemporaryDirectory() as tmp:
        conv = load_conventions(Path(tmp))
        assert len(conv.avoid) == 0
        assert conv.build.host == ""


def test_load_conventions_with_avoid():
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "flow.toml").write_text("""
[build]
host = "python"
test_command = "flow run tests/test.flow"

[conventions]
avoid = [
  { pattern = "reverse for loop", reason = "wrong step (#410)", workaround = "use while" },
  { pattern = "string + string", reason = "not supported (#412)", workaround = "use print()" },
]
""")
        conv = load_conventions(tmpdir)
        assert conv.build.host == "python"
        assert conv.build.test_command == "flow run tests/test.flow"
        assert len(conv.avoid) == 2
        assert conv.avoid[0].pattern == "reverse for loop"
        assert conv.avoid[0].reason == "wrong step (#410)"
        assert conv.avoid[1].workaround == "use print()"


def test_check_file_no_patterns():
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "flow.toml").write_text("[package]\nname = \"test\"\n")
        src = tmpdir / "main.flow"
        src.write_text("function main() -> i32 { return 0 }")
        warnings = check_file(src)
        assert warnings == []


def test_check_file_with_match():
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "flow.toml").write_text("""
[conventions]
avoid = [
  { pattern = "for i in 10 to 0", reason = "wrong step", workaround = "use while" },
]
""")
        src = tmpdir / "main.flow"
        src.write_text("function f() -> void { for i in 10 to 0 { print(i) } }")
        warnings = check_file(src)
        assert len(warnings) == 1
        assert "for i in 10 to 0" in warnings[0]
        assert "wrong step" in warnings[0]
        assert "use while" in warnings[0]


def test_check_file_no_match():
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "flow.toml").write_text("""
[conventions]
avoid = [
  { pattern = "for i in 10 to 0", reason = "wrong step", workaround = "use while" },
]
""")
        src = tmpdir / "main.flow"
        src.write_text("function f() -> void { for i in 0 to 10 { print(i) } }")
        warnings = check_file(src)
        assert warnings == []


def test_load_patterns():
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "flow.toml").write_text("""
[patterns]
math = "use fabs as f64 then cast"
exports = "use export struct for public API"
""")
        conv = load_conventions(tmpdir)
        assert conv.patterns["math"] == "use fabs as f64 then cast"
        assert conv.patterns["exports"] == "use export struct for public API"
