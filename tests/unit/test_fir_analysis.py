import pytest
from flow.fir_g import (
    FirG, OpCode, EFF_IO, EFF_ALLOCATES, EFF_NONE, EFF_READS_MEMORY,
    EFF_WRITES_MEMORY, EFF_FFI, EFF_UNKNOWN, EFF_GPU, EFF_PANIC, EFF_ATOMIC
)
from flow.fir_analysis import propagate_effects, purity_flags

def test_propagate_effects_max_iters():
    g = FirG()
    f0 = g.add_function("f0")
    b0 = g.add_block(f0)

    f1 = g.add_function("f1")
    b1 = g.add_block(f1)

    f2 = g.add_function("f2")
    b2 = g.add_block(f2)

    # f0 calls f1
    g.add_op(OpCode.CALL, f0, b0, callee=f1)
    # f1 calls f2
    g.add_op(OpCode.CALL, f1, b1, callee=f2)

    g.func_effect_bits = [0, 0, EFF_IO]

    # 1 iteration: f1 gets f2's effect, but f0 doesn't get f1's yet
    bits_1 = propagate_effects(g, max_iters=1)
    assert bits_1 == [0, EFF_IO, EFF_IO]

    # 2 iterations: f0 now gets f1's effect
    g.func_effect_bits = [0, 0, EFF_IO]
    bits_2 = propagate_effects(g, max_iters=2)
    assert bits_2 == [EFF_IO, EFF_IO, EFF_IO]

def test_propagate_effects_no_effects():
    g = FirG()
    f0 = g.add_function("f0")
    b0 = g.add_block(f0)

    f1 = g.add_function("f1")
    b1 = g.add_block(f1)

    # f0 calls f1
    g.add_op(OpCode.CALL, f0, b0, callee=f1)

    g.func_effect_bits = [0, 0]

    bits = propagate_effects(g, max_iters=10)
    assert bits == [0, 0]

def test_propagate_effects_cyclic():
    g = FirG()
    f0 = g.add_function("f0")
    b0 = g.add_block(f0)

    f1 = g.add_function("f1")
    b1 = g.add_block(f1)

    f2 = g.add_function("f2")
    b2 = g.add_block(f2)

    # cycle: f0 -> f1 -> f2 -> f0
    g.add_op(OpCode.CALL, f0, b0, callee=f1)
    g.add_op(OpCode.CALL, f1, b1, callee=f2)
    g.add_op(OpCode.CALL, f2, b2, callee=f0)

    g.func_effect_bits = [0, 0, EFF_ALLOCATES]

    bits = propagate_effects(g, max_iters=10)
    assert bits == [EFF_ALLOCATES, EFF_ALLOCATES, EFF_ALLOCATES]

def test_propagate_effects_empty_graph():
    g = FirG()
    bits = propagate_effects(g)
    assert bits == []

def test_purity_flags():
    g = FirG()
    g.add_function("f_pure1")
    g.add_function("f_pure2")
    g.add_function("f_pure3")
    g.add_function("f_impure_io")
    g.add_function("f_impure_ffi")
    g.add_function("f_impure_alloc")
    g.add_function("f_impure_write")
    g.add_function("f_impure_unknown")
    g.add_function("f_impure_gpu")

    # Manually assign effect bits
    g.func_effect_bits = [
        EFF_NONE,                                      # f_pure1 (pure)
        EFF_READS_MEMORY,                              # f_pure2 (pure: read-only)
        EFF_PANIC | EFF_ATOMIC,                        # f_pure3 (pure: panic/atomic is allowed)
        EFF_IO,                                        # f_impure_io
        EFF_FFI,                                       # f_impure_ffi
        EFF_ALLOCATES,                                 # f_impure_alloc
        EFF_WRITES_MEMORY,                             # f_impure_write
        EFF_UNKNOWN,                                   # f_impure_unknown
        EFF_GPU,                                       # f_impure_gpu
    ]

    flags = purity_flags(g)
    assert flags["f_pure1"] is True
    assert flags["f_pure2"] is True
    assert flags["f_pure3"] is True
    assert flags["f_impure_io"] is False
    assert flags["f_impure_ffi"] is False
    assert flags["f_impure_alloc"] is False
    assert flags["f_impure_write"] is False
    assert flags["f_impure_unknown"] is False
    assert flags["f_impure_gpu"] is False
