#!/usr/bin/env python3
"""Fenced code blocks in the documentation, extracted once for everybody.

`build_wiki.build_tutorial_exercises` and `verify_browser_interp.extract_snippets`
each carried their own copy of the same regex and the same `"function main" in
code` filter. The copies had already drifted: only one of them derived a section
heading. Both now call in here.

The regex they used, ```` ```(?:flow…)\\n(.*?)``` ````, mispairs fences. With
`re.DOTALL` and a non-greedy body it can start at the *closing* fence of one
block and run to the opening fence of the next, capturing the prose between them
as if it were code. This module walks lines instead and applies the CommonMark
rule: a fence opened with N backticks closes on the next line of N or more of
the same character.

Per-block metadata lives in the info string, which is the only place markdown
offers and which nothing currently uses::

    ```flow                                  verify as written
    ```flow expect-error                     must FAIL to compile
    ```flow ignore="needs a GPU device"      excluded, reason required
    ```flow host=python                      verify under FLOW_HOST=python
    ```flow flow-body                        wrap in `flow Demo { ... }`
    ```flow preamble=docs/_preambles/gfx.flow
    ```flow from=examples/book/01_hello.flow  assert the inline copy matches

Both older extractors already tolerated a suffix after `flow` (they accepted
`run` and `interactive`), so every form above is backward compatible.
"""

from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Optional

ROOT = Path(__file__).resolve().parent.parent

# Vendored or generated trees: not ours to verify.
EXCLUDED_PREFIXES = (
    "third_party/",
    "docs/formal/",
    "build/",
    "site/vendor/",
)

# Info-string words that are flags rather than key=value pairs.
KNOWN_FLAGS = frozenset(
    {
        "run",  # legacy, honoured by the tutorial runner
        "interactive",  # legacy
        "expect-error",
        "flow-body",
        "no-harness",
    }
)

KNOWN_KEYS = frozenset({"ignore", "host", "preamble", "from"})


@dataclass
class Block:
    """One fenced block, with its position and parsed info string."""

    path: str  # repo-relative POSIX path
    line: int  # 1-based line of the opening fence
    info: str  # raw info string, e.g. 'flow expect-error'
    lang: str  # first word of the info string, lowercased ('' when bare)
    code: str
    flags: frozenset = field(default_factory=frozenset)
    opts: dict = field(default_factory=dict)
    section: Optional[str] = None  # nearest preceding `## `
    title: Optional[str] = None  # nearest preceding `### `

    @property
    def ident(self) -> str:
        return f"{self.path}:{self.line}"

    @property
    def has_main(self) -> bool:
        return "function main" in self.code

    @property
    def ignored(self) -> Optional[str]:
        return self.opts.get("ignore")

    @property
    def expects_error(self) -> bool:
        return "expect-error" in self.flags


class InfoStringError(ValueError):
    """An info string that names something this repo does not define."""


def parse_info(info: str) -> tuple[str, frozenset, dict]:
    """Split an info string into (lang, flags, options).

    Raises InfoStringError on an unknown word, so a typo like `expect_error`
    fails loudly instead of silently verifying the block as ordinary code.
    """
    try:
        words = shlex.split(info)
    except ValueError as exc:  # unbalanced quote
        raise InfoStringError(f"cannot parse info string {info!r}: {exc}") from exc
    if not words:
        return "", frozenset(), {}

    lang = words[0].lower()
    flags: set[str] = set()
    opts: dict[str, str] = {}
    for word in words[1:]:
        if "=" in word:
            key, _, value = word.partition("=")
            key = key.lower()
            if key not in KNOWN_KEYS:
                raise InfoStringError(f"unknown option {key!r} in {info!r}")
            if not value:
                raise InfoStringError(f"option {key!r} needs a value in {info!r}")
            opts[key] = value
            continue
        if word.lower() not in KNOWN_FLAGS:
            raise InfoStringError(f"unknown flag {word!r} in {info!r}")
        flags.add(word.lower())

    if "ignore" in opts and not opts["ignore"].strip():
        raise InfoStringError(f"ignore= needs a written reason in {info!r}")
    return lang, frozenset(flags), opts


_FENCE = re.compile(r"^(?P<indent>\s{0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


def iter_blocks(text: str, path: str) -> Iterator[Block]:
    """Yield every fenced block in `text`, in document order."""
    lines = text.splitlines()
    section: Optional[str] = None
    title: Optional[str] = None
    i = 0
    while i < len(lines):
        line = lines[i]
        match = _FENCE.match(line)
        if not match:
            if line.startswith("## "):
                section, title = line[3:].strip(), None
            elif line.startswith("### "):
                title = line[4:].strip()
            i += 1
            continue

        char = match.group("fence")[0]
        width = len(match.group("fence"))
        info = match.group("info").strip()
        # An info string may not contain a backtick when the fence is backticks.
        if char == "`" and "`" in info:
            i += 1
            continue

        body: list[str] = []
        start = i + 1  # 1-based line of the opening fence
        i += 1
        while i < len(lines):
            closer = _FENCE.match(lines[i])
            if (
                closer
                and closer.group("fence")[0] == char
                and len(closer.group("fence")) >= width
                and not closer.group("info").strip()
            ):
                break
            body.append(lines[i])
            i += 1
        i += 1  # step past the closing fence

        lang, flags, opts = parse_info(info)
        yield Block(
            path=path,
            line=start,
            info=info,
            lang=lang,
            code="\n".join(body).strip("\n"),
            flags=flags,
            opts=opts,
            section=section,
            title=title,
        )


def tracked_markdown(root: Path = ROOT) -> list[str]:
    """Repo-relative markdown paths, from the git index, minus vendored trees.

    Reading the index rather than the filesystem keeps generated output under
    `build/` from ever counting as documentation, which is the same reason
    check_doc_links.py resolves against `git ls-files`.
    """
    out = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "*.md"], text=True
    )
    return [
        line
        for line in out.splitlines()
        if line and not line.startswith(EXCLUDED_PREFIXES)
    ]


def collect(
    paths: Optional[Iterable[str]] = None,
    root: Path = ROOT,
    lang: Optional[str] = None,
) -> list[Block]:
    """Every block across `paths` (default: all tracked markdown).

    `lang` filters to one language tag. Blocks with an empty body are dropped:
    they carry no code to verify.
    """
    if paths is None:
        paths = tracked_markdown(root)
    blocks: list[Block] = []
    for rel in paths:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        for block in iter_blocks(text, rel):
            if not block.code.strip():
                continue
            if lang is not None and block.lang != lang:
                continue
            blocks.append(block)
    return blocks


def tutorial_lessons(root: Path = ROOT) -> list[Block]:
    """The tutorial blocks the interactive app turns into lessons.

    This is the rule build_wiki and verify_browser_interp each implemented
    separately: `docs/tutorials/*.md` except README, flow blocks only, and only
    those carrying a `main`.
    """
    rels = sorted(
        p.relative_to(root).as_posix()
        for p in (root / "docs" / "tutorials").glob("*.md")
        if p.name != "README.md"
    )
    return [b for b in collect(rels, root, lang="flow") if b.has_main]


if __name__ == "__main__":  # quick census
    from collections import Counter

    all_blocks = collect()
    tags = Counter(b.lang or "(none)" for b in all_blocks)
    print(f"{len(all_blocks)} blocks across {len(tracked_markdown())} files")
    for tag, count in tags.most_common(12):
        print(f"  {tag:12s} {count:5d}")
