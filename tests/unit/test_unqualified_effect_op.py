"""An unqualified effect operation is rejected in Flow, not at link time.

Calling `mark(...)` instead of `Bench.mark(...)` inside a handler scope used
to pass type checking, become an undeclared call in the generated C, and fail
as an undefined `_mark` symbol at link. The diagnostic named a backend
artifact rather than the operation the user wrote. See issue #614.
"""

from __future__ import annotations

from tests.unit.compiler_helpers import errors

PRELUDE = """
effect Bench {
    mark(label: string, seconds: f64) -> void,
}

capability Timer {
    effect Bench,
    function mark(label: string, seconds: f64) -> void { },
}
"""

DIAGNOSTIC = "effect operation 'mark' must be called as 'Bench.mark'"


def test_an_unqualified_operation_names_the_qualified_spelling():
    source = PRELUDE + """
function main() -> i32 {
    handle Bench with Timer {
        mark("stage", 0.125)
    }
    return 0
}
"""
    assert any(DIAGNOSTIC in e for e in errors(source)), errors(source)


def test_an_ordinary_function_of_the_same_name_still_wins():
    """The check must not shadow a real function that happens to share a name."""
    source = PRELUDE + """
function mark(label: string, seconds: f64) -> void { }

function main() -> i32 {
    handle Bench with Timer {
        mark("stage", 0.125)
    }
    return 0
}
"""
    assert errors(source) == []


def test_the_qualified_spelling_is_accepted():
    source = PRELUDE + """
function main() -> i32 {
    handle Bench with Timer {
        Bench.mark("stage", 0.125)
    }
    return 0
}
"""
    assert errors(source) == []
