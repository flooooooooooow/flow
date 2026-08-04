#!/usr/bin/env python3
"""
Flow project configuration — loads flow.toml and exposes [paths] roots.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib
except ImportError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


@dataclass
class ProjectConfig:
    """Resolved project configuration."""

    project_root: str
    name: str = "flow"
    version: str = "0.1.0"
    entry: str = ""
    paths: Dict[str, str] = field(default_factory=dict)
    dependencies: Dict[str, Any] = field(default_factory=dict)

    @property
    def stdlib_root(self) -> str:
        """Built-in std.* maps to lib/stdlib (project-local or compiler fallback)."""
        if "stdlib" in self.paths:
            candidate = os.path.join(self.project_root, self.paths["stdlib"])
        else:
            candidate = os.path.join(self.project_root, "lib", "stdlib")
        if os.path.isdir(candidate):
            return candidate
        compiler_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        return os.path.join(compiler_root, "lib", "stdlib")


def _parse_toml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if tomllib is None:
        raise RuntimeError("tomllib/tomli required to read flow.toml")
    return tomllib.loads(text)


def find_flow_toml(start_path: str) -> Optional[str]:
    """Walk upward from start_path until flow.toml is found."""
    current = Path(start_path).resolve()
    if current.is_file():
        current = current.parent
    while True:
        candidate = current / "flow.toml"
        if candidate.is_file():
            return str(candidate)
        parent = current.parent
        if parent == current:
            return None
        current = parent


def load_project_config(
    start_path: Optional[str] = None,
    *,
    fallback_root: Optional[str] = None,
) -> ProjectConfig:
    """
    Load flow.toml relative to start_path (file or directory).
    Falls back to compiler package root when no flow.toml exists.
    """
    search = start_path or fallback_root
    toml_path = find_flow_toml(search) if search else None

    if toml_path:
        data = _parse_toml(Path(toml_path))
        project_root = str(Path(toml_path).parent)
        package = data.get("package", {})
        paths = {k: v for k, v in data.get("paths", {}).items() if isinstance(v, str)}
        dependencies = data.get("dependencies", {})
        if not isinstance(dependencies, dict):
            dependencies = {}
        return ProjectConfig(
            project_root=project_root,
            name=package.get("name", "flow"),
            version=package.get("version", "0.1.0"),
            entry=package.get("entry", ""),
            paths=paths,
            dependencies=dependencies,
        )

    if fallback_root is None:
        fallback_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
    return ProjectConfig(project_root=fallback_root, paths={})
