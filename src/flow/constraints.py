"""Parser and selector helpers for require/prefer constraints (#147).

Flow's constraint vocabulary for multi-implementation selection:

* `require <resource> < <value>`: hard constraint. Rejects implementations
  that cannot meet the budget.
* `prefer <objective>`: soft preference. Biases the cost model toward
  implementations that match the objective ("latency", "energy", "memory",
  "parallel").

These are parsed from attribute syntax and fed into the Facts data dict
that the plan selector reads. The selector itself stays construct-agnostic.

Example Flow syntax (future, once sugar lands):

    @require(memory < 4096)
    @prefer(parallel)
    let result = xs |> reduce(sum)

For now, constraints are set programmatically by the compiler when it
builds Facts for a selection site. The parser for the attribute form is
here so it can be wired in once the surface syntax is finalised.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

__all__ = [
    "parse_require",
    "parse_prefer",
    "constraints_to_facts",
    "REQUIRE_RE",
    "PREFER_RE",
]


# require(memory < 4096)  ->  resource="memory", op="<", value=4096
REQUIRE_RE = re.compile(
    r"require\s*\(\s*(\w+)\s*(<=|<|>=|>|==)\s*(\d+)\s*\)"
)

# prefer(parallel)  ->  objective="parallel"
PREFER_RE = re.compile(
    r"prefer\s*\(\s*(\w+)\s*\)"
)


def parse_require(text: str) -> Optional[Tuple[str, str, int]]:
    """Parse a `require(resource op value)` constraint.

    Returns (resource, operator, value) or None if the text does not match.
    """
    m = REQUIRE_RE.search(text)
    if not m:
        return None
    resource, op, value = m.group(1), m.group(2), int(m.group(3))
    return resource, op, value


def parse_prefer(text: str) -> Optional[str]:
    """Parse a `prefer(objective)` constraint.

    Returns the objective string or None if the text does not match.
    """
    m = PREFER_RE.search(text)
    if not m:
        return None
    return m.group(1)


def constraints_to_facts(
    requires: list[str] = (),
    prefers: list[str] = (),
) -> Dict[str, Any]:
    """Convert parsed require/prefer constraints into Facts data entries.

    `require(memory < 4096)` becomes `require_memory_bytes = 4096`.
    `prefer(parallel)` becomes `prefer = "parallel"`.

    If multiple requires target the same resource, the tightest (smallest
    for `<` / `<=`, largest for `>` / `>=`) wins.
    """
    data: Dict[str, Any] = {}

    for req in requires:
        parsed = parse_require(req)
        if parsed is None:
            continue
        resource, op, value = parsed
        key = f"require_{resource}_bytes" if resource in ("memory", "scratch") else f"require_{resource}"
        if op in ("<", "<="):
            existing = data.get(key)
            if existing is None or value < existing:
                data[key] = value
        elif op in (">", ">="):
            existing = data.get(key)
            if existing is None or value > existing:
                data[key] = value
        else:
            data[key] = value

    for pref in prefers:
        parsed = parse_prefer(pref)
        if parsed is None:
            continue
        data["prefer"] = parsed

    return data
