"""
FLOW Test Runner
Executes test declarations found in FLOW files.

This module:
- Parses FLOW files for test declarations
- Compiles and runs each test
- Reports results
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import List, Tuple

from .parser import FunctionDecl
from .module_resolver import resolve_modules


class TestResult:
    def __init__(self, name: str, passed: bool, output: str = "", error: str = ""):
        self.name = name
        self.passed = passed
        self.output = output
        self.error = error


class TestRunner:
    def __init__(self, build_dir: str = None):
        self.build_dir = Path(build_dir) if build_dir else Path(tempfile.mkdtemp(prefix="flow_test_"))
        self.build_dir.mkdir(exist_ok=True)

    def run_file_tests(self, file_path: str) -> List[TestResult]:
        """Run all tests in a single FLOW file."""
        try:
            # Resolve modules and find test functions
            declarations = resolve_modules(file_path)
            tests = [d for d in declarations if isinstance(d, FunctionDecl) and "test" in getattr(d, 'attributes', [])]

            if not tests:
                return []

            results = []
            for test in tests:
                result = self._run_single_test(file_path, test)
                results.append(result)

            return results

        except Exception as e:
            return [TestResult(f"Error loading {file_path}", False, error=str(e))]

    def run_all_tests(self, directories: List[str]) -> Tuple[int, int, List[TestResult]]:
        """Run all tests in the given directories."""
        all_results = []

        for directory in directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue

            # Find all .flow files
            for flow_file in dir_path.rglob("*.flow"):
                results = self.run_file_tests(str(flow_file))
                all_results.extend(results)

        passed = sum(1 for r in all_results if r.passed)
        total = len(all_results)

        return passed, total, all_results

    def _run_single_test(self, file_path: str, test: FunctionDecl) -> TestResult:
        """Run a single test by creating a wrapper program."""
        # Create a wrapper program that calls the test
        wrapper_code = self._create_test_wrapper(file_path, test)

        # Write to a temporary file
        test_file = self.build_dir / f"test_{test.name.replace(' ', '_')}.flow"
        with open(test_file, 'w') as f:
            f.write(wrapper_code)

        try:
            # Compile the wrapper
            exe_file = self.build_dir / f"test_{test.name.replace(' ', '_')}"

            # Use clang to compile (since we have C backend)
            c_file = self.build_dir / f"test_{test.name.replace(' ', '_')}.c"

            # Compile FLOW to C
            import sys
            flow_src = Path(__file__).parent
            result = subprocess.run([
                sys.executable, '-m', 'flow.transpiler', str(test_file), '--c', '-o', str(c_file)
            ], capture_output=True, text=True, cwd=flow_src, env={'PYTHONPATH': str(flow_src.parent)})

            if result.returncode != 0:
                return TestResult(test.name, False, error=f"Compilation failed: {result.stderr}")

            # Compile C to executable
            compile_result = subprocess.run([
                'clang', str(c_file), '-o', str(exe_file), '-lm'
            ], capture_output=True, text=True)

            if compile_result.returncode != 0:
                return TestResult(test.name, False, error=f"C compilation failed: {compile_result.stderr}")

            # Run the test
            run_result = subprocess.run([str(exe_file)], capture_output=True, text=True, timeout=30)

            # Check exit code - 0 means pass, non-zero means fail
            passed = run_result.returncode == 0
            output = run_result.stdout
            error = run_result.stderr

            return TestResult(test.name, passed, output, error)

        except subprocess.TimeoutExpired:
            return TestResult(test.name, False, error="Test timed out")
        except Exception as e:
            return TestResult(test.name, False, error=f"Test execution failed: {e}")
        finally:
            # Clean up temporary files
            try:
                test_file.unlink(missing_ok=True)
                if exe_file.exists():
                    exe_file.unlink()
                if c_file.exists():
                    c_file.unlink()
            except:
                pass

    def _create_test_wrapper(self, original_file: str, test: FunctionDecl) -> str:
        """Create a wrapper program that runs the test."""
        # Parse the original file to get all declarations
        from .module_resolver import resolve_modules
        declarations = resolve_modules(original_file)

        # Find all non-test functions and the specific test function
        functions = [d for d in declarations if isinstance(d, FunctionDecl)]
        test_functions = [f for f in functions if f.name == test.name]
        helper_functions = [f for f in functions if f.name != test.name and "test" not in getattr(f, 'attributes', [])]

        if not test_functions:
            return "// Test function not found"

        # Generate FLOW code for helper functions and the test
        lines = []
        for func in helper_functions:
            lines.append(self._function_to_code(func))
            lines.append("")

        # Add the test function
        lines.append(self._function_to_code(test_functions[0]))
        lines.append("")

        # Add main function
        lines.append("function main() -> i32 {")
        lines.append(f"    let result: bool = {test.name}()")
        lines.append("    if result {")
        lines.append("        return 0")
        lines.append("    } else {")
        lines.append("        return 1")
        lines.append("    }")
        lines.append("}")

        return "\n".join(lines)

    def _function_to_code(self, func: FunctionDecl) -> str:
        """Convert a function declaration back to FLOW code."""
        params = ", ".join(f"{p.name}: {self._type_to_code(p.type)}" for p in func.parameters)
        return_type = self._type_to_code(func.return_type)

        lines = [f"function {func.name}({params}) -> {return_type} {{"]
        lines.extend(self._block_to_code(func.body))
        lines.append("}")

        return "\n".join(lines)

    def _type_to_code(self, type_obj) -> str:
        """Convert type back to FLOW code."""
        if hasattr(type_obj, 'name'):
            return type_obj.name
        return "void"

    def _block_to_code(self, block) -> list[str]:
        """Convert a block to FLOW code lines."""
        lines = []
        for stmt in block.statements:
            if hasattr(stmt, 'name') and hasattr(stmt, 'type'):
                # Variable declaration
                type_str = self._type_to_code(stmt.type)
                if stmt.initializer:
                    init_str = self._expr_to_code(stmt.initializer)
                    lines.append(f"    let {stmt.name}: {type_str} = {init_str}")
                else:
                    lines.append(f"    let {stmt.name}: {type_str}")
            elif hasattr(stmt, 'value'):
                # Return statement
                if stmt.value:
                    val_str = self._expr_to_code(stmt.value)
                    lines.append(f"    return {val_str}")
                else:
                    lines.append("    return")
        return lines

    def _expr_to_code(self, expr) -> str:
        """Convert expression back to FLOW code."""
        if hasattr(expr, 'value'):
            return str(expr.value)
        elif hasattr(expr, 'name'):
            return expr.name
        elif hasattr(expr, 'left') and hasattr(expr, 'right'):
            left = self._expr_to_code(expr.left)
            right = self._expr_to_code(expr.right)
            return f"{left} {expr.operator} {right}"
        elif hasattr(expr, 'arguments'):
            args = [self._expr_to_code(arg) for arg in expr.arguments]
            return f"{expr.name}({', '.join(args)})"
        return "<expr>"

    def _block_to_code(self, block) -> str:
        """Convert a block back to FLOW code (simplified)."""
        # This is a very basic conversion - just handle the statements we expect in tests
        lines = []
        for stmt in block.statements:
            if hasattr(stmt, 'name') and hasattr(stmt, 'initializer'):
                # Variable declaration
                type_str = self._type_to_string(stmt.type) if hasattr(stmt, 'type') and stmt.type else "auto"
                init_str = self._expr_to_string(stmt.initializer)
                lines.append(f"    let {stmt.name}: {type_str} = {init_str}")
            elif hasattr(stmt, 'target') and hasattr(stmt, 'value'):
                # Assignment
                value_str = self._expr_to_string(stmt.value)
                lines.append(f"    {stmt.target} = {value_str}")
            elif hasattr(stmt, 'condition') and hasattr(stmt, 'then_block'):
                # If statement
                cond_str = self._expr_to_string(stmt.condition)
                then_code = self._block_to_code(stmt.then_block)
                lines.append(f"    if {cond_str} {{")
                lines.extend(then_code.split('\n'))
                if hasattr(stmt, 'else_block') and stmt.else_block:
                    else_code = self._block_to_code(stmt.else_block)
                    lines.append("    } else {")
                    lines.extend(else_code.split('\n'))
                lines.append("    }")
            elif hasattr(stmt, 'value'):
                # Return or expression statement
                if hasattr(stmt, 'value') and stmt.value:
                    val_str = self._expr_to_string(stmt.value)
                    lines.append(f"    {val_str}")
        return '\n'.join(lines)

    def _expr_to_string(self, expr) -> str:
        """Convert expression back to string (very basic)."""
        if hasattr(expr, 'value'):
            return str(expr.value)
        elif hasattr(expr, 'name'):
            return expr.name
        elif hasattr(expr, 'left') and hasattr(expr, 'right') and hasattr(expr, 'operator'):
            left = self._expr_to_string(expr.left)
            right = self._expr_to_string(expr.right)
            return f"{left} {expr.operator} {right}"
        elif hasattr(expr, 'arguments'):
            args = [self._expr_to_string(arg) for arg in expr.arguments]
            return f"{expr.name}({', '.join(args)})"
        else:
            return "<expr>"

    def _type_to_string(self, type_obj) -> str:
        """Convert type back to string."""
        if hasattr(type_obj, 'name'):
            return type_obj.name
        return "auto"


def run_test_command(args):
    """Command-line interface for running tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Run FLOW tests")
    parser.add_argument("files", nargs="*", help="FLOW files to test")
    parser.add_argument("--dir", action="append", help="Directories to search for tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    parsed_args = parser.parse_args(args)

    directories = parsed_args.dir or ["tests", "examples"]

    runner = TestRunner()

    if parsed_args.files:
        # Run specific files
        all_results = []
        for file in parsed_args.files:
            results = runner.run_file_tests(file)
            all_results.extend(results)
    else:
        # Run all tests in directories
        _, _, all_results = runner.run_all_tests(directories)

    # Report results
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    if total == 0:
        print("No tests found.")
        return 0

    print(f"\nRan {total} tests: {passed} passed, {total - passed} failed")

    if parsed_args.verbose:
        for result in all_results:
            status = "✓" if result.passed else "✗"
            print(f"{status} {result.name}")
            if result.error:
                print(f"  Error: {result.error}")
            if result.output and not result.passed:
                print(f"  Output: {result.output}")

    return 0 if passed == total else 1