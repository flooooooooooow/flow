"""Tests for uninitialized growth helpers in stdlib/memory.flow (#424)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _parse_stdlib_memory():
    """Parse the stdlib memory.flow file."""
    path = ROOT / "lib" / "stdlib" / "memory.flow"
    return parse_flow_code(path.read_text())


def _gen_c():
    decls = _parse_stdlib_memory()
    return flow_to_c(decls)


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


def test_grow_uninit_uses_realloc():
    """grow_uninit calls realloc in its implementation."""
    c = _gen_c()
    # Find the implementation (not the prototype)
    lines = c.splitlines()
    in_impl = False
    brace_depth = 0
    body = []
    for line in lines:
        if "grow_uninit" in line and "{" in line and ";" not in line.split("{")[0]:
            in_impl = True
        if in_impl:
            body.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "{" in "\n".join(body):
                break
    body_str = "\n".join(body)
    assert "realloc" in body_str


def test_grow_zeroed_zeros_new_region():
    """grow_zeroed uses realloc and has a zeroing loop."""
    c = _gen_c()
    lines = c.splitlines()
    in_impl = False
    brace_depth = 0
    body = []
    for line in lines:
        if "grow_zeroed" in line and "{" in line and ";" not in line.split("{")[0]:
            in_impl = True
        if in_impl:
            body.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "{" in "\n".join(body):
                break
    body_str = "\n".join(body)
    assert "realloc" in body_str
    # Should have a loop for the delta region
    assert "while" in body_str or "for" in body_str


def test_alloc_uninit_uses_malloc():
    """alloc_uninit calls malloc in its implementation."""
    c = _gen_c()
    lines = c.splitlines()
    in_impl = False
    brace_depth = 0
    body = []
    for line in lines:
        if "alloc_uninit" in line and "{" in line and ";" not in line.split("{")[0]:
            in_impl = True
        if in_impl:
            body.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "{" in "\n".join(body):
                break
    body_str = "\n".join(body)
    assert "malloc" in body_str
