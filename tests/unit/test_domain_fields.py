"""Lifetime domains through struct fields and collections (issue #684).

The v0 domain checker (tests/unit/test_lifetime_domains.py) tracks direct
locals and module statics. This file pins the extension to composite storage:

  * a reference stored into a field or element of a module static is an escape,
    however deep the field path or container nesting goes. The static's domain
    is the struct's domain, reached through `_borrow_root_name`.
  * a struct field may declare its own domain with `@lifetime(D)`. That is a
    contract on the storage the field may point to, so storing a shorter-lived
    reference into it is an escape wherever the instance itself lives (LD5).

The rule only fires on code that opts in on both sides: the writing function
declares a domain and the target field's domain outlives it, with the value
rooted in the writing frame's own storage. Ambiguous stores are allowed, the
same way the v0 checker allows them, so the extension adds no false positives.
"""

from __future__ import annotations

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker

from .compiler_helpers import to_c


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


# --- Static-rooted composite storage ----------------------------------------
# The struct/container lives in a static, so its domain is the static's
# (application by default). A shorter-lived reference stored anywhere inside it
# is an escape.


def test_reference_into_a_static_struct_field_is_rejected():
    assert only_error(
        """
struct Holder { view: ptr<i32> }

let mut holder: Holder = Holder { view: null }

@lifetime(callback)
function process() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    holder.view = &scratch
}
"""
    ) == (
        "lifetime domain escape: `scratch` lives in the `callback` domain but "
        "is stored in `holder`, which lives in the `application` domain "
        "(a longer-lived domain may not hold a reference to a shorter-lived "
        "one) at line 9, column 5"
    )


def test_reference_into_a_nested_static_struct_field_is_rejected():
    assert "lives in the `callback` domain" in only_error(
        """
struct Inner { view: ptr<i32> }
struct Outer { inner: Inner }

let mut holder: Outer = Outer { inner: Inner { view: null } }

@lifetime(callback)
function process() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    holder.inner.view = &scratch
}
"""
    )


def test_reference_into_a_static_array_element_is_rejected():
    assert "is stored in `table`" in only_error(
        """
let mut table: array<ptr<i32>, 4> = [null, null, null, null]

@lifetime(callback)
function process() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    table[0] = &scratch
}
"""
    )


def test_reference_into_a_static_structs_array_field_is_rejected():
    assert "is stored in `holder`" in only_error(
        """
struct Holder { items: array<ptr<i32>, 4> }

let mut holder: Holder = Holder { items: [null, null, null, null] }

@lifetime(callback)
function process() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    holder.items[0] = &scratch
}
"""
    )


def test_a_local_struct_field_store_is_not_an_escape():
    # A plain (unannotated) local struct lives for the frame, exactly as long
    # as the reference it receives. No escape, no diagnostic.
    assert domain_errors(
        """
struct Holder { view: ptr<i32> }

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
"""
    ) == []


# --- LD5: a field that declares its own longer-lived domain ------------------


def test_ld5_shorter_lived_reference_into_a_longer_lived_field():
    assert only_error(
        """
struct Holder {
    @lifetime(application)
    view: ptr<i32>
}

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
"""
    ) == (
        "lifetime domain escape: `scratch` lives in the `callback` domain but "
        "is stored in field `view`, which is declared to live in the "
        "`application` domain (a longer-lived domain may not hold a reference "
        "to a shorter-lived one) at line 11, column 5"
    )


def test_ld5_fires_through_a_pointer_to_the_struct():
    assert "is declared to live in the `session` domain" in only_error(
        """
struct Holder {
    @lifetime(session)
    view: ptr<i32>
}

@lifetime(callback)
function process(h: ptr<Holder>) -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h[0].view = &scratch
}
"""
    )


def test_ld5_fires_through_a_span_local_that_borrows_the_array():
    assert "lives in the `callback` domain" in only_error(
        """
struct Holder {
    @lifetime(application)
    tail: span<i32>
}

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { tail: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    let view: span<i32> = scratch[0..4]
    h.tail = view
}
"""
    )


def test_ld5_frame_reference_into_a_session_field():
    assert "lives in the `frame` domain" in only_error(
        """
struct Holder {
    @lifetime(session)
    view: ptr<i32>
}

@lifetime(frame)
function build() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
"""
    )


# --- LD5 negatives: no false positives --------------------------------------


def test_ld5_allows_a_same_domain_field():
    assert domain_errors(
        """
struct Holder {
    @lifetime(callback)
    view: ptr<i32>
}

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
"""
    ) == []


def test_ld5_allows_a_field_that_does_not_outlive_the_writer():
    # The field is `frame`; the writer is `session`, which is longer-lived.
    # Storing a session-frame reference into a frame field is not an escape.
    assert domain_errors(
        """
struct Holder {
    @lifetime(frame)
    view: ptr<i32>
}

@lifetime(session)
function build() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
"""
    ) == []


def test_ld5_stays_quiet_on_an_unannotated_field():
    assert domain_errors(
        """
struct Holder { view: ptr<i32> }

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
"""
    ) == []


def test_ld5_stays_quiet_in_an_unannotated_function():
    assert domain_errors(
        """
struct Holder {
    @lifetime(application)
    view: ptr<i32>
}

function process() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
"""
    ) == []


def test_ld5_allows_storing_a_longer_lived_reference():
    # `&g` is a reference into a module static (application). Storing it into an
    # application-domain field is fine; the value is not rooted in the frame.
    assert domain_errors(
        """
struct Holder {
    @lifetime(application)
    view: ptr<i32>
}

let mut g: i32 = 0

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { view: null }
    h.view = &g
}
"""
    ) == []


def test_ld5_allows_a_plain_value_field():
    # A non-reference field cannot carry a borrow, so no escape is possible.
    assert domain_errors(
        """
struct Holder {
    @lifetime(application)
    count: i32
}

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { count: 0 }
    h.count = 7
}
"""
    ) == []


# --- Codegen: the annotation leaves no trace --------------------------------


def test_a_field_annotation_leaves_no_trace_in_the_generated_c():
    c = to_c(
        """
struct Holder {
    @lifetime(application)
    view: ptr<i32>
}

function main() -> i32 {
    let mut h: Holder = Holder { view: null }
    return 0
}
"""
    )
    assert "lifetime" not in c
    assert "application" not in c
