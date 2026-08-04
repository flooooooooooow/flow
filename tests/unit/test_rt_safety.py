"""
RT-safety compile-time no-alloc enforcement (GitHub issue #134).

`@rt_safe` marks a function as callable from a hard real-time path
(docs/library/rt-safety.md). The type checker rejects any call, direct or
transitive, from an `@rt_safe` function into a heap-touching API
(`malloc`/`calloc`/`realloc`/`free`, or `lib/stdlib/memory.flow` helpers that
call them). Bump allocation from an already-created arena
(`arena_alloc*`, `arena_reset`, `arena_used`, `arena_remaining`) stays
RT-safe, since it never touches the heap itself.
"""

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def check_strict(code: str):
    ast = parse_flow_code(code)
    checker = TypeChecker()
    checker.strict = True
    result = checker.check(ast)
    return result.errors


def rt_errors(errors):
    return [e for e in errors if "RT-safety violation" in e]


MALLOC_EXTERN = """
extern {
    function malloc(size: i64) -> ptr<void>
    function calloc(nmemb: i64, size: i64) -> ptr<void>
    function realloc(p: ptr<void>, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}
"""


def test_rt_safe_function_calling_malloc_is_rejected():
    errors = rt_errors(check_strict(
        MALLOC_EXTERN
        + """
@rt_safe
function process(x: i32) -> i32 {
    let p: ptr<void> = malloc(64)
    return x
}
"""
    ))
    assert len(errors) == 1, errors
    assert "process" in errors[0] and "malloc" in errors[0]


def test_rt_safe_function_calling_free_is_rejected():
    errors = rt_errors(check_strict(
        MALLOC_EXTERN
        + """
@rt_safe
function teardown(p: ptr<void>) -> i32 {
    free(p)
    return 0
}
"""
    ))
    assert len(errors) == 1, errors
    assert "free" in errors[0]


def test_rt_safe_function_calling_calloc_or_realloc_is_rejected():
    errors = rt_errors(check_strict(
        MALLOC_EXTERN
        + """
@rt_safe
function grow(p: ptr<void>) -> i32 {
    let q: ptr<void> = calloc(4, 16)
    let r: ptr<void> = realloc(p, 128)
    return 0
}
"""
    ))
    assert len(errors) == 2, errors


def test_rt_safe_function_calling_stdlib_alloc_helper_is_rejected():
    """`alloc_bytes` etc. wrap malloc/calloc directly (lib/stdlib/memory.flow)."""
    errors = rt_errors(check_strict(
        MALLOC_EXTERN
        + """
function alloc_bytes(size: i64) -> ptr<void> {
    return malloc(size)
}

@rt_safe
function process(x: i32) -> i32 {
    let p: ptr<void> = alloc_bytes(64)
    return x
}
"""
    ))
    assert len(errors) == 1, errors
    assert "alloc_bytes" in errors[0]


def test_rt_safe_function_calling_arena_create_is_rejected():
    """`arena_create` mallocs its backing buffer - setup-only, not RT-safe."""
    errors = rt_errors(check_strict(
        MALLOC_EXTERN
        + """
struct Arena {
    buffer: ptr<i8>,
    capacity: i64,
    offset: i64
}

function arena_create(capacity: i64) -> Arena {
    let raw: ptr<void> = malloc(capacity)
    let buf: ptr<i8> = raw
    return Arena { buffer: buf, capacity: capacity, offset: 0 }
}

@rt_safe
function process(capacity: i64) -> i32 {
    let a: Arena = arena_create(capacity)
    return 0
}
"""
    ))
    assert len(errors) == 1, errors
    assert "arena_create" in errors[0]


def test_rt_safe_function_calling_indirect_allocator_is_rejected():
    """Transitive violation: helper() is not marked, but it calls malloc."""
    errors = rt_errors(check_strict(
        MALLOC_EXTERN
        + """
function helper_alloc(n: i64) -> ptr<void> {
    return malloc(n)
}

@rt_safe
function process(x: i32) -> i32 {
    let p: ptr<void> = helper_alloc(64)
    return x
}
"""
    ))
    assert len(errors) == 1, errors
    assert "helper_alloc" in errors[0] and "malloc" in errors[0]


def test_rt_safe_function_using_only_locals_and_stack_is_accepted():
    """Positive case: arithmetic, branches, and a fixed-bound loop over locals."""
    errors = rt_errors(check_strict(
        """
@rt_safe
function sum_block(block_size: i32) -> i32 {
    let mut total: i32 = 0
    let mut i: i32 = 0
    while i < block_size {
        total = total + i
        i = i + 1
    }
    return total
}
"""
    ))
    assert errors == [], errors


def test_rt_safe_function_using_preallocated_arena_bump_is_accepted():
    """Positive case: bumping a preallocated arena (arena_alloc) is RT-safe;
    only creating/destroying its backing storage is not."""
    errors = rt_errors(check_strict(
        MALLOC_EXTERN
        + """
struct Arena {
    buffer: ptr<i8>,
    capacity: i64,
    offset: i64
}

function arena_alloc(arena: ptr<Arena>, size: i64) -> ptr<void> {
    return null
}

function arena_reset(arena: ptr<Arena>) -> void {
    arena[0].offset = 0
}

@rt_safe
function process_block(arena: ptr<Arena>, block_size: i32) -> i32 {
    let scratch: ptr<void> = arena_alloc(arena, 64)
    arena_reset(arena)
    let mut total: i32 = 0
    let mut i: i32 = 0
    while i < block_size {
        total = total + i
        i = i + 1
    }
    return total
}
"""
    ))
    assert errors == [], errors


def test_non_rt_safe_function_may_call_malloc_freely():
    """Functions without `@rt_safe` are unaffected (e.g. setup/teardown code)."""
    errors = rt_errors(check_strict(
        MALLOC_EXTERN
        + """
function setup(size: i64) -> ptr<void> {
    return malloc(size)
}
"""
    ))
    assert errors == [], errors
