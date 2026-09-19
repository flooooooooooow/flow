"""Domain-bound allocation tracking for arenas and heap regions (issue #690).

Memory bumped from an arena or region allocator carries the lifetime domain of
the arena instance it came from. The v0 checker
(tests/unit/test_lifetime_domains.py) already binds the return of
`arena_alloc(a, size)` to its arena argument `a` and, when the writing function
declares a domain, rejects storing that pointer in a longer-lived static, field,
or return.

This file pins the extension #690 adds: when the arena argument names a *module
static* arena instance, the checker reads that arena's own declared
`@lifetime(D)` and uses it as the pointer's domain. That is provable from the
arena declaration alone, so:

  * a frame arena bumped into a longer-lived static or annotated field is
    rejected, even from a function that declares no domain of its own;
  * an arena declared to live as long as (or longer than) the place its memory
    is stored is allowed;
  * an unannotated arena defaults to `application` and so never triggers an
    escape, and an arena whose provenance is not a named static (a parameter or
    a local) falls back to the v0 writer-domain rule.

Ambiguous provenance is allowed. The rule adds no false positive to code that
does not declare a shorter-lived arena.
"""

from __future__ import annotations

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


ARENA = """
struct Arena {
    buffer: ptr<i8>,
    capacity: i64,
    offset: i64
}

function arena_alloc(a: ptr<Arena>, size: i64) -> ptr<void> {
    let off: i64 = a[0].offset
    let base: ptr<i8> = a[0].buffer
    a[0].offset = off + size
    return base + off
}

function arena_reset(a: ptr<Arena>) -> void {
    a[0].offset = 0
}
"""


def domain_errors(source: str):
    checker = TypeChecker()
    checker.strict = True
    return [
        e for e in checker.check(parse_flow_code(source)).errors
        if "lifetime domain" in e or "RT-safety violation" in e
    ]


def only_error(source: str) -> str:
    found = domain_errors(source)
    assert len(found) == 1, found
    return found[0]


# --- Positive: a frame arena's memory may not outlive its domain ------------


def test_frame_arena_pointer_stored_in_an_application_static_is_rejected():
    assert only_error(
        ARENA
        + """
@lifetime(frame)
let mut fa: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

@lifetime(application)
let mut cache: ptr<void> = null

@lifetime(session)
function build() -> void {
    cache = arena_alloc(&fa, 64)
}
"""
    ) == (
        "lifetime domain escape: `fa` lives in the `frame` domain but is "
        "stored in `cache`, which lives in the `application` domain "
        "(a longer-lived domain may not hold a reference to a shorter-lived "
        "one) at line 27, column 5"
    )


def test_the_arena_declaration_alone_is_enough_to_catch_the_escape():
    # The writing function declares no domain. The arena instance carries the
    # signal, so the escape is still proven and rejected.
    assert only_error(
        ARENA
        + """
@lifetime(frame)
let mut fa: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

@lifetime(application)
let mut cache: ptr<void> = null

function build() -> void {
    cache = arena_alloc(&fa, 64)
}
"""
    ).startswith(
        "lifetime domain escape: `fa` lives in the `frame` domain but is "
        "stored in `cache`, which lives in the `application` domain"
    )


def test_a_session_arena_stored_in_an_application_static_is_rejected():
    assert "`ra` lives in the `session` domain" in only_error(
        ARENA
        + """
@lifetime(session)
let mut ra: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

@lifetime(application)
let mut cache: ptr<void> = null

function build() -> void {
    cache = arena_alloc(&ra, 64)
}
"""
    )


def test_the_arena_argument_may_be_written_without_the_address_of_operator():
    # `arena_alloc(fa, ...)` where `fa` is a static `ptr<Arena>` names the same
    # instance as `&fa` on a static `Arena`; both resolve to the arena's domain.
    assert "`fa` lives in the `frame` domain" in only_error(
        ARENA
        + """
@lifetime(frame)
let mut fa: ptr<Arena> = null

@lifetime(application)
let mut cache: ptr<void> = null

function build() -> void {
    cache = arena_alloc(fa, 64)
}
"""
    )


