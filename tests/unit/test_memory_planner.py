import pytest
from flow.memory_planner import MemoryPlanner

def test_no_interference():
    planner = MemoryPlanner()
    planner.add_buffer("A", 0, 10, 100)
    planner.add_buffer("B", 10, 20, 100)

    offsets = planner.plan()
    assert offsets["A"] == 0
    assert offsets["B"] == 0
    assert planner.get_total_size(offsets) == 100

def test_interference():
    planner = MemoryPlanner()
    planner.add_buffer("A", 0, 10, 100)
    planner.add_buffer("B", 5, 15, 50)

    offsets = planner.plan()
    assert offsets["A"] == 0
    assert offsets["B"] == 100
    assert planner.get_total_size(offsets) == 150

def test_complex_scheduling():
    planner = MemoryPlanner()
    planner.add_buffer("A", 0, 10, 50)
    planner.add_buffer("B", 5, 15, 60)
    planner.add_buffer("C", 12, 20, 40)
    planner.add_buffer("D", 8, 25, 30)

    offsets = planner.plan()
    # A overlaps B, D
    # B overlaps A, D, C
    # C overlaps B, D
    # D overlaps A, B, C

    assert offsets["A"] == 0
    assert offsets["B"] == 50
    # C starts at 12. A ends at 10. C and A don't overlap.
    # Since C is 40 and A is 50, C can be placed at 0.
    assert offsets["C"] == 0
    # D overlaps A, B, C.
    # A is at 0..50
    # B is at 50..110
    # C is at 0..40
    assert offsets["D"] == 110
    assert planner.get_total_size(offsets) == 140

def test_interference_graph_generation():
    planner = MemoryPlanner()
    planner.add_buffer("A", 0, 5, 10)
    planner.add_buffer("B", 5, 10, 10)
    planner.add_buffer("C", 4, 6, 10)

    assert "B" not in planner.interference_graph["A"]
    assert "C" in planner.interference_graph["A"]
    assert "C" in planner.interference_graph["B"]
