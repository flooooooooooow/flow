"""IntelliSense data for declarative ordering (`|> sort` / `sortBy`)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

KIND_KEYWORD = 14
KIND_SNIPPET = 15

ORDERING_HOVER: Dict[str, str] = {
    "sort": (
        "**`sort`** — declarative ordering (Phase 1).\n\n"
        "```flow\nxs |> sort\nxs |> sort descending\n"
        "xs |> sort by .score\n"
        "xs |> sortBy [desc .score, asc .name]\n```\n"
        "In-place on `array<T, N>`. See docs/language/ordering.md."
    ),
    "sortBy": (
        "**`sortBy`** — multi-key ordering alias for `sort by [...]`.\n\n"
        "```flow\nxs |> sortBy [asc .score, asc .name]\n```"
    ),
    "asc": "`asc .field` — ascending key in a sort key list.",
    "desc": "`desc .field` — descending key in a sort key list.",
    "unique": "`sort unique` — sort then compact adjacent duplicates (prefix; N unchanged).",
    "entropy": "`with entropy` / `with entropy(seed: N)` — allow randomized strategies (parsed; Phase 2).",
    "order": "`order` — declarative ordering head (same family as `sort`).",
}


def ordering_completion_items(prefix: str = "") -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    snippets = [
        ("sort", "${1:xs} |> sort", "Declarative ascending sort"),
        (
            "sortBy",
            "${1:xs} |> sortBy [${2|asc,desc|} .${3:score}, "
            "${4|asc,desc|} .${5:name}]",
            "Multi-key declarative sort",
        ),
        ("sort by", "${1:xs} |> sort by .${2:field}", "Sort by one field"),
        (
            "sort descending",
            "${1:xs} |> sort descending",
            "Declarative descending sort",
        ),
        ("asc", "asc .${1:field}", "Ascending sort key"),
        ("desc", "desc .${1:field}", "Descending sort key"),
    ]
    for label, insert, detail in snippets:
        if prefix and not label.startswith(prefix) and prefix not in label:
            continue
        items.append(
            {
                "label": label,
                "kind": KIND_SNIPPET,
                "detail": detail,
                "insertText": insert,
                "insertTextFormat": 2,
                "documentation": ORDERING_HOVER.get(label.split()[0], detail),
            }
        )
    for kw, doc in ORDERING_HOVER.items():
        if prefix and not kw.startswith(prefix):
            continue
        if any(it["label"] == kw for it in items):
            continue
        items.append(
            {
                "label": kw,
                "kind": KIND_KEYWORD,
                "detail": "ordering",
                "documentation": doc,
            }
        )
    return items


def ordering_hover(word: str) -> Optional[str]:
    return ORDERING_HOVER.get(word)
