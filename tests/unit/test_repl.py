"""
Unit tests for FlowREPL in src/flow/repl.py.
"""

from flow.repl import FlowREPL


def test_add_function_error_path(capsys):
    """Test that add_function catches exceptions on invalid input and pops the function."""
    repl = FlowREPL()
    # Invalid syntax that will fail Lexer/Parser parsing
    invalid_func = "function bad_fn("

    repl.add_function(invalid_func)

    # Assert that the invalid function was popped from functions list
    assert len(repl.functions) == 0

    # Check that error message was printed
    captured = capsys.readouterr()
    assert "Error parsing function" in captured.out


def test_add_function_success_path(capsys):
    """Test that add_function correctly parses and retains valid function definitions."""
    repl = FlowREPL()
    valid_func = "function add(a: i32, b: i32) -> i32 { return a + b }"

    repl.add_function(valid_func)

    assert len(repl.functions) == 1
    assert repl.functions[0] == valid_func

    captured = capsys.readouterr()
    assert "Defined function add(a: i32, b: i32) -> i32" in captured.out


def test_add_struct_error_path(capsys):
    """Test that add_struct catches exceptions on invalid input and pops the struct."""
    repl = FlowREPL()
    invalid_struct = "struct BadStruct {"

    repl.add_struct(invalid_struct)

    assert len(repl.structs) == 0

    captured = capsys.readouterr()
    assert "Error parsing struct" in captured.out


def test_add_struct_success_path(capsys):
    """Test that add_struct correctly parses and retains valid struct definitions."""
    repl = FlowREPL()
    valid_struct = "struct Point { x: i32, y: i32 }"

    repl.add_struct(valid_struct)

    assert len(repl.structs) == 1
    assert repl.structs[0] == valid_struct

    captured = capsys.readouterr()
    assert "Defined struct Point { x: i32, y: i32 }" in captured.out
