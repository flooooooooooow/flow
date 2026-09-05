"""Lifetime domains: callback / frame / session / application (issue #148).

`@lifetime(D)` on a function declares the domain its frame runs in;
`@lifetime(D)` on a module static declares the domain of that storage. The
type checker enforces four rules, each pinned here by its exact diagnostic
(docs/language/lifetime-domains.md):

  LD1  a longer-lived static may not be given a reference into a
       shorter-lived frame
  LD2  a domain function may not return a reference into its own frame
  LD3  `callback` composes with `@rt_safe`; `frame` forbids heap
       create/destroy but allows bumping an arena
  LD4  a domain may not call into a longer-lived one

Every escape the checker deliberately does *not* catch is pinned too, in
`TestKnownGaps`, so the gap is visible rather than assumed closed.
"""

from __future__ import annotations

import pytest

from flow.attributes import (
    LIFETIME_DOMAINS,
    attribute_errors,
    domain_rank,
    lifetime_domain,
)
from flow.parser import parse_flow_code

from .compiler_helpers import errors, to_c


MALLOC = """
extern {
    function malloc(size: i64) -> ptr<void>
    function calloc(nmemb: i64, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}
"""

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
    return [
        e for e in errors(source)
        if "lifetime domain" in e or "RT-safety violation" in e
    ]


def only_error(source: str) -> str:
    found = domain_errors(source)
    assert len(found) == 1, found
    return found[0]


# --- The domain order -------------------------------------------------------


def test_the_four_domains_are_ordered_shortest_lived_first():
    assert LIFETIME_DOMAINS == ("callback", "frame", "session", "application")
    assert domain_rank("callback") < domain_rank("frame")
    assert domain_rank("frame") < domain_rank("session")
    assert domain_rank("session") < domain_rank("application")


def test_an_unannotated_declaration_has_no_domain():
    assert lifetime_domain([]) is None
    assert lifetime_domain(["inline", "rt_safe"]) is None


def test_the_annotation_reads_back_its_domain():
    for d in LIFETIME_DOMAINS:
        assert lifetime_domain([f"lifetime({d})"]) == d


def test_an_unknown_domain_is_named_in_the_error():
    found = attribute_errors("f", ["lifetime(gpu_frame)"])
    assert found == [
        "Unknown lifetime domain 'gpu_frame' on 'f'. "
        "Known domains: callback, frame, session, application "
        "(see docs/language/lifetime-domains.md)"
    ]


def test_lifetime_requires_exactly_one_domain():
    found = attribute_errors("f", ["lifetime"])
    assert found == [
        "Attribute '@lifetime' on 'f' takes exactly one domain: "
        "callback, frame, session, application"
    ]
    found = attribute_errors("f", ["lifetime(frame,session)"])
    assert found and "takes exactly one domain" in found[0]


def test_two_lifetimes_on_one_declaration_are_rejected():
    found = attribute_errors("f", ["lifetime(frame)", "lifetime(session)"])
    assert found == [
        "'f' declares more than one '@lifetime' domain; "
        "a declaration lives in exactly one domain"
    ]


def test_the_annotation_parses_on_a_function_and_on_a_static():
    decls = parse_flow_code(
        """
@lifetime(application)
let mut cache: ptr<i32> = null

@lifetime(callback)
function process(n: i32) -> i32 { return n }
"""
    )
    assert [getattr(d, "attributes", None) for d in decls] == [
        ["lifetime(application)"],
        ["lifetime(callback)"],
    ]


def test_only_lifetime_is_allowed_on_a_module_static():
    found = [e for e in errors("@inline\nlet mut cache: ptr<i32> = null\n")
             if "module static" in e]
    assert found == [
        "Attribute '@inline' is not allowed on module static 'cache'; "
        "only '@lifetime(...)' is"
    ]


# --- LD1: escape into a longer-lived static ---------------------------------


def test_ld1_callback_span_stored_in_an_application_static():
    assert only_error(
        """
let mut tail: span<f32> = null

@lifetime(callback)
function process(input: span<f32>) -> void {
    let scratch: array<f32, 4> = [0.0, 0.0, 0.0, 0.0]
    tail = scratch[0..4]
}
"""
    ) == (
        "lifetime domain escape: `scratch` lives in the `callback` domain but "
        "is stored in `tail`, which lives in the `application` domain "
        "(a longer-lived domain may not hold a reference to a shorter-lived "
        "one) at line 7, column 5"
    )


def test_ld1_frame_pointer_stored_in_an_application_static():
    assert only_error(
        """
let mut cache: ptr<i32> = null

@lifetime(frame)
function build() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    cache = &scratch
}
"""
    ) == (
        "lifetime domain escape: `scratch` lives in the `frame` domain but is "
        "stored in `cache`, which lives in the `application` domain "
        "(a longer-lived domain may not hold a reference to a shorter-lived "
        "one) at line 7, column 5"
    )


