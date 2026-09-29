"""
Repository statistics formatting and path classification.

The counter is the Flow program in scripts/tools/repo_stats/main.flow. These
tests build it with scripts/tools/build_tool.sh and run it in a scratch tree
with a hand-written file list, so no git is involved. The formatting rules
are pinned here because a truncating Flow counter once published 72.5k
against a README that said 72.6k.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
START = "<!-- repo-stats:start -->"
END = "<!-- repo-stats:end -->"
NO_LINES = "n/a"


@pytest.fixture(scope="module")
def counter():
    if shutil.which("cc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler")
    out = subprocess.run(
        [str(ROOT / "scripts" / "tools" / "build_tool.sh"), "repo_stats"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return ROOT / out


def run_counter(counter, tmp_path, files, mode="write", readme=None):
    """Lay out `files` ({path: line count}) and run the counter over them."""
    for rel, lines in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x\n" * lines)
    meta = tmp_path / "build" / "repo-stats"
    meta.mkdir(parents=True, exist_ok=True)
    # scripts/update_repo_stats.sh creates this before running the counter.
    (tmp_path / "docs" / "generated").mkdir(parents=True, exist_ok=True)
    (meta / "files.txt").write_text("".join(f"{rel}\n" for rel in files))
    (meta / "meta.txt").write_text("commit=abcdef123456\ngenerated_at=2026-01-01T00:00:00+00:00\n")
    (meta / "mode.txt").write_text(mode + "\n")
    if readme is None:
        readme = f"# Title\n\n{START}\nold\n{END}\n\ntail\n"
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    result = subprocess.run([str(counter)], cwd=tmp_path, capture_output=True, text=True)
    data = None
    out_json = tmp_path / "docs" / "generated" / "repository-stats.json"
    if out_json.exists():
        data = json.loads(out_json.read_text(encoding="utf-8"))
    return result, data, (tmp_path / "README.md").read_text(encoding="utf-8")


class TestCompact:
    """Badge text: plain below 1k, one rounded decimal below 100k, then k."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (999, "999"),
            (1_000, "1.0k"),
            (72_586, "72.6k"),
            (99_960, "100.0k"),
            (100_000, "100k"),
            (171_889, "172k"),
            (1_234_000, "1,234k"),
        ],
    )
    def test_compact(self, counter, tmp_path, value, expected):
        result, data, _ = run_counter(counter, tmp_path, {"lib/stdlib/a.flow": value})
        assert result.returncode == 0, result.stderr
        assert data["badges"]["flow"] == f"{expected} Flow LOC"
        assert data["badges"]["loc"] == f"{expected} LOC"


class TestUnder:
    """Areas match whole path components, never bare string prefixes."""

    def test_directory_prefix_and_partial_component(self, counter, tmp_path):
        files = {
            "src/flow/parser.py": 5,
            "src/flowers/parser.py": 7,
            "runtime": 3,
            "docs/index.md": 2,
        }
        result, data, _ = run_counter(counter, tmp_path, files)
        assert result.returncode == 0, result.stderr
        assert data["areas"]["python_compiler"] == {"files": 1, "lines": 5}
        assert data["areas"]["runtime"]["files"] == 0
        assert data["languages"]["Python"] == {"files": 2, "lines": 12}


class TestMarkdown:
    """The rendered block is delimited and uses grouped numbers."""

    FILES = {
        "lib/stdlib/big.flow": 2_000,
        "src/flow/a.py": 1_500,
        "registry/packages/x/flow.toml": 4,
    }

    def block(self, counter, tmp_path):
        result, _, readme = run_counter(counter, tmp_path, self.FILES)
        assert result.returncode == 0, result.stderr
        return readme[readme.index(START) : readme.index(END) + len(END)]

    def test_numbers_are_grouped(self, counter, tmp_path):
        assert "| **Tracked source** | 2 | 3,500 |" in self.block(counter, tmp_path)

    def test_registry_packages_reports_no_line_count(self, counter, tmp_path):
        assert f"| **Registry packages** | 1 | {NO_LINES} |" in self.block(counter, tmp_path)

    def test_languages_ordered_by_lines_descending(self, counter, tmp_path):
        block = self.block(counter, tmp_path)
        assert block.index("| Flow |") < block.index("| Python |")

    def test_footnote_credits_the_flow_counter(self, counter, tmp_path):
        assert "scripts/tools/repo_stats/main.flow" in self.block(counter, tmp_path)


class TestReadmeContract:
    """The markers have to survive edits, or every refresh fails."""

    def test_readme_has_both_markers(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        assert text.count(START) == 1
        assert text.count(END) == 1

    def test_update_replaces_only_the_block(self, counter, tmp_path):
        result, _, readme = run_counter(counter, tmp_path, {"a.flow": 1})
        assert result.returncode == 0, result.stderr
        assert readme.startswith(f"# Title\n\n{START}\n")
        assert readme.endswith(f"{END}\n\ntail\n")
        assert "\nold\n" not in readme

    def test_missing_markers_fail(self, counter, tmp_path):
        result, _, _ = run_counter(counter, tmp_path, {"a.flow": 1}, readme="no markers\n")
        assert result.returncode == 1
        assert "missing repository-stat markers" in result.stderr

    def test_check_mode_reports_stale_files(self, counter, tmp_path):
        result, _, _ = run_counter(counter, tmp_path, {"a.flow": 1}, mode="check")
        assert result.returncode == 1
        assert result.stdout == (
            "Repository statistics are stale: docs/generated/repository-stats.json, README.md\n"
        )
