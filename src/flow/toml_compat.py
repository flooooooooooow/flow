"""Small TOML loader fallback for source checkouts on Python 3.9/3.10.

Flow declares ``tomli`` for these Python versions, but the source launcher is
also expected to work before the project has been installed.  This fallback
covers the TOML subset used by ``flow.toml`` and ``flow.lock`` project setup:
tables, strings, booleans, numbers, arrays, and inline tables.
"""

from __future__ import annotations

import ast
from typing import Any, Dict, List

try:
    import tomllib as _tomllib
except ImportError:  # pragma: no cover - exercised on Python 3.9/3.10
    try:
        import tomli as _tomllib  # type: ignore
    except ImportError:  # pragma: no cover - fallback is the point of this module
        _tomllib = None


def _split_top_level(value: str, delimiter: str = ",") -> List[str]:
    parts: List[str] = []
    start = 0
    depth = 0
    quote = ""
    escaped = False
    for index, char in enumerate(value):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        elif char == delimiter and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return [part for part in parts if part]


def _strip_comment(value: str) -> str:
    quote = ""
    escaped = False
    for index, char in enumerate(value):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char == "#":
            return value[:index].rstrip()
    return value.strip()


def _parse_value(value: str) -> Any:
    value = value.strip()
    if value.startswith(("\"", "'")):
        return ast.literal_eval(value)
    if value in ("true", "false"):
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        return [_parse_value(item) for item in _split_top_level(value[1:-1])]
    if value.startswith("{") and value.endswith("}"):
        result: Dict[str, Any] = {}
        for item in _split_top_level(value[1:-1]):
            key, raw = item.split("=", 1)
            result[key.strip().strip("\"'")] = _parse_value(raw)
        return result
    try:
        return float(value) if any(c in value for c in ".eE") else int(value)
    except ValueError:
        return value


def _fallback_loads(text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    current: Dict[str, Any] = result
    for raw_line in text.splitlines():
        line = _strip_comment(raw_line.strip())
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = result
            for section in line[1:-1].split("."):
                current = current.setdefault(section.strip().strip("\"'"), {})
            continue
        if "=" not in line:
            raise ValueError(f"unsupported flow.toml line: {raw_line}")
        key, value = line.split("=", 1)
        current[key.strip().strip("\"'")] = _parse_value(value)
    return result


def loads(text: str) -> Dict[str, Any]:
    if _tomllib is not None:
        return _tomllib.loads(text)
    return _fallback_loads(text)
