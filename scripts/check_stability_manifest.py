#!/usr/bin/env python3
"""Validate Flow's machine-readable 1.0 stability surface manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "stability" / "surfaces.json"
ALLOWED_CLASSES = {"stable", "experimental", "reserved-future", "internal"}
ALLOWED_KINDS = {
    "language",
    "language-feature",
    "language-domain",
    "standard-library",
    "runtime",
    "cli",
    "manifest",
    "target",
}


def fail(message: str) -> None:
    raise SystemExit(f"stability manifest: {message}")


def validate(*, require_complete: bool) -> None:
    data = json.loads(MANIFEST.read_text())

    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    if data.get("release") != "1.0.0":
        fail("release must be 1.0.0")

    declared_classes = set(data.get("classes", []))
    if declared_classes != ALLOWED_CLASSES:
        fail(
            "classes must be exactly: "
            + ", ".join(sorted(ALLOWED_CLASSES))
        )

    surfaces = data.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        fail("surfaces must be a non-empty list")

    seen: set[str] = set()
    pending: list[str] = []

    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict):
            fail(f"surfaces[{index}] must be an object")

        surface_id = surface.get("id")
        if not isinstance(surface_id, str) or not surface_id:
            fail(f"surfaces[{index}].id must be a non-empty string")
        if surface_id in seen:
            fail(f"duplicate surface id: {surface_id}")
        seen.add(surface_id)

        kind = surface.get("kind")
        if kind not in ALLOWED_KINDS:
            fail(f"{surface_id}: unknown kind {kind!r}")

        classification = surface.get("classification")
        if classification == "pending":
            pending.append(surface_id)
        elif classification not in ALLOWED_CLASSES:
            fail(
                f"{surface_id}: classification must be one of "
                f"{sorted(ALLOWED_CLASSES)} or 'pending' during stabilisation"
            )

        source = surface.get("source")
        if not isinstance(source, str) or not source:
            fail(f"{surface_id}: source must be a non-empty repository path")
        if not (ROOT / source).exists():
            fail(f"{surface_id}: source path does not exist: {source}")

        owner_issue = surface.get("owner_issue")
        if not isinstance(owner_issue, int) or owner_issue <= 0:
            fail(f"{surface_id}: owner_issue must be a positive issue number")

    if require_complete and pending:
        fail(
            "RC classification incomplete; pending surfaces: "
            + ", ".join(sorted(pending))
        )

    state = "complete" if not pending else f"{len(pending)} pending"
    print(f"stability manifest OK: {len(surfaces)} surfaces, {state}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="fail if any surface is still classified as pending (RC1 gate)",
    )
    args = parser.parse_args()
    validate(require_complete=args.require_complete)


if __name__ == "__main__":
    main()