def test_ld1_fires_through_a_span_local_that_borrows_the_array():
    assert "lives in the `callback` domain" in only_error(
        """
let mut tail: span<i32> = null

@lifetime(callback)
function process() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    let view: span<i32> = scratch[0..4]
    tail = view
}
"""
    )


def test_ld1_allows_a_static_whose_domain_does_not_outlive_the_writer():
    # The static is re-labelled `callback`, so it lives no longer than the
    # frame that writes it and the rule does not apply.
    assert domain_errors(
        """
@lifetime(callback)
let mut tail: span<f32> = null

@lifetime(callback)
function process() -> void {
    let scratch: array<f32, 4> = [0.0, 0.0, 0.0, 0.0]
    tail = scratch[0..4]
}
"""
    ) == []


def test_ld1_does_not_fire_for_a_pointer_that_is_not_local_storage():
    assert domain_errors(
        MALLOC
        + """
let mut cache: ptr<void> = null

@lifetime(session)
function build() -> void {
    let block: ptr<void> = malloc(64)
    cache = block
}
"""
    ) == []


def test_ld1_does_not_fire_in_an_unannotated_function():
    # Opt-in: without `@lifetime(...)` the domain rules say nothing. The
    # older span check still covers the span case on its own.
    assert domain_errors(
        """
let mut cache: ptr<i32> = null

function build() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    cache = &scratch
}
"""
    ) == []


def test_ld1_supersedes_the_span_diagnostic_for_the_same_assignment():
    # One mistake, one error.
    found = errors(
        """
let mut tail: span<f32> = null

@lifetime(callback)
function process() -> void {
    let scratch: array<f32, 4> = [0.0, 0.0, 0.0, 0.0]
    tail = scratch[0..4]
}
"""
    )
    assert [e for e in found if "span outlives borrowed storage" in e] == []
    assert len([e for e in found if "lifetime domain escape" in e]) == 1


def test_the_span_diagnostic_is_unchanged_without_an_annotation():
    found = errors(
        """
let mut tail: span<f32> = null

function process() -> void {
    let scratch: array<f32, 4> = [0.0, 0.0, 0.0, 0.0]
    tail = scratch[0..4]
}
"""
    )
    assert [e for e in found if "span outlives borrowed storage" in e] == [
        "span outlives borrowed storage `scratch` at line 6, column 5"
    ]


# --- LD2: escape by return --------------------------------------------------


def test_ld2_returning_a_pointer_into_the_frame():
    assert only_error(
        """
@lifetime(frame)
function build() -> ptr<i32> {
    let scratch: array<i32, 8> = [0, 0, 0, 0, 0, 0, 0, 0]
    return scratch
}
"""
    ) == (
        "lifetime domain escape: `scratch` lives in the `frame` domain but is "
        "returned from 'build', which outlives it (a returned reference may "
        "not point into the frame that produced it) at line 5, column 5"
    )


def test_ld2_returning_a_span_into_the_frame():
    assert "lives in the `callback` domain" in only_error(
        """
@lifetime(callback)
function view() -> span<i32> {
    let scratch: array<i32, 3> = [1, 2, 3]
    return scratch[0..3]
}
"""
    )


def test_ld2_supersedes_the_span_diagnostic_for_the_same_return():
    found = errors(
        """
@lifetime(callback)
function view() -> span<i32> {
    let scratch: array<i32, 3> = [1, 2, 3]
    return scratch[0..3]
}
"""
    )
    assert [e for e in found if "span outlives borrowed storage" in e] == []


def test_ld2_allows_returning_a_view_of_a_parameter():
    assert domain_errors(
        """
@lifetime(callback)
function head(values: span<i32>) -> span<i32> {
    return values[0..2]
}
"""
    ) == []


def test_ld2_allows_returning_a_plain_value():
    assert domain_errors(
        """
@lifetime(callback)
function peak(values: span<f32>) -> f32 {
    let mut acc: f32 = 0.0
    let mut i: i64 = 0
    while i < values.len {
        acc = acc + values[i]
        i = i + 1
    }
    return acc
}
"""
    ) == []


# --- LD3: allocation discipline ---------------------------------------------


def test_ld3_callback_rejects_malloc_and_names_the_domain():
    assert only_error(
        MALLOC
        + """
@lifetime(callback)
function process(n: i32) -> i32 {
    let p: ptr<void> = malloc(64)
    return n
}
"""
    ) == (
        "RT-safety violation: 'process' is in the `callback` lifetime domain, "
        "which forbids allocation, but calls 'malloc', which is forbidden on "
        "an RT-safe path (heap, device/file I/O, GPU, or blocking lock; see "
        "docs/language/lifetime-domains.md)"
    )


