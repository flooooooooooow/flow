import io
import pytest
from unittest.mock import patch, MagicMock
from flow.repl import FlowREPL, main


def test_repl_init():
    repl = FlowREPL()
    assert repl.variables == {}
    assert repl.var_values == {}
    assert repl.functions == []
    assert repl.structs == []
    assert repl.history == []


def test_process_input_exception_handling(capsys):
    """Test process_input catches exceptions and prints formatted error message (line 183)."""
    repl = FlowREPL()

    with patch("flow.repl.Lexer", side_effect=RuntimeError("Lexer failure")):
        repl.process_input("1 + 1")

    captured = capsys.readouterr()
    assert "Error: Lexer failure" in captured.out


def test_add_function_success_and_error(capsys):
    repl = FlowREPL()

    # Successful function addition
    repl.add_function("function add(a: i32, b: i32) -> i32 { return a + b }")
    assert len(repl.functions) == 1
    captured = capsys.readouterr()
    assert "Defined function add" in captured.out

    # Invalid function syntax (it gets popped on error)
    repl.add_function("function invalid(")
    assert len(repl.functions) == 1  # only the first valid function remains
    captured = capsys.readouterr()
    assert "Error parsing function:" in captured.out


def test_add_struct_success_and_error(capsys):
    repl = FlowREPL()

    # Successful struct addition
    repl.add_struct("struct Point { x: i32, y: i32 }")
    assert len(repl.structs) == 1
    captured = capsys.readouterr()
    assert "Defined struct Point" in captured.out

    # Invalid struct syntax (it gets popped on error)
    repl.add_struct("struct Invalid {")
    assert len(repl.structs) == 1  # only the first valid struct remains
    captured = capsys.readouterr()
    assert "Error parsing struct:" in captured.out


def test_add_variable(capsys):
    repl = FlowREPL()

    # Variable declaration without '=' initializer
    repl.add_variable("let x")
    captured = capsys.readouterr()
    assert "Variable declaration needs an initializer" in captured.out

    # Variable declaration with type annotation and expression evaluation mock
    with patch.object(repl, "compile_and_run_expr", return_value=42):
        repl.add_variable("let x: i32 = 40 + 2")
        assert repl.variables["x"] == "i32"
        assert repl.var_values["x"] == 42
        captured = capsys.readouterr()
        assert "x" in captured.out and "= 42" in captured.out

    # Variable declaration without explicit type (inferred auto)
    with patch.object(repl, "compile_and_run_expr", return_value=10):
        repl.add_variable("let y = 10")
        assert repl.variables["y"] == "auto"
        assert repl.var_values["y"] == 10

    # Variable declaration raising exception during evaluation
    with patch.object(repl, "compile_and_run_expr", side_effect=ValueError("Evaluation failed")):
        repl.add_variable("let z = 1 / 0")
        captured = capsys.readouterr()
        assert "Error: Evaluation failed" in captured.out


def test_handle_commands(capsys):
    repl = FlowREPL()

    # Quit commands raise EOFError
    for cmd in [":quit", ":q", ":exit"]:
        with pytest.raises(EOFError):
            repl.handle_command(cmd)

    # Help command
    repl.handle_command(":help")
    captured = capsys.readouterr()
    assert "REPL Commands:" in captured.out

    # Vars command empty and non-empty
    repl.handle_command(":vars")
    captured = capsys.readouterr()
    assert "No variables defined" in captured.out

    repl.variables["x"] = "i32"
    repl.var_values["x"] = 100
    repl.handle_command(":vars")
    captured = capsys.readouterr()
    assert "x" in captured.out and "i32 = 100" in captured.out

    # Funcs command empty and non-empty
    repl.handle_command(":funcs")
    captured = capsys.readouterr()
    assert "No functions defined" in captured.out

    repl.functions.append("function foo() -> i32 { return 0 }")
    repl.handle_command(":funcs")
    captured = capsys.readouterr()
    assert "function foo() -> i32" in captured.out

    # Type command
    repl.handle_command(":type 1 + 2")
    captured = capsys.readouterr()
    assert "Type inference not fully implemented yet" in captured.out

    # Clear command
    repl.structs.append("struct Dummy {}")
    repl.handle_command(":clear")
    assert repl.variables == {}
    assert repl.var_values == {}
    assert repl.functions == []
    assert repl.structs == []
    captured = capsys.readouterr()
    assert "Cleared all definitions" in captured.out

    # Unknown command
    repl.handle_command(":unknown")
    captured = capsys.readouterr()
    assert "Unknown command: :unknown" in captured.out


