"""Effect-row Phase 1 + 2 + first-class fn types under check_effect_rows."""

from flow.parser import FunctionDecl, VarDecl, parse_flow_code
from flow.type_checker import TypeChecker


PRELUDE = """
effect Log {
    info(msg: string) -> void,
}

capability Console {
    effect Log,
    function info(msg: string) -> void {
        printf("%s\\n", msg)
    },
}
"""


def check(code: str, *, rows: bool = True):
    checker = TypeChecker()
    checker.strict = True
    checker.check_effect_rows = rows
    return checker.check(parse_flow_code(code)).errors


def test_unhandled_effect_errors_when_rows_enabled():
    errors = check(
        PRELUDE
        + """
function main() -> i32 {
    Log.info("oops")
    return 0
}
"""
    )
    assert any("Unhandled effect 'Log.info'" in e for e in errors), errors


def test_handled_effect_ok():
    errors = check(
        PRELUDE
        + """
function main() -> i32 {
    handle Log with Console {
        Log.info("ok")
    }
    return 0
}
"""
    )
    assert not any("Unhandled effect" in e for e in errors), errors


def test_rows_disabled_allows_unhandled():
    errors = check(
        PRELUDE
        + """
function main() -> i32 {
    Log.info("soft default")
    return 0
}
""",
        rows=False,
    )
    assert not any("Unhandled effect" in e for e in errors), errors


def test_nested_handle_restores_outer():
    errors = check(
        PRELUDE
        + """
capability Quiet {
    effect Log,
    function info(msg: string) -> void { },
}

function main() -> i32 {
    handle Log with Console {
        handle Log with Quiet {
            Log.info("quiet")
        }
        Log.info("loud again")
    }
    return 0
}
"""
    )
    assert not any("Unhandled effect" in e for e in errors), errors


def test_declared_row_allows_body_perform():
    errors = check(
        PRELUDE
        + """
function greet() -> void with Log {
    Log.info("hi")
}

function main() -> i32 {
    handle Log with Console {
        greet()
    }
    return 0
}
"""
    )
    assert not any("Unhandled effect" in e for e in errors), errors
    assert not any("requires effect" in e for e in errors), errors


def test_caller_must_cover_callee_row():
    errors = check(
        PRELUDE
        + """
function greet() -> void with Log {
    Log.info("hi")
}

function main() -> i32 {
    greet()
    return 0
}
"""
    )
    assert any("requires effect" in e and "Log" in e for e in errors), errors


def test_caller_with_row_covers_callee():
    errors = check(
        PRELUDE
        + """
function greet() -> void with Log {
    Log.info("hi")
}

function outer() -> void with Log {
    greet()
}

function main() -> i32 {
    handle Log with Console {
        outer()
    }
    return 0
}
"""
    )
    assert not any("requires effect" in e for e in errors), errors
    assert not any("Unhandled effect" in e for e in errors), errors


def test_parse_with_clause():
    decls = parse_flow_code(
        PRELUDE
        + """
function f() -> i32 with Log {
    return 0
}
"""
    )
    funcs = [d for d in decls if getattr(d, "name", None) == "f"]
    assert len(funcs) == 1
    assert funcs[0].effects == ["Log"]


def test_first_class_fn_type_with_effects():
    """`(T) -> R with E` annotation; calling the value requires E."""
    decls = parse_flow_code(
        PRELUDE
        + """
function main() -> i32 {
    let f: (string) -> void with Log = |msg: string| -> void { return }
    return 0
}
"""
    )
    main = next(d for d in decls if getattr(d, "name", None) == "main")
    assert isinstance(main, FunctionDecl)
    var = next(
        s for s in main.body.statements if isinstance(s, VarDecl) and s.name == "f"
    )
    assert var.type.effects == ["Log"]

    errors = check(
        PRELUDE
        + """
function main() -> i32 {
    let f: (string) -> void with Log = |msg: string| -> void { return }
    f("x")
    return 0
}
"""
    )
    assert any("requires effect" in e and "Log" in e for e in errors), errors

    errors_ok = check(
        PRELUDE
        + """
function main() -> i32 {
    let f: (string) -> void with Log = |msg: string| -> void { return }
    handle Log with Console {
        f("x")
    }
    return 0
}
"""
    )
    assert not any("requires effect" in e for e in errors_ok), errors_ok