def test_ld3_callback_rejects_a_transitive_allocation():
    assert only_error(
        MALLOC
        + """
function helper(n: i64) -> ptr<void> {
    return malloc(n)
}

@lifetime(callback)
function process(n: i32) -> i32 {
    let p: ptr<void> = helper(64)
    return n
}
"""
    ) == (
        "RT-safety violation: 'process' is in the `callback` lifetime domain, "
        "which forbids allocation, but calls 'helper', which is not RT-safe "
        "because it calls 'malloc' (forbidden on an RT-safe path; see "
        "docs/language/lifetime-domains.md)"
    )


def test_ld3_callback_rejects_a_blocking_lock():
    assert "which is forbidden on an RT-safe path" in only_error(
        """
extern {
    function mutex_lock(m: ptr<void>) -> i32
}

@lifetime(callback)
function process(m: ptr<void>, n: i32) -> i32 {
    let r: i32 = mutex_lock(m)
    return n
}
"""
    )


def test_ld3_callback_allows_bumping_an_existing_arena():
    assert domain_errors(
        ARENA
        + """
@lifetime(callback)
function process(a: ptr<Arena>, n: i32) -> i32 {
    let p: ptr<void> = arena_alloc(a, 64)
    return n
}
"""
    ) == []


def test_ld3_frame_rejects_malloc_and_points_at_the_arena():
    assert only_error(
        MALLOC
        + """
@lifetime(frame)
function build_scene(n: i32) -> i32 {
    let p: ptr<void> = malloc(64)
    return n
}
"""
    ) == (
        "lifetime domain violation: 'build_scene' is in the `frame` domain "
        "but calls 'malloc', which allocates or frees heap memory. "
        "Frame-domain code allocates by bumping a frame arena "
        "(frame_alloc_*); see docs/language/lifetime-domains.md"
    )


def test_ld3_frame_rejects_a_transitive_allocation():
    assert only_error(
        MALLOC
        + """
function make_buffer(n: i64) -> ptr<void> {
    return calloc(n, 4)
}

@lifetime(frame)
function build_scene(n: i32) -> i32 {
    let p: ptr<void> = make_buffer(64)
    return n
}
"""
    ) == (
        "lifetime domain violation: 'build_scene' is in the `frame` domain "
        "but calls 'make_buffer', which allocates or frees heap memory "
        "because it calls 'calloc'. Frame-domain code allocates by bumping a "
        "frame arena (frame_alloc_*); see docs/language/lifetime-domains.md"
    )


def test_ld3_frame_allows_a_lock_that_callback_forbids():
    # A frame loop is allowed to block; a callback is not. This is the one
    # place the two domains' allocation rules differ.
    src = """
extern {
    function mutex_lock(m: ptr<void>) -> i32
}

@lifetime(%s)
function step(m: ptr<void>, n: i32) -> i32 {
    let r: i32 = mutex_lock(m)
    return n
}
"""
    assert domain_errors(src % "frame") == []
    assert len(domain_errors(src % "callback")) == 1


def test_ld3_frame_allows_bumping_and_resetting_an_arena():
    assert domain_errors(
        ARENA
        + """
@lifetime(frame)
function build(a: ptr<Arena>, n: i32) -> i32 {
    arena_reset(a)
    let p: ptr<void> = arena_alloc(a, 64)
    return n
}
"""
    ) == []


def test_ld3_session_and_application_may_allocate():
    for domain in ("session", "application"):
        assert domain_errors(
            MALLOC
            + f"""
@lifetime({domain})
function setup(n: i32) -> i32 {{
    let p: ptr<void> = malloc(64)
    free(p)
    return n
}}
"""
        ) == [], domain


def test_rt_safe_keeps_its_own_wording():
    # The `@rt_safe` diagnostic is unchanged for code that does not use
    # domains at all.
    assert only_error(
        MALLOC
        + """
@rt_safe
function process(n: i32) -> i32 {
    let p: ptr<void> = malloc(64)
    return n
}
"""
    ) == (
        "RT-safety violation: 'process' is marked '@rt_safe' but calls "
        "'malloc', which is forbidden on an RT-safe path (heap, device/file "
        "I/O, GPU, or blocking lock; see docs/library/rt-safety.md)"
    )


def test_rt_safe_and_lifetime_callback_may_be_written_together():
    found = domain_errors(
        MALLOC
        + """
@rt_safe
@lifetime(callback)
function process(n: i32) -> i32 {
    let p: ptr<void> = malloc(64)
    return n
}
"""
    )
    assert len(found) == 1, found
    assert "is marked '@rt_safe'" in found[0]


# --- LD4: call ordering -----------------------------------------------------


