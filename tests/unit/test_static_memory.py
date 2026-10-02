from flow.static_memory import BufferLifetime, build_interference_graph, plan_static_memory


def test_interference_uses_inclusive_lifetimes() -> None:
    first = BufferLifetime("first", 16, 0, 4)
    second = BufferLifetime("second", 16, 4, 7)
    third = BufferLifetime("third", 16, 5, 8)

    graph = build_interference_graph([first, second, third])

    assert graph["first"] == frozenset({"second"})
    assert graph["second"] == frozenset({"first", "third"})
    assert graph["third"] == frozenset({"second"})


def test_plan_reuses_space_after_lifetime_ends() -> None:
    plan = plan_static_memory(
        [
            BufferLifetime("a", 64, 0, 2),
            BufferLifetime("b", 32, 3, 5),
            BufferLifetime("c", 48, 1, 4),
        ],
        arena_alignment=16,
    )

    assert plan.offsets["a"] == 0
    assert plan.offsets["c"] == 64
    assert plan.offsets["b"] == 0
    assert plan.arena_size == 112


def test_plan_preserves_alignment_and_does_not_overlap_interfering_buffers() -> None:
    items = [
        BufferLifetime("wide", 24, 0, 3, alignment=32),
        BufferLifetime("narrow", 8, 1, 1, alignment=8),
        BufferLifetime("later", 8, 4, 6, alignment=64),
    ]
    plan = plan_static_memory(items, arena_alignment=8)

    assert plan.offsets["wide"] % 32 == 0
    assert plan.offsets["narrow"] % 8 == 0
    assert plan.offsets["later"] % 64 == 0
    for name, neighbours in plan.interference.items():
        for other in neighbours:
            assert plan.offsets[name] != plan.offsets[other]