def test_read_multiline():
    repl = FlowREPL()

    with patch("builtins.input", side_effect=["return 1", "}"]):
        lines = repl.read_multiline("function bar() {")
        assert "function bar() {" in lines
        assert "return 1" in lines
        assert "}" in lines

    # EOFError handling in read_multiline
    with patch("builtins.input", side_effect=EOFError):
        lines = repl.read_multiline("function baz() {")
        assert lines == "function baz() {"


def test_process_input_dispatch(capsys):
    repl = FlowREPL()

    # Function dispatch
    with patch.object(repl, "add_function") as mock_add_fn:
        repl.process_input("function test_fn() -> i32 { return 0 }")
        mock_add_fn.assert_called_once()

    # Struct dispatch
    with patch.object(repl, "add_struct") as mock_add_struct:
        repl.process_input("struct TestStruct { a: i32 }")
        mock_add_struct.assert_called_once()

    # Let dispatch
    with patch.object(repl, "add_variable") as mock_add_var:
        repl.process_input("let val = 5")
        mock_add_var.assert_called_once()

    # Expression evaluation dispatch
    with patch.object(repl, "evaluate_expression") as mock_eval:
        repl.process_input("10 + 20")
        mock_eval.assert_called_once_with("10 + 20")


def test_compile_and_run_expr(tmp_path):
    repl = FlowREPL()
    repl.build_dir = tmp_path
    repl.variables["x"] = "i32"
    repl.var_values["x"] = 5
    repl.functions.append("function double_val(n: i32) -> i32 { return n * 2 }")

    # Mock subprocess.run for GCC compilation and execution
    mock_gcc_res = MagicMock(returncode=0, stderr="")
    mock_exec_res = MagicMock(returncode=0, stdout="10\n")

    with patch("subprocess.run", side_effect=[mock_gcc_res, mock_exec_res]):
        res = repl.compile_and_run_expr("double_val(x)")
        assert res == 10

    # Test float return value parsing
    mock_exec_float_res = MagicMock(returncode=0, stdout="3.140000\n")
    with patch("subprocess.run", side_effect=[mock_gcc_res, mock_exec_float_res]):
        res = repl.compile_and_run_expr("3.14")
        assert res == 3.14

    # Test gcc compilation error
    mock_gcc_err_res = MagicMock(returncode=1, stderr="In function 'main': ...")
    with patch("subprocess.run", return_value=mock_gcc_err_res):
        res = repl.compile_and_run_expr("invalid_expr")
        assert res is None


def test_print_banner(capsys):
    repl = FlowREPL()
    repl.print_banner()
    captured = capsys.readouterr()
    assert "FLOW REPL" in captured.out


def test_repl_run_loop(capsys):
    repl = FlowREPL()

    # Test run loop with command input then EOF
    with patch("builtins.input", side_effect=[":help", "", EOFError()]):
        repl.run()

    captured = capsys.readouterr()
    assert "FLOW REPL" in captured.out
    assert "REPL Commands:" in captured.out
    assert "Goodbye!" in captured.out

    # Test KeyboardInterrupt in loop
    with patch("builtins.input", side_effect=[KeyboardInterrupt(), EOFError()]):
        repl.run()

    captured = capsys.readouterr()
    assert "Use :quit or Ctrl+D to exit" in captured.out


def test_main():
    with patch("flow.repl.FlowREPL.run") as mock_run:
        main()
        mock_run.assert_called_once()