def test_ld4_callback_may_not_call_session():
    assert only_error(
        """
@lifetime(session)
function reload_preset(id: i32) -> i32 { return id }

@lifetime(callback)
function process(n: i32) -> i32 {
    return reload_preset(n)
}
"""
    ) == (
        "lifetime domain violation: 'process' is in the `callback` domain but "
        "calls 'reload_preset', which is in the `session` domain "
        "(a shorter-lived domain may not call into a longer-lived one; see "
        "docs/language/lifetime-domains.md)"
    )


def test_ld4_frame_may_not_call_application():
    assert "is in the `application` domain" in only_error(
        """
@lifetime(application)
function install_hook(n: i32) -> i32 { return n }

@lifetime(frame)
function step(n: i32) -> i32 {
    return install_hook(n)
}
"""
    )


def test_ld4_allows_calling_into_a_shorter_or_equal_domain():
    assert domain_errors(
        """
@lifetime(callback)
function process(n: i32) -> i32 { return n }

@lifetime(callback)
function sibling(n: i32) -> i32 { return process(n) }

@lifetime(session)
function run(n: i32) -> i32 { return process(n) }
"""
    ) == []


def test_ld4_stays_quiet_when_either_side_is_unannotated():
    assert domain_errors(
        """
function helper(n: i32) -> i32 { return n }

@lifetime(callback)
function process(n: i32) -> i32 { return helper(n) }
"""
    ) == []
    assert domain_errors(
        """
@lifetime(session)
function setup(n: i32) -> i32 { return n }

function caller(n: i32) -> i32 { return setup(n) }
"""
    ) == []


# --- Known gaps, pinned so they stay visible --------------------------------


class TestKnownGaps:
    """Escapes the checker deliberately does not catch.

    Each of these compiles clean today. They are listed in
    docs/language/lifetime-domains.md under "What the compiler does not
    check". If one of these starts failing, the gap closed and the doc
    should say so.
    """

    def test_escape_through_a_call_is_not_caught(self):
        assert domain_errors(
            """
let mut cache: ptr<i32> = null

function stash(p: ptr<i32>) -> void {
    cache = p
}

@lifetime(callback)
function process() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    stash(&scratch)
}
"""
        ) == []

    def test_escape_through_a_struct_field_is_not_caught(self):
        assert domain_errors(
            """
struct Holder {
    view: ptr<i32>
}

let mut holder: Holder = Holder { view: null }

@lifetime(callback)
function process() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    holder.view = &scratch
}
"""
        ) == []

    def test_the_domain_of_arena_memory_is_modelled(self):
        assert only_error(
            ARENA
            + """
let mut cache: ptr<void> = null

@lifetime(frame)
function build(a: ptr<Arena>) -> void {
    cache = arena_alloc(a, 64)
}
"""
        ).startswith(
            "lifetime domain escape: `a` lives in the `frame` domain but is stored in `cache`, "
            "which lives in the `application` domain (a longer-lived domain may not hold a "
            "reference to a shorter-lived one)"
        )

    def test_the_domain_of_arena_memory_is_accepted_within_its_lifetime(self):
        assert domain_errors(
            ARENA
            + """
@lifetime(frame)
function build(a: ptr<Arena>) -> void {
    let mut local_cache: ptr<void> = null
    local_cache = arena_alloc(a, 64)
}
"""
        ) == []


# --- Codegen and execution --------------------------------------------------


ACCEPTED_PROGRAM = """
extern {
    function printf(fmt: string, v: i32) -> i32
}

@lifetime(application)
let mut total: i32 = 0

@lifetime(callback)
function process(values: span<i32>) -> i32 {
    let mut acc: i32 = 0
    let mut i: i64 = 0
    while i < values.len {
        acc = acc + values[i]
        i = i + 1
    }
    return acc
}

@lifetime(session)
function run() -> i32 {
    let block: array<i32, 4> = [1, 2, 3, 4]
    total = process(block)
    return total
}

function main() -> i32 {
    let got: i32 = run()
    if got != 10 {
        return 1
    }
    return 0
}
"""


def test_the_annotation_leaves_no_trace_in_the_generated_c():
    c = to_c(ACCEPTED_PROGRAM)
    assert "lifetime" not in c
    assert "callback" not in c
    assert "session" not in c


def test_an_accepted_domain_program_type_checks_clean():
    assert errors(ACCEPTED_PROGRAM) == []


# test_an_accepted_domain_program_runs compiled and ran ACCEPTED_PROGRAM.
# tests/lang/test_lifetime_domains.flow runs a larger version of the same
# shape: an application static written from a session function, a callback
# reading a span, a frame function bumping and resetting an arena, and a
# callback returning a view of its parameter.


@pytest.mark.parametrize("domain", LIFETIME_DOMAINS)
def test_every_domain_compiles_to_the_same_c(domain):
    body = """
function step(n: i32) -> i32 {
    return n + 1
}
"""
    annotated = f"@lifetime({domain})\n" + body.lstrip()
    assert to_c(annotated) == to_c(body)
