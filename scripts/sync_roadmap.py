#!/usr/bin/env python3
"""Sync open ROADMAP.md items to GitHub issues.

Source of truth: ROADMAP.md. Open items are any of:

  * a table row whose status column contains ``🔲`` or ``partial``
  * an unchecked checklist line (``- [ ] ...``) under Phase 2/4
  * a numbered ``🔲 **Title** ...`` line under What's Next
  * the curated KNOWN_GAPS list (prose gaps in Current State)

For every open item a stable slug is derived. The slug maps to a GitHub
issue (label ``roadmap``) and a line in ``issues-checklist.md`` of the form:

  - [ ] #NNN [roadmap:<slug>] <title> <url>

That line is deliberately the format ``scripts/sync_issues.sh`` already
parses (``#NNN`` number, ``- [x]`` checkbox), so the two tools sit next to
each other.

When an item is marked done in ROADMAP.md (status flips to ``✅``, the
checkbox is checked, or it stops matching an open rule), ``sync_roadmap.py``
closes the GitHub issue and flips the checklist line to ``- [x]``.

Usage:
  scripts/sync_roadmap.py [--roadmap ROADMAP.md] [--checklist issues-checklist.md]
                          [--repo owner/name] [--dry-run] [--verbose]

Requires: gh (authenticated). Pure Python stdlib otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROADMAP_DEFAULT = "ROADMAP.md"
CHECKLIST_DEFAULT = "issues-checklist.md"
REPO_DEFAULT = "flooooooooooow/flow"
LABEL = "roadmap"
LABEL_COLOR = "5319E7"
LABEL_DESC = "Open ROADMAP.md item synced by scripts/sync_roadmap.py"

# Known gaps from Current State -> "What's broken/missing" prose. These
# aren't structured rows/checkboxes, so they're curated here. Remove a slug
# once resolved so the item is treated as done.
KNOWN_GAPS = [
    "MLIR backend not exercised against new chained AST shapes",
    "Three older effects demos transpile but do not link (capability parameter "
    "style)",
]

_CODE = re.compile(r"`([^`]*)`")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_SLUG_NON = re.compile(r"[^a-z0-9]+")
_HEADER = re.compile(r"^#{2,4}\s+(.+)$")
_TABLE_SEP = re.compile(r"^\|[\s\-:]+\|?$")
_CHECKBOX = re.compile(r"^- \[ \]\s+(.+)$")


def clean_text(s: str) -> str:
    s = _CODE.sub(r"\1", s)
    s = _LINK.sub(r"\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.rstrip("|").strip()
    return s


def slugify(title: str) -> str:
    s = clean_text(title).lower()
    s = _SLUG_NON.sub("-", s)
    return s.strip("-") or "untitled"


def normalize_repo(repo: str) -> str:
    return repo.removeprefix("https://github.com/").removesuffix(".git")


def is_open_status(status: str) -> bool:
    return "🔲" in status or "partial" in status.lower()


def extract_open_items(roadmap: str) -> list[dict]:
    """Return open items as {slug, title, section, extra}."""
    items: dict[str, dict] = {}
    section = ""

    def add(title: str, extra: str = "", sec: str | None = None) -> None:
        slug = slugify(title)
        if slug not in items:
            items[slug] = {
                "slug": slug,
                "title": clean_text(title),
                "section": sec or section,
                "extra": clean_text(extra),
            }

    for raw in roadmap.splitlines():
        line = raw.strip()

        h = _HEADER.match(line)
        if h:
            section = h.group(1).strip()
            continue

        # --- table rows: open if ANY cell has 🔲 / partial ---
        if line.startswith("|") and not _TABLE_SEP.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if any(is_open_status(c) for c in cells):
                extra = cells[2] if len(cells) > 2 else ""
                add(cells[0], extra=extra)
            continue

        # --- unchecked checklist lines: - [ ] ... ---
        c = _CHECKBOX.match(line)
        if c:
            add(c.group(1))
            continue

        # --- numbered open lines: "2. 🔲 **Async primitives** - ..." ---
        n = re.match(r"^(\d+\.)\s+🔲\s+(.*)$", line)
        if n:
            rest = n.group(2).strip()
            b = re.match(r"^\*\*(.+?)\*\*\s*[-–]?\s*(.*)$", rest)
            if b:
                add(b.group(1), extra=b.group(2))
            else:
                parts = re.split(r"\s+[-–]\s+", rest, maxsplit=1)
                add(parts[0], extra=parts[1] if len(parts) > 1 else "")

    for text in KNOWN_GAPS:
        add(text, sec="Current State (known gaps)")

    return sorted(items.values(), key=lambda it: it["slug"])


# --------------------------------------------------------------- checklist --
def parse_checklist(text: str) -> dict[str, dict]:
    """Map slug -> {line, checked, number} from existing [roadmap:<slug>] lines."""
    result: dict[str, dict] = {}
    for raw in text.splitlines():
        m = re.match(r"^- \[([ xX])\]\s+#(\d+)\s+\[roadmap:([a-z0-9-]+)\]", raw.strip())
        if m:
            result[m.group(3)] = {
                "line": raw,
                "checked": m.group(1).lower() == "x",
                "number": int(m.group(2)),
            }
    return result


def build_checklist_line(slug: str, number: int, title: str, url: str) -> str:
    return f"- [ ] #{number} [roadmap:{slug}] {title} {url}"


# ------------------------------------------------------------------ github --
def gh(args: list[str], **kw) -> str:
    return subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=True, **kw
    ).stdout.strip()


def ensure_label(repo: str) -> None:
    try:
        gh(["label", "create", LABEL, "--repo", repo,
            "--color", LABEL_COLOR, "--description", LABEL_DESC])
    except subprocess.CalledProcessError:
        pass  # already exists


def find_existing_issues(repo: str) -> dict[str, dict]:
    """Map slug -> {number, title} for roadmap-labeled issues.

    Reads every roadmap issue in one API call and keys by the stable
    ``ROADMAP-SYNC: <slug>`` marker stored in the body.
    """
    out = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--label", LABEL,
         "--state", "all", "--limit", "500",
         "--json", "number,title,body"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        print(f"warning: gh issue list failed: {out.stderr.strip()}", file=sys.stderr)
        return {}
    mapping: dict[str, dict] = {}
    try:
        issues = json.loads(out.stdout)
    except json.JSONDecodeError:
        return mapping
    for iss in issues:
        m = re.search(r"ROADMAP-SYNC:[ ]+([a-z0-9-]+)", iss.get("body") or "")
        if m:
            mapping[m.group(1)] = {
                "number": int(iss["number"]),
                "title": iss.get("title", ""),
            }
    return mapping


# ---------------------------------------------------------------- matching --
_TOK = re.compile(r"[a-z0-9]+")


def token_set(s: str) -> set[str]:
    s = re.sub(r"^\[roadmap\]\s+", "", clean_text(s))
    return set(_TOK.findall(s.lower()))


def similarity(a: str, b: str) -> float:
    """Overlap over the smaller token set; 1.0 if one title contains the other.

    Favors rewords (a title that grows or shrinks keeps its core tokens).
    """
    ta, tb = token_set(a), token_set(b)
    if not ta or not tb:
        return 0.0
    overlap = len(ta & tb)
    return overlap / min(len(ta), len(tb))


def closest_existing(item_title: str, candidates: list[tuple[str, dict]]) -> tuple[str, dict] | None:
    """Best existing slug/issue whose title resembles item_title, or None."""
    best: tuple[float, str, dict] | None = None
    for slug, rec in candidates:
        sim = similarity(item_title, rec["title"])
        if best is None or sim > best[0]:
            best = (sim, slug, rec)
    if best is not None and best[0] >= 0.6:
        return best[1], best[2]
    return None


# -------------------------------------------------------------------- main --
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roadmap", default=ROADMAP_DEFAULT)
    ap.add_argument("--checklist", default=CHECKLIST_DEFAULT)
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would change without touching GitHub or files")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    repo = normalize_repo(args.repo)
    roadmap_path = Path(args.roadmap)
    checklist_path = Path(args.checklist)

    if not roadmap_path.is_file():
        print(f"ROADMAP file not found: {roadmap_path}", file=sys.stderr)
        return 1
    if not checklist_path.is_file():
        print(f"Checklist file not found: {checklist_path}", file=sys.stderr)
        return 1

    items = extract_open_items(roadmap_path.read_text())
    by_slug = {it["slug"]: it for it in items}

    checklist = parse_checklist(checklist_path.read_text())
    gh_issues = find_existing_issues(repo)  # slug -> {number, title}

    # Open items that need a GitHub issue: not in checklist and not on GitHub.
    to_create: list[dict] = []
    # Existing GitHub issues adopted via title-similarity (reworded item).
    to_adopt: list[tuple[str, dict]] = []  # (new slug, issue rec)
    created_lines: list[str] = []

    matched_slugs: set[str] = set()
    for it in items:
        slug = it["slug"]
        if slug in checklist or slug in gh_issues:
            matched_slugs.add(slug)
            continue
        # Try title similarity against unmatched existing issues.
        candidates = [
            (s, rec) for s, rec in gh_issues.items() if s not in matched_slugs
        ]
        hit = closest_existing(it["title"], candidates)
        if hit:
            hit_slug, hit_rec = hit
            to_adopt.append((slug, hit_rec))
            matched_slugs.add(hit_slug)
            matched_slugs.add(slug)
        else:
            to_create.append(it)

    # Roadmap items that went away / were resolved: close their issue + [x].
    to_close_numbers: set[int] = set()
    for slug, rec in checklist.items():
        if slug not in by_slug and not rec["checked"]:
            to_close_numbers.add(rec["number"])
    for slug, rec in gh_issues.items():
        if slug not in by_slug:
            to_close_numbers.add(rec["number"])
    to_close = sorted(to_close_numbers)

    if args.verbose or args.dry_run:
        print(f"Open items in ROADMAP: {len(items)}")
        print(f"Already tracked in checklist: {len(checklist)}")
        print(f"Found on GitHub with roadmap label: {len(gh_issues)}")
        print(f"To create: {len(to_create)}")
        print(f"To adopt (reworded): {len(to_adopt)}")
        print(f"To close (done): {len(to_close)}")

    if args.dry_run:
        for it in to_create:
            print(f"  would create: #{it['slug']} :: {it['title']} [{it['section']}]")
        for slug, rec in to_adopt:
            print(f"  would adopt #{rec['number']} for: {slug}")
        for num in to_close:
            print(f"  would close: #{num}")
        return 0

    ensure_label(repo)

    # Adopt reworded items: repoint the marker, rename the issue, use same number.
    adopted_lines: list[str] = []
    adopt_old_to_new: dict[str, str] = {}
    for new_slug, rec in to_adopt:
        old_slug = next(
            (s for s, r in gh_issues.items() if r["number"] == rec["number"]), None
        )
        item = by_slug[new_slug]
        gh(["issue", "edit", str(rec["number"]), "--repo", repo,
            "--title", f"[roadmap] {item['title']}"])
        body = gh(["issue", "view", str(rec["number"]), "--repo", repo,
                   "--json", "body", "--jq", ".body"])
        body = re.sub(
            r"ROADMAP-SYNC: [a-z0-9-]+", f"ROADMAP-SYNC: {new_slug}", body
        )
        gh(["issue", "edit", str(rec["number"]), "--repo", repo, "--body", body])
        url = f"https://github.com/{repo}/issues/{rec['number']}"
        adopted_lines.append(build_checklist_line(new_slug, rec["number"], item["title"], url))
        checklist[new_slug] = {"line": adopted_lines[-1], "checked": False, "number": rec["number"]}
        if old_slug and old_slug != new_slug:
            checklist.pop(old_slug, None)
            adopt_old_to_new[old_slug] = new_slug
        if args.verbose:
            print(f"adopted #{rec['number']} as '{item['title']}' (was slug '{old_slug}')")

    for it in to_create:
        body = (
            f"Automatically mirrored from [ROADMAP.md]({args.roadmap}).\n\n"
            f"**Section:** {it['section']}\n\n"
            f"**Task:** {it['title']}\n"
            + (f"\n{it['extra']}\n" if it["extra"] else "")
            + f"\nROADMAP-SYNC: {it['slug']}"
        )
        out = gh(["issue", "create", "--repo", repo, "--label", LABEL,
                  "--title", f"[roadmap] {it['title']}", "--body", body])
        m = re.search(r"issues/(\d+)", out)
        number = int(m.group(1)) if m else 0
        if args.verbose:
            print(f"created #{number}: {it['title']}")
        created_lines.append(build_checklist_line(it["slug"], number, it["title"], out))
        checklist[it["slug"]] = {"line": created_lines[-1], "checked": False, "number": number}

    for num in to_close:
        if args.verbose:
            print(f"closing #{num}")
        gh(["issue", "close", str(num), "--repo", repo])

    # Rewrite checklist: keep all lines, flip done roadmap entries to - [x],
    # and replace adopted (reworded) slugs in place so the old slug stays linked
    # to the same issue number rather than being treated as resolved.
    output: list[str] = []
    emitted_adopted = set()
    for line in checklist_path.read_text().splitlines():
        m = re.match(r"^- \[([ xX])\]\s+(#\d+\s+\[roadmap:[a-z0-9-]+\].*)$", line.strip())
        if m:
            slug = re.search(r"\[roadmap:([a-z0-9-]+)\]", m.group(2)).group(1)
            if slug in adopt_old_to_new:
                new_slug = adopt_old_to_new[slug]
                rec = checklist[new_slug]
                output.append(rec["line"])
                emitted_adopted.add(new_slug)
                continue
            checked = "x" if slug not in by_slug else " "
            output.append(f"- [{checked}] {m.group(2)}")
        else:
            output.append(line)
    output.extend(created_lines)
    # Adopted items appear in place above (emitted_adopted); append any that
    # had no old-slug line to replace yet (e.g. adopted from a bare GitHub issue
    # that was never in the file).
    for s, rec in checklist.items():
        if s in adopt_old_to_new.values() and s not in emitted_adopted:
            output.append(rec["line"])

    with checklist_path.open("w") as fh:
        fh.write("\n".join(output) + "\n")


if __name__ == "__main__":
    sys.exit(main())
