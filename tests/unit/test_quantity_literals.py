"""Tests for quantity literal syntax: NUMBER UnitName desugars to NUMBER as UnitName."""
import os
import tempfile
import warnings
import pytest

from flow.parser import Lexer, Parser
from flow.type_checker import TypeChecker
from flow.transpiler import resolve_modules
from flow.c_generator import flow_to_c
from flow.monomorphize import monomorphize

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _errors(source: str):
    decls = Parser(Lexer(source), source=source).parse()
    checker = TypeChecker()
    checker.strict = True
    return checker.check(decls).errors


def _errors_with_imports(source: str):
    cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        with tempfile.NamedTemporaryFile(suffix=".flow", mode="w", delete=False) as f:
            f.write(source)
            path = f.name
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            decls = resolve_modules(path)
    finally:
        os.chdir(cwd)
        os.unlink(path)
    checker = TypeChecker()
    checker.strict = True
    return checker.check(decls).errors


def _to_c_with_imports(source: str) -> str:
    cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        with tempfile.NamedTemporaryFile(suffix=".flow", mode="w", delete=False) as f:
            f.write(source)
            path = f.name
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            decls = resolve_modules(path)
    finally:
        os.chdir(cwd)
        os.unlink(path)
    decls = monomorphize(decls)
    return flow_to_c(decls)


PRELUDE = """
unit Meter
unit Second
unit Hertz = Second^-1
unit Velocity = Meter / Second
unit Accel = Meter / Second^2
"""


def test_quantity_literal_basic():
    """3.14 Hertz desugars to 3.14 as Hertz."""
    assert not _errors(PRELUDE + """
    function main() -> i32 {
        let f: Hertz = 3.14 Hertz
        return 0
    }
    """)


def test_quantity_literal_multiple():
    assert not _errors(PRELUDE + """
    function main() -> i32 {
        let f: Hertz = 1.0e6 Hertz
        let d: Meter = 100.0 Meter
        let t: Second = 2.5 Second
        return 0
    }
    """)


def test_quantity_literal_integer():
    """Integer literals also work with quantity suffix."""
    assert not _errors(PRELUDE + """
    function main() -> i32 {
        let d: Meter = 42 Meter
        return 0
    }
    """)


def test_quantity_literal_invalid_unit():
    """Invalid unit name is rejected by the type checker."""
    errs = _errors(PRELUDE + """
    function main() -> i32 {
        let x = 3.14 NotAUnit
        return 0
    }
    """)
    assert any("NotAUnit" in e for e in errs), errs


def test_quantity_literal_same_as_cast():
    """3.14 Hertz and 3.14 as Hertz produce the same type."""
    assert not _errors(PRELUDE + """
    function main() -> i32 {
        let a: Hertz = 3.14 Hertz
        let b: Hertz = 3.14 as Hertz
        let c: Hertz = a + b
        return 0
    }
    """)


def test_quantity_literal_in_expression():
    """Quantity literals work inside larger expressions."""
    assert not _errors(PRELUDE + """
    function main() -> i32 {
        let v: Velocity = 100.0 Meter / 2.0 Second
        return 0
    }
    """)


def test_quantity_literal_doesnt_consume_lowercase():
    """Lowercase identifiers after numbers are NOT consumed as unit names.
    This avoids ambiguity with contextual keywords like 'step'.
    `42 foo` parses as two statements: `let x = 42` and `foo` (variable ref)."""
    from flow.parser import Variable, VarDecl, Literal
    decls = Parser(Lexer("""
    function main() -> i32 {
        let x = 42 foo
        return 0
    }
    """), source="test").parse()
    fn = decls[0]
    # First statement: let x = 42 (a VarDecl with a Literal initializer)
    assert isinstance(fn.body.statements[0], VarDecl)
    assert isinstance(fn.body.statements[0].initializer, Literal)
    # Second statement: foo (a Variable reference, not consumed as unit)
    assert isinstance(fn.body.statements[1], Variable)
    assert fn.body.statements[1].name == "foo"


def test_quantity_literal_with_imports():
    """Quantity literals work with units from imported modules."""
    assert not _errors_with_imports("""
    import "stdlib/units_si.flow"
    function main() -> i32 {
        let f: Hertz = 3.14e6 Hertz
        let d: Meter = 100.0 Meter
        let t: Second = 2.5 Second
        return 0
    }
    """)


def test_quantity_literal_c_codegen():
    """Verify the generated C has the cast."""
    c_code = _to_c_with_imports("""
    import "stdlib/units_si.flow"
    function main() -> i32 {
        let f: Hertz = 3.14e6 Hertz
        return 0
    }
    """)
    assert "Hertz" in c_code
    assert "3.14e6" in c_code


def test_quantity_literal_for_loop_step_unaffected():
    """`for i in 0 to 10 step 2` still works (step is lowercase)."""
    assert not _errors("""
    function main() -> i32 {
        let mut sum: i32 = 0
        for i in 0 to 10 step 2 {
            sum = sum + i
        }
        return sum
    }
    """)
