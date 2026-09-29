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


def _parse_stdlib_memory():
    path = ROOT / "lib" / "stdlib" / "memory.flow"
    return parse_flow_code(path.read_text())


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


# The C-shape checks on arena_alloc and arena_reset are now
# tests/cgen/arena_bump.flow, which runs the arena through flowc.
