"""Release-facing security invariants for the Stable Python toolchain.

These tests intentionally cover properties that are easy to regress during
1.x maintenance: no shell-mediated subprocess execution in ``src/flow``, no
race-prone ``tempfile.mktemp`` use, and no legacy import path traversal.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from flow.module_resolver import ModuleResolver


ROOT = Path(__file__).resolve().parents[2]
STABLE_PYTHON = ROOT / "src" / "flow"


def _python_trees():
    for path in sorted(STABLE_PYTHON.rglob("*.py")):
        yield path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _qualified_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _qualified_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def test_stable_python_never_uses_shell_true() -> None:
    offenders: list[str] = []
    for path, tree in _python_trees():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for keyword in node.keywords:
                if keyword.arg != "shell":
                    continue
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert offenders == [], "shell=True in Stable toolchain: " + ", ".join(offenders)


def test_stable_python_avoids_shell_shortcuts() -> None:
    forbidden = {"os.system", "os.popen"}
    offenders: list[str] = []
    for path, tree in _python_trees():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _qualified_name(node.func)
            if name in forbidden:
                offenders.append(f"{path.relative_to(ROOT)}:{node.lineno} ({name})")
    assert offenders == [], "shell shortcut in Stable toolchain: " + ", ".join(offenders)


def test_stable_python_never_uses_tempfile_mktemp() -> None:
    offenders: list[str] = []
    for path, tree in _python_trees():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if _qualified_name(node.func) == "tempfile.mktemp":
                offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert offenders == [], "race-prone tempfile.mktemp use: " + ", ".join(offenders)


@pytest.mark.parametrize(
    "path",
    [
        "../secret.flow",
        "nested/../../secret.flow",
        "/tmp/secret.flow",
        "~/secret.flow",
    ],
)
def test_legacy_imports_reject_path_traversal(path: str) -> None:
    # The rejection happens before search-path state is consulted, so no
    # project fixture is needed to exercise the security boundary itself.
    resolver = object.__new__(ModuleResolver)
    with pytest.raises(FileNotFoundError, match="Unsafe import path"):
        resolver._resolve_legacy_import_path(path, "/tmp/flow-project")
