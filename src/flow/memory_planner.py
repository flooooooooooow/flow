import collections
from typing import Dict, List, Set, Tuple

class MemoryPlanner:
    """
    Implements buffer interference graph analysis and static memory lifetime scheduling
    to minimize memory allocation at runtime.

    Limits:
    - This static memory planner operates offline (AOT) assuming deterministic lifetimes.
    - It does not account for dynamic sizing at runtime (buffers must be statically sized).
    - Data-dependent control flow that extends lifetimes arbitrarily isn't modeled accurately by simple start/end times unless worst-case is provided.
    - Only tracks linear offset allocations, it does not do complex memory defragmentation beyond a simple first-fit block allocation.

    """
    def __init__(self):
        self.interference_graph = collections.defaultdict(set)
        self.lifetimes: Dict[str, Tuple[int, int]] = {}
        self.sizes: Dict[str, int] = {}

    def add_buffer(self, name: str, start_time: int, end_time: int, size: int):
        """
        Registers a buffer with its lifetime (start and end times) and size.
        """
        self.lifetimes[name] = (start_time, end_time)
        self.sizes[name] = size
        self._update_interference()

    def _update_interference(self):
        """
        Recomputes the interference graph based on the current lifetimes.
        Two buffers interfere if their lifetimes overlap.
        """
        self.interference_graph.clear()
        buffers = list(self.lifetimes.keys())
        for i in range(len(buffers)):
            for j in range(i + 1, len(buffers)):
                b1, b2 = buffers[i], buffers[j]
                start1, end1 = self.lifetimes[b1]
                start2, end2 = self.lifetimes[b2]

                # Check for overlap: max(start1, start2) < min(end1, end2)
                # Overlap means they interfere
                if max(start1, start2) < min(end1, end2):
                    self.interference_graph[b1].add(b2)
                    self.interference_graph[b2].add(b1)

    def plan(self) -> Dict[str, int]:
        """
        Schedules buffers to memory offsets, reusing space for non-interfering buffers.
        Returns a mapping from buffer name to memory offset.
        """
        offsets = {}

        # Sort buffers by size (descending) to allocate larger buffers first (simple heuristic)
        # Or by start time (linear scan allocation). Let's use start time then size.
        sorted_buffers = sorted(self.lifetimes.keys(), key=lambda b: (self.lifetimes[b][0], -self.sizes[b]))

        allocated = []  # List of tuples: (buffer_name, offset, size)

        for buf in sorted_buffers:
            size = self.sizes[buf]
            interferes_with = self.interference_graph[buf]

            # Find a valid offset
            offset = 0
            while True:
                conflict = False
                for alloc_buf, alloc_offset, alloc_size in allocated:
                    if alloc_buf in interferes_with:
                        # Check if the memory regions overlap:
                        # [offset, offset + size) overlaps with [alloc_offset, alloc_offset + alloc_size)
                        if max(offset, alloc_offset) < min(offset + size, alloc_offset + alloc_size):
                            conflict = True
                            # Move offset past this conflicting buffer
                            offset = alloc_offset + alloc_size
                            break
                if not conflict:
                    break

            offsets[buf] = offset
            allocated.append((buf, offset, size))

        return offsets

    def get_total_size(self, offsets: Dict[str, int]) -> int:
        """
        Calculates the total memory size required for the given plan.
        """
        if not offsets:
            return 0
        return max(offsets[b] + self.sizes[b] for b in offsets)
