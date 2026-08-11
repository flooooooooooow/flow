"""Tests for arena/bump allocator in stdlib/memory.flow (#425).

The stdlib already provides Arena and FrameArena types with
arena_alloc, arena_reset, arena_destroy, frame_begin, frame_alloc,
and frame_end.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _parse_stdlib_memory():
    path = ROOT / "lib" / "stdlib" / "memory.flow"
    return parse_flow_code(path.read_text())


def _gen_c():
    decls = _parse_stdlib_memory()
    return flow_to_c(decls)


def _find_func_names(decls):
    return [d.name for d in decls if hasattr(d, "name")]


def test_arena_struct_exists():
    decls = _parse_stdlib_memory()
    structs = [d for d in decls if hasattr(d, "name") and d.name == "Arena"]
    assert len(structs) == 1


def test_arena_create_exists():
    names = _find_func_names(_parse_stdlib_memory())
    assert "arena_create" in names


def test_arena_alloc_exists():
    names = _find_func_names(_parse_stdlib_memory())
    assert "arena_alloc" in names


def test_arena_reset_exists():
    names = _find_func_names(_parse_stdlib_memory())
    assert "arena_reset" in names


def test_arena_destroy_exists():
    names = _find_func_names(_parse_stdlib_memory())
    assert "arena_destroy" in names


def test_frame_arena_struct_exists():
    decls = _parse_stdlib_memory()
    structs = [d for d in decls if hasattr(d, "name") and d.name == "FrameArena"]
    assert len(structs) == 1


def test_frame_arena_create_exists():
    names = _find_func_names(_parse_stdlib_memory())
    assert "frame_arena_create" in names


def test_frame_begin_exists():
    names = _find_func_names(_parse_stdlib_memory())
    assert "frame_begin" in names


def test_frame_alloc_exists():
    names = _find_func_names(_parse_stdlib_memory())
    assert "frame_alloc" in names


def test_frame_end_exists():
    names = _find_func_names(_parse_stdlib_memory())
    assert "frame_end" in names


def test_arena_alloc_uses_pointer_bump():
    """arena_alloc advances offset by aligned size."""
    c = _gen_c()
    lines = c.splitlines()
    in_impl = False
    brace_depth = 0
    body = []
    for line in lines:
        if "arena_alloc_ptr" in line and "{" in line and ";" not in line.split("{")[0]:
            in_impl = True
        if in_impl:
            body.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "{" in "\n".join(body):
                break
    body_str = "\n".join(body)
    assert "offset" in body_str
    assert "align" in body_str or "aligned" in body_str


def test_arena_reset_zeros_offset():
    """arena_reset sets offset to 0."""
    c = _gen_c()
    lines = c.splitlines()
    in_impl = False
    brace_depth = 0
    body = []
    for line in lines:
        if "arena_reset" in line and "{" in line and ";" not in line.split("{")[0]:
            in_impl = True
        if in_impl:
            body.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "{" in "\n".join(body):
                break
    body_str = "\n".join(body)
    assert "offset" in body_str
    assert "0" in body_str
