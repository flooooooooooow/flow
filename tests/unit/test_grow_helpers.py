"""Tests for uninitialized growth helpers in stdlib/memory.flow (#424)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code


def _parse_stdlib_memory():
    """Parse the stdlib memory.flow file."""
    path = ROOT / "lib" / "stdlib" / "memory.flow"
    return parse_flow_code(path.read_text())


def test_grow_uninit_exists():
    """grow_uninit function is defined in stdlib/memory.flow."""
    decls = _parse_stdlib_memory()
    funcs = [d for d in decls if hasattr(d, "name") and d.name == "grow_uninit"]
    assert len(funcs) == 1


def test_grow_zeroed_exists():
    """grow_zeroed function is defined in stdlib/memory.flow."""
    decls = _parse_stdlib_memory()
    funcs = [d for d in decls if hasattr(d, "name") and d.name == "grow_zeroed"]
    assert len(funcs) == 1


def test_alloc_uninit_exists():
    """alloc_uninit function is defined in stdlib/memory.flow."""
    decls = _parse_stdlib_memory()
    funcs = [d for d in decls if hasattr(d, "name") and d.name == "alloc_uninit"]
    assert len(funcs) == 1


# The C shape and runtime checks are tests/cgen/grow_helpers_memory.