def test_frame_arena_stored_in_a_longer_lived_field_is_rejected():
    assert only_error(
        ARENA
        + """
struct Holder {
    @lifetime(session)
    view: ptr<void>
}

@lifetime(frame)
let mut fa: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

function build(h: ptr<Holder>) -> void {
    h[0].view = arena_alloc(&fa, 64)
}
"""
    ) == (
        "lifetime domain escape: `fa` lives in the `frame` domain but is "
        "stored in field `view`, which is declared to live in the `session` "
        "domain (a longer-lived domain may not hold a reference to a "
        "shorter-lived one) at line 28, column 5"
    )


# --- Negative: same-or-shorter-lived use, and unclear provenance ------------


def test_a_frame_arena_pointer_in_a_frame_local_is_allowed():
    assert domain_errors(
        ARENA
        + """
@lifetime(frame)
let mut fa: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

@lifetime(frame)
function build() -> void {
    let mut p: ptr<void> = null
    p = arena_alloc(&fa, 64)
}
"""
    ) == []


def test_an_application_arena_stored_in_an_application_static_is_allowed():
    assert domain_errors(
        ARENA
        + """
@lifetime(application)
let mut fa: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

@lifetime(application)
let mut cache: ptr<void> = null

function build() -> void {
    cache = arena_alloc(&fa, 64)
}
"""
    ) == []


def test_a_session_arena_stored_in_a_session_static_is_allowed():
    assert domain_errors(
        ARENA
        + """
@lifetime(session)
let mut ra: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

@lifetime(session)
let mut cache: ptr<void> = null

function build() -> void {
    cache = arena_alloc(&ra, 64)
}
"""
    ) == []


def test_an_unannotated_arena_defaults_to_application_and_never_escapes():
    # No `@lifetime` on the arena, so it defaults to `application`, the longest
    # domain. Storing its memory in an application static is not an escape.
    assert domain_errors(
        ARENA
        + """
let mut fa: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

@lifetime(application)
let mut cache: ptr<void> = null

function build() -> void {
    cache = arena_alloc(&fa, 64)
}
"""
    ) == []


def test_a_frame_arena_stored_in_a_shorter_field_is_allowed():
    # The field outlives nothing the frame arena needs to outlive.
    assert domain_errors(
        ARENA
        + """
struct Holder {
    @lifetime(callback)
    view: ptr<void>
}

@lifetime(frame)
let mut fa: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

function build(h: ptr<Holder>) -> void {
    h[0].view = arena_alloc(&fa, 64)
}
"""
    ) == []


def test_an_arena_reached_through_a_parameter_keeps_the_v0_behaviour():
    # The arena argument is a parameter rather than a named static, so its
    # domain is not statically clear here. The v0 checker still catches the
    # escape using the writing function's own frame domain.
    assert "`a` lives in the `frame` domain" in only_error(
        ARENA
        + """
@lifetime(application)
let mut cache: ptr<void> = null

@lifetime(frame)
function build(a: ptr<Arena>) -> void {
    cache = arena_alloc(a, 64)
}
"""
    )


def test_an_arena_parameter_in_an_unannotated_function_is_not_flagged():
    # Unclear provenance and no writer domain: allowed, no false positive.
    assert domain_errors(
        ARENA
        + """
@lifetime(application)
let mut cache: ptr<void> = null

function build(a: ptr<Arena>) -> void {
    cache = arena_alloc(a, 64)
}
"""
    ) == []


def test_bumping_and_resetting_a_frame_arena_locally_is_allowed():
    # A frame arena used and reset within its own domain, memory kept local, is
    # exactly the intended use and stays clean.
    assert domain_errors(
        ARENA
        + """
@lifetime(frame)
let mut fa: Arena = Arena { buffer: null, capacity: 0, offset: 0 }

@lifetime(frame)
function build() -> void {
    arena_reset(&fa)
    let mut p: ptr<void> = null
    p = arena_alloc(&fa, 64)
}
"""
    ) == []


def test_a_plain_heap_pointer_is_untouched_by_the_arena_rule():
    # malloc has no arena instance, so the arena rule never applies to it.
    assert domain_errors(
        """
extern {
    function malloc(size: i64) -> ptr<void>
}

@lifetime(application)
let mut cache: ptr<void> = null

@lifetime(session)
function build() -> void {
    cache = malloc(64)
}
"""
    ) == []
