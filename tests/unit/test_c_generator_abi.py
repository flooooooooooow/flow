"""C backend ABI / lowering contracts — soft goldens (substring asserts)."""

from tests.unit.compiler_helpers import to_c, needs_clang, compile_c_only, compile_and_run


def test_effect_handlers_are_thread_local():
    c = to_c(
        """
effect Log {
    write(msg: i32) -> void,
}
function main() -> i32 { return 0 }
"""
    )
    assert "_Thread_local" in c
    assert "_current_Log_handler" in c


def test_handle_saves_and_restores_handler():
    c = to_c(
        """
effect Log {
    write(msg: i32) -> void,
}
capability Sink {
    effect Log,
    function write(msg: i32) -> void { return },
}
function main() -> i32 {
    handle Log with Sink {
        Log.write(1)
    }
    return 0
}
"""
    )
    # Save/restore pattern around handle blocks
    assert "_current_Log_handler" in c
    assert "Sink" in c


def test_parallel_for_openmp_guards():
    c = to_c(
        """
function main() -> i32 {
    parallel for i in 0 to 8 {
        let x: i32 = i
    }
    return 0
}
"""
    )
    assert "#ifdef _OPENMP" in c
    assert "#pragma omp parallel for" in c


def test_extern_calls_remain_unmangled():
    c = to_c(
        """
extern {
    function puts(s: string) -> i32
}
function main() -> i32 {
    puts("hi")
    return 0
}
"""
    )
    assert "puts(" in c
    # Should not invent a Flow-style mangled wrapper name for the call
    assert "flow_puts" not in c


def test_debug_line_directives_emitted():
    c = to_c(
        """
function main() -> i32 {
    let x: i32 = 1
    return x
}
""",
        debug_info=True,
        source_file="/tmp/demo.flow",
    )
    assert "#line" in c
    assert "demo.flow" in c


def test_strict_effects_emits_abort_helper():
    c = to_c(
        """
effect Log {
    write(msg: i32) -> void,
}
function main() -> i32 {
    Log.write(1)
    return 0
}
""",
        strict_effects=True,
    )
    assert "_flow_unhandled_effect" in c or "abort" in c


def test_struct_and_array_lower_to_c():
    c = to_c(
        """
struct Point { x: i32, y: i32 }
function main() -> i32 {
    let mut pts: array<Point, 2> = [Point { x: 1, y: 2 }, Point { x: 3, y: 4 }]
    pts[0].x = 9
    return pts[0].x + pts[1].y
}
"""
    )
    assert "typedef struct Point" in c or "struct Point" in c
    assert "Point" in c


def test_escaping_closure_fat_pointer_abi():
    c = to_c(
        """
function main() -> i32 {
    let n: i32 = 5
    let add_n: (i32) -> i32 = |x: i32| -> i32 { return x + n }
    return add_n(10)
}
"""
    )
    assert "fn_i32__i32" in c
    assert ".env" in c


@needs_clang
def test_clang_accepts_basic_abi_program():
    compile_c_only(
        """
struct Point { x: i32, y: i32 }
function add(a: i32, b: i32) -> i32 { return a + b }
function main() -> i32 {
    let p: Point = Point { x: 10, y: 32 }
    return add(p.x, p.y) - 42
}
"""
    )


# test_e2e_struct_field_math is now tests/lang/test_structs.flow.
# test_e2e_generic_box_after_mono stays: it uses the *inferred* generic
# struct literal `let b: Box<i32> = Box { value: 42 }`, which strict mode
# still rejects ("field 'value' expects T, got i32"), so it cannot become
# a strict-clean tests/lang program. tests/lang/test_generics.flow covers
# the explicit `Box<i32> { value: 42 }` spelling.


@needs_clang
def test_e2e_generic_box_after_mono():
    rc = compile_and_run(
        """
struct Box<T> { value: T }
function main() -> i32 {
    let b: Box<i32> = Box { value: 42 }
    if b.value == 42 {
        return 0
    }
    return 1
}
"""
    )
    assert rc == 0


def test_multi_handle_emits_multiple_tls_pointers():
    c = to_c(
        """
effect A { op() -> i32 }
effect B { op() -> i32 }
capability CA {
    effect A,
    function op() -> i32 { return 1 },
}
capability CB {
    effect B,
    function op() -> i32 { return 2 },
}
function main() -> i32 {
    handle A, B with CA, CB {
        return A.op() + B.op() - 3
    }
    return 1
}
"""
    )
    assert "_current_A_handler" in c
    assert "_current_B_handler" in c
    assert "_Thread_local" in c
