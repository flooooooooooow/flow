"""
Repository statistics formatting and path classification.

scripts/update_repo_stats.py is the reference implementation that the Flow
counter in scripts/tools/repo_stats/main.flow has to match byte for byte,
so the formatting rules are pinned here. The two once disagreed because
Flow truncated where Python rounds, which is invisible until a badge
reads 72.5k against the README's 72.6k.

Nothing here shells out to git; only the pure helpers are exercised.
"""

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "update_repo_stats.py"


def load_module():
    spec = importlib.util.spec_from_file_location("repo_stats_reference", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


stats = load_module()


class TestCompact:
    """Badge text: plain below 1k, one rounded decimal below 100k, then k."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (0, "0"),
            (999, "999"),
            (1_000, "1.0k"),
            (72_586, "72.6k"),
            (99_960, "100.0k"),
            (99_999, "100.0k"),
            (100_000, "100k"),
            (171_889, "172k"),
        ],
    )
    def test_compact(self, value, expected):
        assert stats.compact(value) == expected

    def test_rounds_rather_than_truncates(self):
        # The divergence that motivated this file: truncation gives 72.5k.
        assert stats.compact(72_586) == "72.6k"

    def test_thousands_separator_above_a_million(self):
        assert stats.compact(1_234_000) == "1,234k"


class TestUnder:
    """`under` matches whole path components, never bare string prefixes."""

    def test_matches_directory_prefix(self):
        assert stats.under(Path("src/flow/parser.py"), "src/flow")

    def test_matches_one_of_several_prefixes(self):
        assert stats.under(Path("lib/verify/proof.flow"), "examples/verify", "lib/verify")

    def test_rejects_partial_component(self):
        # "src/flowers" must not count as living under "src/flow".
        assert not stats.under(Path("src/flowers/parser.py"), "src/flow")

    def test_rejects_unrelated_path(self):
        assert not stats.under(Path("docs/index.md"), "src/flow")

    def test_rejects_the_prefix_itself_as_a_file(self):
        assert not stats.under(Path("runtime"), "runtime")


class TestMarkdown:
    """The rendered block is delimited and uses grouped numbers."""

    @staticmethod
    def sample():
        area = {"files": 3, "lines": 4_000}
        return {
            "commit": "abcdef123456",
            "proof_documents": 1_080,
            "totals": {"source_files": 1_868, "source_lines": 171_889},
            "languages": {
                "Flow": {"files": 1_526, "lines": 77_338},
                "Python": {"files": 176, "lines": 62_793},
            },
            "areas": {
                key: dict(area)
                for key in (
                    "python_compiler",
                    "self_hosted_compiler",
                    "standard_library",
                    "runtime",
                    "examples",
                    "verify_corpus",
                    "tests",
                    "applications",
                    "registry_packages",
                    "documentation",
                )
            },
        }

    def test_block_is_delimited_by_markers(self):
        block = stats.markdown(self.sample())
        assert block.startswith(stats.START)
        assert block.endswith(stats.END)

    def test_numbers_are_grouped(self):
        block = stats.markdown(self.sample())
        assert "| **Tracked source** | 1,868 | 171,889 |" in block

    def test_registry_packages_reports_no_line_count(self):
        # Manifests are counted as files; a line total would be meaningless.
        assert "| **Registry packages** | 3 | — |" in stats.markdown(self.sample())

    def test_languages_ordered_by_lines_descending(self):
        block = stats.markdown(self.sample())
        assert block.index("| Flow |") < block.index("| Python |")

    def test_footnote_credits_both_implementations(self):
        block = stats.markdown(self.sample())
        assert "scripts/tools/repo_stats/main.flow" in block
        assert "scripts/update_repo_stats.py" in block


class TestReadmeContract:
    """The markers have to survive edits, or every refresh fails."""

    def test_readme_has_both_markers(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        assert text.count(stats.START) == 1
        assert text.count(stats.END) == 1

    def test_update_readme_replaces_only_the_block(self):
        original = (ROOT / "README.md").read_text(encoding="utf-8")
        rewritten = stats.update_readme(f"{stats.START}\nreplaced\n{stats.END}")
        head = original.split(stats.START, 1)[0]
        assert rewritten.startswith(head)
        assert "replaced" in rewritten
