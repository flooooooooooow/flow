"""Project-level conventions reader for flow.toml (#415).

Reads the [conventions] and [build] sections from flow.toml.
Provides pattern matching for avoid patterns and access to build
settings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class AvoidPattern:
    """A pattern to avoid, with reason and workaround."""
    pattern: str
    reason: str = ""
    workaround: str = ""


@dataclass
class BuildSettings:
    """Build settings from flow.toml."""
    host: str = ""
    test_command: str = ""
    test_all: str = ""


@dataclass
class Conventions:
    """Project conventions parsed from flow.toml."""
    avoid: List[AvoidPattern] = field(default_factory=list)
    patterns: Dict[str, str] = field(default_factory=dict)
    build: BuildSettings = field(default_factory=BuildSettings)


def find_flow_toml(start: Optional[Path] = None) -> Optional[Path]:
    """Walk up from start to find flow.toml."""
    p = (start or Path.cwd()).resolve()
    for parent in [p] + list(p.parents):
        candidate = parent / "flow.toml"
        if candidate.exists():
            return candidate
    return None


def load_conventions(start: Optional[Path] = None) -> Conventions:
    """Load conventions from flow.toml, or empty if not found."""
    path = find_flow_toml(start)
    if path is None:
        return Conventions()
    if tomllib is None:
        return Conventions()
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return Conventions()

    conv = Conventions()
    build_data = data.get("build", {})
    conv.build = BuildSettings(
        host=build_data.get("host", ""),
        test_command=build_data.get("test_command", ""),
        test_all=build_data.get("test_all", ""),
    )

    for item in data.get("conventions", {}).get("avoid", []):
        if isinstance(item, dict):
            conv.avoid.append(AvoidPattern(
                pattern=item.get("pattern", ""),
                reason=item.get("reason", ""),
                workaround=item.get("workaround", ""),
            ))

    patterns_data = data.get("patterns", {})
    if isinstance(patterns_data, dict):
        conv.patterns = {k: v for k, v in patterns_data.items() if isinstance(v, str)}

    return conv


def check_file(source_path: Path, conv: Optional[Conventions] = None) -> List[str]:
    """Check a .flow file for avoid patterns. Returns warning messages."""
    if conv is None:
        conv = load_conventions(source_path.parent)
    if not conv.avoid:
        return []
    try:
        source = source_path.read_text()
    except Exception:
        return []
    warnings: List[str] = []
    for ap in conv.avoid:
        if not ap.pattern:
            continue
        if _matches_pattern(source, ap.pattern):
            msg = f"{source_path}: avoid '{ap.pattern}'"
            if ap.reason:
                msg += f" - {ap.reason}"
            if ap.workaround:
                msg += f" (workaround: {ap.workaround})"
            warnings.append(msg)
    return warnings


def _matches_pattern(source: str, pattern: str) -> bool:
    """Check if source matches an avoid pattern.

    Patterns are matched as substring or regex depending on content.
    Simple text patterns use substring match. Patterns containing
    regex metacharacters use regex.
    """
    if any(c in pattern for c in r"[](){}.*+?^$|\\"):
        try:
            return bool(re.search(pattern, source))
        except re.error:
            pass
    return pattern.lower() in source.lower()
