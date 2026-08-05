"""Repository statistics for the README and docs/generated/repository-stats.json.

Counts tracked source files only: `git ls-files`, minus vendored and
generated trees. Physical lines include comments and blanks, so the
numbers describe the size of the repository rather than any notion of
"useful" code.

This is the reference implementation. The counter of record is the Flow
program in scripts/tools/repo_stats/main.flow; scripts/update_repo_stats.sh
runs that first and cross-checks it against this script, falling back here
when Flow cannot be built or run.

Usage:
    python3 scripts/update_repo_stats.py
    python3 scripts/update_repo_stats.py --check
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
OUTPUT = ROOT / "docs" / "generated" / "repository-stats.json"
START = "<!-- repo-stats:start -->"
END = "<!-- repo-stats:end -->"
STATS_COMMIT_SUBJECT = "docs: refresh repository statistics [skip ci]"

SOURCE_SUFFIXES = {
    ".flow": "Flow",
    ".py": "Python",
    ".c": "C",
    ".h": "C/C++ headers",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".cc": "C++",
    ".cpp": "C++",
    ".rs": "Rust",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".sh": "Shell",
    ".html": "HTML",
    ".css": "CSS",
}

EXCLUDED_PREFIXES = (".git/", "build/", "dist/", "third_party/", "node_modules/")
EXCLUDED_PARTS = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}


def under(rel: Path, *prefixes: str) -> bool:
    posix = rel.as_posix()
    return any(posix.startswith(prefix + "/") for prefix in prefixes)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths: list[Path] = []
    for raw in result.stdout.split(b"\n"):
        if not raw:
            continue
        rel = Path(raw.decode("utf-8", "surrogateescape"))
        posix = rel.as_posix()
        if posix.startswith(EXCLUDED_PREFIXES):
            continue
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        path = ROOT / rel
        if not path.is_file():
            continue
        paths.append(rel)
    return sorted(paths)


def line_count(rel: Path) -> int:
    with open(ROOT / rel, "rb") as handle:
        return sum(1 for _ in handle)


def compact(value: int) -> str:
    if value < 1_000:
        return f"{value:,}"
    if value < 100_000:
        return f"{value / 1_000:.1f}k"
    return f"{round(value / 1_000):,}k"


def git_value(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def source_revision() -> str:
    """Return the latest non-generated commit to avoid daily stats churn.

    Bounded so a shallow clone, where the parent of the grafted root is
    unreachable, degrades to the current commit instead of raising.
    """
    revision = "HEAD"
    for _ in range(5):
        try:
            subject = git_value("show", "-s", "--format=%s", revision)
        except subprocess.CalledProcessError:
            break
        if subject != STATS_COMMIT_SUBJECT:
            break
        parent = f"{revision}^"
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", parent],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if probe.returncode != 0:
            break
        revision = parent
    return revision


def collect() -> dict[str, object]:
    files = tracked_files()
    language_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"files": 0, "lines": 0}
    )
    source_files: list[Path] = []
    lines_by_file: dict[Path, int] = {}

    for rel in files:
        language = SOURCE_SUFFIXES.get(rel.suffix.lower())
        if language is None:
            continue
        lines = line_count(rel)
        lines_by_file[rel] = lines
        language_counts[language]["files"] += 1
        language_counts[language]["lines"] += lines
        source_files.append(rel)

    def area(
        name: str,
        predicate: object,
        suffixes: set[str] | None = None,
    ) -> tuple[str, dict[str, int]]:
        selected = [
            rel
            for rel in files
            if callable(predicate)
            and predicate(rel)
            and (suffixes is None or rel.suffix.lower() in suffixes)
        ]
        return name, {
            "files": len(selected),
            "lines": sum(lines_by_file.get(rel) or line_count(rel) for rel in selected),
        }

    areas = dict(
        [
            area(
                "python_compiler",
                lambda rel: under(rel, "src/flow"),
                {".py"},
            ),
            area(
                "self_hosted_compiler",
                lambda rel: under(rel, "compiler/src"),
                {".flow"},
            ),
            area(
                "standard_library",
                lambda rel: under(rel, "lib/stdlib"),
                {".flow"},
            ),
            area(
                "runtime",
                lambda rel: under(rel, "runtime"),
                {".c", ".h", ".m", ".mm", ".cc", ".cpp"},
            ),
            area(
                "examples",
                lambda rel: under(rel, "examples")
                and not under(rel, "examples/verify"),
                {".flow"},
            ),
            area(
                "verify_corpus",
                lambda rel: under(rel, "examples/verify", "lib/verify"),
                {".flow"},
            ),
            area(
                "tests",
                lambda rel: under(rel, "tests"),
                {".py", ".flow"},
            ),
            area(
                "applications",
                lambda rel: under(rel, "apps"),
                {".flow"},
            ),
            area(
                "registry_packages",
                lambda rel: under(rel, "registry/packages")
                and rel.name == "flow.toml",
            ),
            area(
                "documentation",
                lambda rel: under(rel, "docs"),
                {".md"},
            ),
        ]
    )

    proof_docs = [
        rel
        for rel in files
        if rel.name.endswith(".proof.md")
        and under(rel, "examples/verify", "lib/verify", "docs")
    ]

    total_lines = sum(lines_by_file.values())
    revision = source_revision()
    flow = language_counts.get("Flow", {"files": 0, "lines": 0})
    stdlib = areas["standard_library"]
    examples = areas["examples"]
    tests = areas["tests"]

    return {
        "schema_version": 1,
        "generated_at": git_value("show", "-s", "--format=%cI", revision),
        "commit": git_value("rev-parse", "--short=12", revision),
        "methodology": (
            "Tracked source files only; physical lines include comments and blanks; "
            "third_party and generated/build directories are excluded."
        ),
        "totals": {
            "source_files": len(source_files),
            "source_lines": total_lines,
            "tracked_files": len(files),
        },
        "languages": dict(sorted(language_counts.items())),
        "areas": areas,
        "proof_documents": len(proof_docs),
        "badges": {
            "loc": f"{compact(total_lines)} LOC",
            "flow": f"{compact(flow['lines'])} Flow LOC",
            "stdlib": f"{stdlib['files']} modules",
            "examples": f"{examples['files']} examples",
            "tests": f"{tests['files']} tests",
            "proofs": f"{areas['verify_corpus']['files']} verify files",
        },
    }


def markdown(stats: dict[str, object]) -> str:
    totals = stats["totals"]
    areas = stats["areas"]
    languages = stats["languages"]
    flow = languages.get("Flow", {"files": 0, "lines": 0})
    compiler = areas["python_compiler"]
    self_hosted = areas["self_hosted_compiler"]
    stdlib = areas["standard_library"]
    runtime = areas["runtime"]
    examples = areas["examples"]
    verify = areas["verify_corpus"]
    tests = areas["tests"]
    apps = areas["applications"]
    docs = areas["documentation"]
    packages = areas["registry_packages"]

    rows = [
        ("Tracked source", totals["source_files"], totals["source_lines"]),
        ("Flow language", flow["files"], flow["lines"]),
        ("Python compiler (`src/flow`)", compiler["files"], compiler["lines"]),
        ("Self-hosted compiler (`compiler/src`)", self_hosted["files"], self_hosted["lines"]),
        ("Standard library modules", stdlib["files"], stdlib["lines"]),
        ("Native runtime", runtime["files"], runtime["lines"]),
        ("Examples (excluding verify corpus)", examples["files"], examples["lines"]),
        ("Verify corpus", verify["files"], verify["lines"]),
        ("Tests (`.py` + `.flow`)", tests["files"], tests["lines"]),
        ("Application programs", apps["files"], apps["lines"]),
        ("Registry packages", packages["files"], "—"),
        ("Documentation pages", docs["files"], docs["lines"]),
    ]

    table = [
        START,
        "| Metric | Files / modules | Physical lines |",
        "|---|---:|---:|",
    ]
    for label, file_count, lines in rows:
        rendered_lines = f"{lines:,}" if isinstance(lines, int) else lines
        table.append(f"| **{label}** | {file_count:,} | {rendered_lines} |")

    table.extend(
        [
            "",
            "<details>",
            "<summary>Tracked source by language</summary>",
            "",
            "| Language | Files | Physical lines |",
            "|---|---:|---:|",
        ]
    )
    for language, counts in sorted(
        languages.items(),
        key=lambda item: (-item[1]["lines"], item[0]),
    ):
        table.append(
            f"| {language} | {counts['files']:,} | {counts['lines']:,} |"
        )
    table.extend(
        [
            "",
            "</details>",
            "",
            (
                f"*Generated by CI from tracked files at `{stats['commit']}`. "
                f"Proof documents: {stats['proof_documents']:,}. "
                "[Raw JSON](docs/generated/repository-stats.json) · "
                "[Flow counter](scripts/tools/repo_stats/main.flow) · "
                "[Python fallback](scripts/update_repo_stats.py).*"
            ),
            END,
        ]
    )
    return "\n".join(table)


def update_readme(block: str) -> str:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise RuntimeError(f"{README} is missing repository-stat markers")
    before, remainder = text.split(START, 1)
    _, after = remainder.split(END, 1)
    return f"{before}{block}{after}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if README/JSON differ from generated output",
    )
    args = parser.parse_args()

    stats = collect()
    json_text = json.dumps(stats, indent=2, sort_keys=True) + "\n"
    readme_text = update_readme(markdown(stats))

    if args.check:
        stale: list[str] = []
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != json_text:
            stale.append(str(OUTPUT.relative_to(ROOT)))
        if README.read_text(encoding="utf-8") != readme_text:
            stale.append(str(README.relative_to(ROOT)))
        if stale:
            print("Repository statistics are stale: " + ", ".join(stale))
            return 1
        print("Repository statistics are current")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json_text, encoding="utf-8")
    README.write_text(readme_text, encoding="utf-8")
    print(
        f"Updated {README.relative_to(ROOT)} and {OUTPUT.relative_to(ROOT)} "
        f"({stats['totals']['source_lines']:,} source lines)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
