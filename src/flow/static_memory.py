"""Static scratchpad planning for non-overlapping compiler buffers.

The planner operates on buffer live intervals. It is deliberately independent
of an MLIR binding so the same plan can be consumed by the textual emitter,
the native lowering, or a target-specific scratchpad allocator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BufferLifetime:
    """A buffer's inclusive live interval and byte size."""

    name: str
    size: int
    start: int
    end: int
    alignment: int = 1

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("buffer name must not be empty")
        if self.size <= 0:
            raise ValueError("buffer size must be positive")
        if self.start < 0 or self.end < self.start:
            raise ValueError("buffer lifetime must satisfy 0 <= start <= end")
        if self.alignment <= 0 or self.alignment & (self.alignment - 1):
            raise ValueError("buffer alignment must be a positive power of two")


@dataclass(frozen=True)
class MemoryPlan:
    """Offsets for one contiguous arena."""

    offsets: dict[str, int]
    arena_size: int
    interference: dict[str, frozenset[str]]


def _align(value: int, alignment: int) -> int:
    return (value + alignment - 1) & -alignment


def build_interference_graph(
    lifetimes: Iterable[BufferLifetime],
) -> dict[str, frozenset[str]]:
    """Return the symmetric graph of buffers with overlapping lifetimes.

    Endpoints are inclusive. A buffer ending at operation 4 overlaps one
    beginning at operation 4 because both may be used by that operation.
    """

    items = list(lifetimes)
    names = [item.name for item in items]
    if len(set(names)) != len(names):
        raise ValueError("buffer names must be unique")
    graph = {item.name: set() for item in items}
    for index, left in enumerate(items):
        for right in items[index + 1 :]:
            if left.start <= right.end and right.start <= left.end:
                graph[left.name].add(right.name)
                graph[right.name].add(left.name)
    return {name: frozenset(neighbours) for name, neighbours in graph.items()}


def plan_static_memory(
    lifetimes: Iterable[BufferLifetime],
    *,
    arena_alignment: int = 1,
) -> MemoryPlan:
    """Pack non-overlapping buffers into a contiguous arena.

    The allocator uses a first-fit scan over released blocks. It is stable for
    equal intervals and preserves every buffer's requested alignment. Buffers
    with overlapping intervals can never share bytes.
    """

    items = list(lifetimes)
    if arena_alignment <= 0 or arena_alignment & (arena_alignment - 1):
        raise ValueError("arena alignment must be a positive power of two")
    graph = build_interference_graph(items)
    offsets: dict[str, int] = {}
    active: list[tuple[int, BufferLifetime]] = []
    free: list[tuple[int, int]] = []
    arena_size = 0

    for item in sorted(items, key=lambda value: (value.start, value.end, value.name)):
        still_active: list[tuple[int, BufferLifetime]] = []
        for end, other in active:
            if end < item.start:
                free.append((offsets[other.name], other.size))
            else:
                still_active.append((end, other))
        active = still_active
        free.sort()

        chosen = None
        for block_index, (block_offset, block_size) in enumerate(free):
            aligned = _align(block_offset, max(item.alignment, arena_alignment))
            padding = aligned - block_offset
            if padding + item.size <= block_size:
                chosen = (block_index, aligned, block_offset, block_size)
                break
        if chosen is None:
            aligned = _align(arena_size, max(item.alignment, arena_alignment))
            offsets[item.name] = aligned
            arena_size = aligned + item.size
        else:
            block_index, aligned, block_offset, block_size = chosen
            offsets[item.name] = aligned
            del free[block_index]
            before = aligned - block_offset
            after_start = aligned + item.size
            after = block_offset + block_size - after_start
            if before:
                free.append((block_offset, before))
            if after:
                free.append((after_start, after))

        active.append((item.end, item))

    return MemoryPlan(offsets, _align(arena_size, arena_alignment), graph)

