"""A capability name used as a value is reported in Flow terms (#561).

The parser accepts `capability E` in a parameter position and the generator
lowers a call through it, but nothing defines a C symbol for the capability,
so passing one used to surface as a clang error naming an identifier the
author never wrote.
"""

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


SOURCE = """
effect Counter {
    next(current: i32) -> i32,
}

capability UnitCounter {
    effect Counter,
    function next(current: i32) -> i32 { return current + 1 },
}

function run(c: capability Counter) -> i32 {
    return Counter.next(41)
}

function main() -> i32 {
    let got: i32 = run(UnitCounter)
    return got
}
"""


def check(source: str, *, strict: bool = True):
    checker = TypeChecker()
    checker.strict = strict
    return checker.check(parse_flow_code(source))


def test_passing_a_capability_names_the_construct():
    result = check(SOURCE)
    assert any("Capability 'UnitCounter' is not a value" in e for e in result.errors)
    assert not any(e == "Undefined variable 'UnitCounter'" for e in result.errors)


def test_the_message_points_at_handle():
    (message,) = [e for e in check(SOURCE).errors if "UnitCounter" in e and "value" in e]
    assert "handle <Effect> with UnitCounter" in message


def test_lenient_does_not_downgrade_it():
    """Compiling anyway would emit C that cannot build, so this stays fatal."""
    result = check(SOURCE, strict=False)
    assert any("is not a value" in e for e in result.fatal_errors)


def test_an_ordinary_undefined_name_is_unaffected():
    result = check("function main() -> i32 { return nope }")
    assert any(e == "Undefined variable 'nope'" for e in result.errors)
    assert result.fatal_errors == []


def test_capability_parameters_still_type_check():
    """The declaration form is supported; only using the name as a value is not."""
    result = check("""
effect Counter {
    next(current: i32) -> i32,
}

capability UnitCounter {
    effect Counter,
    function next(current: i32) -> i32 { return current + 1 },
}

function run(c: capability Counter) -> i32 {
    return Counter.next(41)
}

function main() -> i32 {
    handle Counter with UnitCounter {
        return run_it()
    }
}

function run_it() -> i32 {
    return Counter.next(41)
}
""")
    assert result.fatal_errors == []
