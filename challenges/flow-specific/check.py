#!/usr/bin/env python3
"""Check that a Flow challenge submission uses the required language forms."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


CHALLENGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CHALLENGE_DIR.parent.parent
CATALOG_PATH = CHALLENGE_DIR / "catalog.json"


def load_catalog() -> dict[str, dict]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return {item["id"].upper(): item for item in data["challenges"]}


def strip_flow_comments(source: str) -> str:
    """Remove # comments without treating # inside a string as a comment."""
    output: list[str] = []
    in_string = False
    escaped = False
    in_comment = False

    for char in source:
        if char == "\n":
            output.append(char)
            escaped = False
            in_comment = False
            continue
        if in_comment:
            continue
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            output.append(char)
            continue
        if char == "#":
            in_comment = True
            continue
        output.append(char)

    return "".join(output)


def check_patterns(challenge: dict, source: str) -> list[str]:
    code = strip_flow_comments(source)
    failures: list[str] = []

    for rule in challenge.get("required", []):
        if re.search(rule["pattern"], code, re.MULTILINE | re.DOTALL) is None:
            failures.append(f"missing required syntax: {rule['label']}")

    for group in challenge.get("required_any", []):
        if not any(
            re.search(rule["pattern"], code, re.MULTILINE | re.DOTALL)
            for rule in group["rules"]
        ):
            choices = ", ".join(rule["label"] for rule in group["rules"])
            failures.append(f"missing one of: {choices}")

    for rule in challenge.get("forbidden", []):
        if re.search(rule["pattern"], code, re.MULTILINE | re.DOTALL) is not None:
            failures.append(f"forbidden shortcut found: {rule['label']}")

    return failures


def run_submission(challenge: dict, submission: Path, timeout: int) -> int:
    command = [part.format(submission=str(submission)) for part in challenge["runner"]]
    env = os.environ.copy()
    if challenge.get("host"):
        env["FLOW_HOST"] = challenge["host"]
    env.update(challenge.get("env", {}))

    print("run:", " ".join(command))
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"FAIL: execution exceeded {timeout} seconds", file=sys.stderr)
        return 1

    if result.returncode != 0:
        print(f"FAIL: program returned {result.returncode}", file=sys.stderr)
        return 1
    print("PASS: required syntax found and program returned zero")
    return 0


def list_challenges(catalog: dict[str, dict]) -> int:
    for item in catalog.values():
        level = "*" * item["difficulty"]
        print(f"{item['id']:>3}  {level:<5}  {item['track']:<18}  {item['title']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check required Flow syntax, then compile and run a challenge submission."
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list", help="list challenge identifiers")

    check_parser = subparsers.add_parser("check", help="check one submission")
    check_parser.add_argument("challenge_id")
    check_parser.add_argument("submission", type=Path)
    check_parser.add_argument("--syntax-only", action="store_true")
    check_parser.add_argument("--timeout", type=int, default=60)

    args = parser.parse_args()
    catalog = load_catalog()

    if args.command in (None, "list"):
        return list_challenges(catalog)

    challenge_id = args.challenge_id.upper()
    if challenge_id not in catalog:
        parser.error(f"unknown challenge id: {challenge_id}")
    challenge = catalog[challenge_id]

    submission = args.submission.resolve()
    if not submission.is_file():
        parser.error(f"submission does not exist: {submission}")
    if submission.suffix != ".flow":
        parser.error("submission must have a .flow suffix")

    source = submission.read_text(encoding="utf-8")
    failures = check_patterns(challenge, source)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print(f"syntax: {challenge_id} {challenge['title']} passed")
    if args.syntax_only or challenge.get("syntax_only", False):
        print("PASS: syntax check complete")
        return 0
    return run_submission(challenge, submission, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
