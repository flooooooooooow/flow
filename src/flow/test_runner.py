"""
FLOW Test Runner
Executes test programs and validates their behavior.

This module provides:
- Runtime test execution (compile + run + check exit code/output)
- Support for test "name" { ... } blocks parsed from FLOW files
- Integration with the main ./flow test-runtime command
"""

import subprocess
import tempfile
import os
import sys
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of running a single test."""

    name: str
    passed: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0


class TestRunner:
    """
    Runs FLOW programs as tests.

    Tests are standalone .flow files with a main() function.
    - Exit code 0 = pass
    - Exit code != 0 = fail
    - Optional .expected file for output comparison
    """

    def __init__(self, build_dir: str = None, verbose: bool = False):
        self.build_dir = (
            Path(build_dir)
            if build_dir
            else Path(tempfile.mkdtemp(prefix="flow_test_"))
        )
        self.build_dir.mkdir(exist_ok=True)
        self.verbose = verbose

        # Find the src directory for PYTHONPATH
        self.src_dir = Path(__file__).parent.parent

    def run_file(self, file_path: str) -> TestResult:
        """Run a single FLOW file as a test."""
        file_path = Path(file_path)
        test_name = file_path.stem

        if not file_path.exists():
            return TestResult(test_name, False, error=f"File not found: {file_path}")

        c_file = self.build_dir / f"{test_name}.c"
        exe_file = self.build_dir / test_name

        try:
            # Step 1: Transpile FLOW to C
            transpile_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flow.transpiler",
                    str(file_path),
                    "--c",
                    "--lenient",
                    "-o",
                    str(c_file),
                ],
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": str(self.src_dir)},
                timeout=30,
            )

            if transpile_result.returncode != 0:
                return TestResult(
                    test_name,
                    False,
                    output=transpile_result.stdout,
                    error=f"Transpile failed: {transpile_result.stderr}",
                    exit_code=transpile_result.returncode,
                )

            # Step 2: Compile C to executable
            compile_result = subprocess.run(
                ["clang", str(c_file), "-o", str(exe_file), "-lm"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if compile_result.returncode != 0:
                return TestResult(
                    test_name,
                    False,
                    error=f"Clang compile failed: {compile_result.stderr}",
                    exit_code=compile_result.returncode,
                )

            # Step 3: Run the executable
            run_result = subprocess.run(
                [str(exe_file)], capture_output=True, text=True, timeout=30
            )

            # Step 4: Check output against .expected file if present
            expected_file = file_path.with_suffix(".expected")
            if expected_file.exists():
                expected_output = expected_file.read_text()
                if run_result.stdout != expected_output:
                    return TestResult(
                        test_name,
                        False,
                        output=run_result.stdout,
                        error=f"Output mismatch:\nExpected:\n{expected_output}\nGot:\n{run_result.stdout}",
                        exit_code=run_result.returncode,
                    )

            # Exit code 0 = pass
            passed = run_result.returncode == 0
            return TestResult(
                test_name,
                passed,
                output=run_result.stdout,
                error=run_result.stderr if not passed else "",
                exit_code=run_result.returncode,
            )

        except subprocess.TimeoutExpired:
            return TestResult(test_name, False, error="Test timed out (30s)")
        except FileNotFoundError as e:
            return TestResult(test_name, False, error=f"Required tool not found: {e}")
        except Exception as e:
            return TestResult(test_name, False, error=f"Test execution failed: {e}")
        finally:
            # Clean up generated files
            self._cleanup_files([c_file, exe_file])

    def run_directory(self, directory: str) -> Tuple[int, int, List[TestResult]]:
        """Run all .flow files in a directory as tests."""
        dir_path = Path(directory)
        results = []

        if not dir_path.exists():
            return 0, 0, []

        for flow_file in sorted(dir_path.rglob("*.flow")):
            # Skip files in wip/ directories
            if "wip" in flow_file.parts:
                continue

            result = self.run_file(str(flow_file))
            results.append(result)

            if self.verbose:
                status = "✓" if result.passed else "✗"
                print(f"  {status} {flow_file.relative_to(dir_path)}")
                if not result.passed and result.error:
                    for line in result.error.split("\n")[:3]:
                        print(f"      {line}")

        passed = sum(1 for r in results if r.passed)
        return passed, len(results), results

    def _cleanup_files(self, files: List[Path]):
        """Remove temporary files, ignoring errors."""
        for f in files:
            try:
                if f.exists():
                    f.unlink()
            except Exception:
                pass

    def cleanup(self):
        """Remove the build directory."""
        import shutil

        try:
            shutil.rmtree(self.build_dir)
        except Exception:
            pass


def run_tests_from_directory(directory: str, verbose: bool = False) -> int:
    """
    Run all FLOW tests in a directory.
    Returns exit code (0 = all passed, 1 = some failed).
    """
    runner = TestRunner(verbose=verbose)

    try:
        passed, total, results = runner.run_directory(directory)

        print(f"\n{'=' * 40}")
        if total == 0:
            print("No tests found.")
            return 0

        if passed == total:
            print(f"✅ All {total} tests passed!")
            return 0
        else:
            print(f"❌ {total - passed}/{total} tests failed")
            if not verbose:
                print("\nFailed tests:")
                for r in results:
                    if not r.passed:
                        print(
                            f"  - {r.name}: {r.error[:80] if r.error else f'exit code {r.exit_code}'}"
                        )
            return 1
    finally:
        runner.cleanup()


def main():
    """Command-line entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run FLOW runtime tests")
    parser.add_argument(
        "path",
        nargs="?",
        default="tests/runtime",
        help="Directory or file to test (default: tests/runtime)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed output"
    )

    args = parser.parse_args()

    path = Path(args.path)

    if path.is_file():
        runner = TestRunner(verbose=args.verbose)
        result = runner.run_file(str(path))

        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status}: {result.name}")
        if result.output:
            print(f"Output: {result.output}")
        if result.error:
            print(f"Error: {result.error}")

        runner.cleanup()
        return 0 if result.passed else 1
    else:
        return run_tests_from_directory(str(path), verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
