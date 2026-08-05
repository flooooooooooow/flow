"""Module-level mutable state (module statics).

Top-level `let mut name: Type = init` declares a file-scope C `static` that
functions in the same module read and write like a normal variable. Allowed
types: primitives, fixed arrays of primitives, and ptr<T> initialized to null.
Initializers must be compile-time constants.
"""

import pytest

from flow.parser import parse_flow_code, StaticDecl
from flow.mlir_generator import flow_to_mlir

from .compiler_helpers import errors, to_c, typecheck, compile_and_run, needs_clang


COUNTER_MODULE = """
let mut counter: i32 = 0

function bump() -> i32 {
    counter = counter + 1
    return counter
}

function main() -> i32 {
    bump()
    bump()
    return bump()
}
"""


class TestParseAndTypecheck:
    def test_static_counter_parses_and_typechecks(self):
        decls = parse_flow_code(COUNTER_MODULE)
        statics = [d for d in decls if isinstance(d, StaticDecl)]
        assert len(statics) == 1
        assert statics[0].name == "counter"
        assert statics[0].type.name == "i32"
        assert typecheck(COUNTER_MODULE).errors == []

    def test_reassignment_from_function_allowed_in_strict(self):
        # Module statics are mutable module-scope symbols: assigning to one
        # from a function body is legal even in strict mode.
        assert errors(COUNTER_MODULE, strict=True) == []

    def test_top_level_immutable_let_is_a_syntax_error(self):
        with pytest.raises(SyntaxError, match="let mut"):
            parse_flow_code("let x: i32 = 1")

    def test_static_requires_type_annotation(self):
        with pytest.raises(SyntaxError, match="type annotation"):
            parse_flow_code("let mut x = 1")

    def test_non_constant_initializer_rejected(self):
        errs = errors(
            """
            function f() -> i32 { return 1 }
            let mut x: i32 = f()
            """
        )
        assert any("compile-time constant" in e for e in errs)

    def test_struct_typed_static_rejected(self):
        errs = errors(
            """
            struct Point { x: f32, y: f32 }
            let mut p: Point = Point { x: 1.0, y: 2.0 }
            """
        )
        assert any(
            "unsupported type 'Point'" in e and "module statics" in e for e in errs
        )

    def test_array_static_with_wrong_length_rejected(self):
        errs = errors("let mut a: array<i32, 3> = [1, 2]")
        assert any("2 elements" in e and "declares 3" in e for e in errs)

    def test_pointer_static_must_start_null(self):
        errs = errors(
            """
            function f() -> ptr<i32> { return null }
            let mut p: ptr<i32> = f()
            """
        )
        assert any("initialized to null" in e for e in errs)


class TestCodegen:
    def test_counter_lowers_to_c_static(self):
        c = to_c(COUNTER_MODULE)
        assert "static int32_t counter = 0;" in c

    def test_static_is_file_scope_static_even_outside_library_mode(self):
        c = to_c(COUNTER_MODULE, library=False)
        assert "static int32_t counter" in c

    def test_array_static_lowers_with_brace_initializer(self):
        c = to_c("let mut table: array<i32, 4> = [1, 2, 3, 4]")
        assert "static int32_t table[4] = { 1, 2, 3, 4 };" in c

    def test_all_zero_array_static_uses_zero_fill_shorthand(self):
        c = to_c(
            "let mut zeros: array<f32, 8> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"
        )
        assert "static float zeros[8] = {0};" in c

    def test_null_pointer_static_lowers_to_null(self):
        c = to_c("let mut head: ptr<i32> = null")
        assert "static int32_t* head = NULL;" in c


class TestMlirBackend:
    def test_mlir_backend_rejects_statics_loudly(self):
        decls = parse_flow_code(COUNTER_MODULE)
        with pytest.raises(NotImplementedError, match="module statics not yet supported"):
            flow_to_mlir(decls)


@needs_clang
class TestCompileAndRun:
    def test_counter_bumped_three_times_exits_with_3(self):
        assert compile_and_run(COUNTER_MODULE) == 3

    def test_array_static_read_write_across_functions(self):
        source = """
        let mut cells: array<i32, 4> = [0, 0, 0, 0]

        function poke(i: i32, v: i32) -> void {
            cells[i] = v
        }

        function main() -> i32 {
            poke(0, 1)
            poke(3, 2)
            return cells[0] + cells[3]
        }
        """
        assert compile_and_run(source) == 3
