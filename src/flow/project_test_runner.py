"""Project-level test runner for Flow.

`flow test` uses this module outside the Flow compiler repository itself.

A project test is either:

    test "descriptive name" {
        expect condition
    }

or a compatibility-style standalone `.flow` program whose `main()` returns
zero on success. Native `test` blocks are isolated and executed one at a time,
which gives deterministic case-level reporting while reusing the normal Flow
compiler and runtime path.

Sibling golden files are supported for program tests:
    foo.expected
    foo.expected-stderr
    foo.exitcode

For named tests, use the stable slug printed by `flow test --list`:
    foo.<slug>.expected
    foo.<slug>.expected-stderr
    foo.<slug>.exitcode

The runner deliberately does not contain a second compiler pipeline. It calls
the same internal Flow driver used by `flow compile`, then executes the emitted
binary directly so compiler chatter cannot contaminate stdout/stderr goldens.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    import tomllib
except ImportError:  # Python 3.9/3.10
    import tomli as tomllib  # type: ignore


TEST_HEADER_RE = re.compile(
    r'(?m)^(?P<indent>[ \t]*)test\s+"(?P<name>(?:[^"\\]|\\.)*)"\s*\{'
)
MAIN_RE = re.compile(r"(?m)^\s*function\s+main\s*\(")
EXCLUDED_PARTS = {
    ".git",
    ".flow-audio-test",
    ".flow-test",
    "build",
    "flow_packages",
    "wip",
    "__pycache__",
}


@dataclass(frozen=True)
class NativeTest:
    name: str
    slug: str
    function_name: str
    index: int


@dataclass(frozen=True)
class TestCase:
    source: Path
    display_id: str
    backend: str
    native: Optional[NativeTest] = None


@dataclass
class CaseResult:
    case: TestCase
    passed: bool
    duration_s: float
    phase: str = "run"
    message: str = ""
    stdout: str = ""
    stderr: str = ""


def _decode_test_name(raw: str) -> str:
    try:
        return json.loads('"' + raw + '"')
    except Exception:
        return raw


def _slug(text: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return value or "case"


def _find_project_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "flow.toml").is_file():
            return candidate
    return current


def _load_test_config(root: Path) -> dict:
    path = root / "flow.toml"
    if not path.is_file():
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"cannot parse {path}: {exc}") from exc
    section = data.get("test", {})
    return section if isinstance(section, dict) else {}


def _configured_paths(root: Path, config: dict) -> list[Path]:
    raw = config.get("paths", ["tests"])
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        raise RuntimeError("[test].paths must be a string or array of strings")
    return [(root / str(item)).resolve() for item in raw]


def _discover_files(targets: Iterable[Path]) -> list[Path]:
    found: set[Path] = set()
    for target in targets:
        target = target.resolve()
        if target.is_file():
            if target.suffix == ".flow":
                found.add(target)
            continue
        if not target.is_dir():
            continue
        for path in target.rglob("*.flow"):
            rel_parts = set(path.relative_to(target).parts)
            if rel_parts & EXCLUDED_PARTS:
                continue
            if path.name.startswith("_") or path.name.startswith(".flow_test_"):
                continue
            found.add(path.resolve())
    return sorted(found, key=lambda p: str(p))


def _native_tests(source: str) -> list[NativeTest]:
    tests: list[NativeTest] = []
    used: dict[str, int] = {}
    for index, match in enumerate(TEST_HEADER_RE.finditer(source)):
        name = _decode_test_name(match.group("name"))
        base_slug = _slug(name)
        occurrence = used.get(base_slug, 0) + 1
        used[base_slug] = occurrence
        slug = base_slug if occurrence == 1 else f"{base_slug}_{occurrence}"
        tests.append(
            NativeTest(
                name=name,
                slug=slug,
                function_name=f"__flow_test_{index}_{slug}",
                index=index,
            )
        )
    return tests


def _rewrite_native_file(source: str, selected: NativeTest) -> str:
    """Turn each native test header into a void function and call one case.

    Only the header text changes, so source line numbers in the test body stay
    aligned with the original file. `expect` remains the assertion primitive.
    """
    counter = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal counter
        raw_name = _decode_test_name(match.group("name"))
        # Recompute the exact stable function name in source order. Slugs are
        # already made unique by _native_tests; use that table by index.
        all_tests = tests_by_index[counter]
        counter += 1
        return f'{match.group("indent")}function {all_tests.function_name}() -> void {{'

    natives = _native_tests(source)
    tests_by_index = {test.index: test for test in natives}
    rewritten = TEST_HEADER_RE.sub(replace, source)

    # Native-test files should not normally define main(), but renaming it
    # makes the transformation composable with old program-style helpers.
    rewritten = re.sub(
        r"(?m)^(?P<indent>[ \t]*)function\s+main\s*\(",
        r"\g<indent>function __flow_test_original_main(",
        rewritten,
        count=1,
    )
    rewritten += (
        "\n\n# Generated by flow test; not written back to the project.\n"
        "function main() -> i32 {\n"
        f"    {selected.function_name}()\n"
        "    return 0\n"
        "}\n"
    )
    return rewritten


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _matches_filter(case_id: str, pattern: Optional[str]) -> bool:
    if not pattern:
        return True
    if any(ch in pattern for ch in "*?["):
        return fnmatch.fnmatch(case_id, pattern)
    return pattern.lower() in case_id.lower()


def _golden_base(case: TestCase) -> Path:
    if case.native is None:
        return case.source.with_suffix("")
    return case.source.with_suffix("").with_name(
        case.source.stem + "." + case.native.slug
    )


def _expected_exit(base: Path) -> int:
    path = Path(str(base) + ".exitcode")
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8").strip()
    try:
        return int(text)
    except ValueError as exc:
        raise RuntimeError(f"invalid exit code in {path}: {text!r}") from exc


def _compare_golden(actual: str, path: Path, label: str) -> Optional[str]:
    if not path.is_file():
        return None
    expected = path.read_text(encoding="utf-8")
    if actual == expected:
        return None
    return (
        f"{label} mismatch against {path}\n"
        f"--- expected ({len(expected)} bytes)\n"
        f"+++ actual   ({len(actual)} bytes)"
    )


def _driver_path() -> Path:
    override = os.environ.get("FLOW_TEST_DRIVER")
    if override:
        return Path(override).resolve()
    root = Path(__file__).resolve().parents[2]
    candidate = root / "flow-driver"
    if candidate.is_file():
        return candidate
    raise RuntimeError("Flow test driver not found; set FLOW_TEST_DRIVER")


def _build_dir() -> Path:
    override = os.environ.get("FLOW_TEST_BUILD_DIR")
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[2] / "build"


def _compile(
    program: Path,
    backend: str,
    timeout: float,
    sanitize: Optional[str],
    profile: Optional[str],
    host: Optional[str],
) -> tuple[subprocess.CompletedProcess[str], Path]:
    driver = _driver_path()
    command = [str(driver), "compile", str(program), f"--backend={backend}"]
    if sanitize:
        command.append(f"--sanitize={sanitize}")
    if profile:
        command.append(f"--profile={profile}")

    env = os.environ.copy()
    if host:
        env["FLOW_HOST"] = host

    completed = subprocess.run(
        command,
        cwd=str(Path.cwd()),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    executable = _build_dir() / program.stem
    return completed, executable


def _run_case(
    case: TestCase,
    timeout: float,
    sanitize: Optional[str],
    profile: Optional[str],
    host: Optional[str],
    keep: bool,
) -> CaseResult:
    started = time.monotonic()
    source_text = case.source.read_text(encoding="utf-8")
    temp_path: Optional[Path] = None
    program = case.source

    try:
        if case.native is not None:
            rewritten = _rewrite_native_file(source_text, case.native)
            fd, name = tempfile.mkstemp(
                prefix=f".flow_test_{case.source.stem}_{case.native.index}_",
                suffix=".flow",
                dir=str(case.source.parent),
                text=True,
            )
            os.close(fd)
            temp_path = Path(name)
            temp_path.write_text(rewritten, encoding="utf-8")
            program = temp_path

        try:
            compiled, executable = _compile(
                program,
                case.backend,
                timeout,
                sanitize,
                profile,
                host,
            )
        except subprocess.TimeoutExpired:
            return CaseResult(
                case,
                False,
                time.monotonic() - started,
                phase="compile",
                message=f"compile timed out after {timeout:g}s",
            )

        if compiled.returncode != 0 or not executable.is_file():
            return CaseResult(
                case,
                False,
                time.monotonic() - started,
                phase="compile",
                message=f"compiler exited {compiled.returncode}",
                stdout=compiled.stdout,
                stderr=compiled.stderr,
            )

        try:
            run = subprocess.run(
                [str(executable)],
                cwd=str(case.source.parent),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            return CaseResult(
                case,
                False,
                time.monotonic() - started,
                phase="run",
                message=f"test timed out after {timeout:g}s",
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
            )

        base = _golden_base(case)
        wanted_exit = _expected_exit(base)
        errors: list[str] = []
        if run.returncode != wanted_exit:
            errors.append(f"exit code {run.returncode}, expected {wanted_exit}")
        stdout_error = _compare_golden(
            run.stdout, Path(str(base) + ".expected"), "stdout"
        )
        stderr_error = _compare_golden(
            run.stderr, Path(str(base) + ".expected-stderr"), "stderr"
        )
        if stdout_error:
            errors.append(stdout_error)
        if stderr_error:
            errors.append(stderr_error)

        return CaseResult(
            case,
            not errors,
            time.monotonic() - started,
            phase="run",
            message="; ".join(errors),
            stdout=run.stdout,
            stderr=run.stderr,
        )
    finally:
        if temp_path is not None and temp_path.exists() and not keep:
            temp_path.unlink()
        if not keep and program != case.source:
            generated = _build_dir() / program.stem
            for candidate in (generated, generated.with_suffix(".c"), generated.with_suffix(".ll")):
                try:
                    candidate.unlink()
                except FileNotFoundError:
                    pass


def _cases_for_file(path: Path, root: Path, backends: list[str]) -> list[TestCase]:
    source = path.read_text(encoding="utf-8")
    natives = _native_tests(source)
    rel = _relative(path, root)
    cases: list[TestCase] = []

    if natives:
        for backend in backends:
            for native in natives:
                cases.append(
                    TestCase(
                        source=path,
                        display_id=f"{rel}::{native.name}",
                        backend=backend,
                        native=native,
                    )
                )
        return cases

    if MAIN_RE.search(source):
        for backend in backends:
            cases.append(TestCase(path, rel, backend, None))
    return cases


def _resolve_backends(value: str) -> list[str]:
    if value == "all":
        return ["c", "mlir"]
    if value in {"c", "mlir"}:
        return [value]
    raise RuntimeError(f"unknown backend {value!r}; expected c, mlir, or all")


def _parser(default_backend: str, default_timeout: float) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flow test",
        description="Discover, compile and run tests in the current Flow project.",
    )
    parser.add_argument("paths", nargs="*", help="test files/directories; defaults to [test].paths or tests/")
    parser.add_argument("--filter", "-f", help="substring or glob matched against file::test name")
    parser.add_argument("--list", action="store_true", help="list discovered cases without compiling")
    parser.add_argument("--backend", choices=["c", "mlir", "all"], default=default_backend)
    parser.add_argument("--sanitize", help="ub, asan, tsan, or a comma-separated combination")
    parser.add_argument("--profile", choices=["safety", "flight"])
    parser.add_argument("--host", choices=["flowc", "python", "auto"], help="override FLOW_HOST for compilation")
    parser.add_argument("--timeout", type=float, default=default_timeout, help="per compile/run timeout in seconds")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--keep", action="store_true", help="keep generated native-test wrappers/artifacts")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = _find_project_root(Path.cwd())
    try:
        config = _load_test_config(root)
        default_backend = str(config.get("backend", "c"))
        default_timeout = float(config.get("timeout", 30))
    except Exception as exc:
        print(f"flow test: {exc}", file=sys.stderr)
        return 2

    args = _parser(default_backend, default_timeout).parse_args(argv)
    try:
        backends = _resolve_backends(args.backend)
        targets = [Path(item) if Path(item).is_absolute() else root / item for item in args.paths]
        if not targets:
            targets = _configured_paths(root, config)
        files = _discover_files(targets)
    except Exception as exc:
        print(f"flow test: {exc}", file=sys.stderr)
        return 2

    cases: list[TestCase] = []
    for file in files:
        cases.extend(_cases_for_file(file, root, backends))
    cases = [case for case in cases if _matches_filter(case.display_id, args.filter)]

    if not cases:
        searched = ", ".join(_relative(p, root) for p in targets)
        print(f"flow test: no runnable tests found ({searched})", file=sys.stderr)
        return 2

    if args.list:
        for case in cases:
            suffix = "" if len(backends) == 1 else f" [{case.backend}]"
            print(case.display_id + suffix)
        print(f"\n{len(cases)} test case(s)")
        return 0

    backend_text = ",".join(backends)
    print(f"running {len(cases)} tests (backend={backend_text})")
    failures = 0
    passed = 0
    started = time.monotonic()

    for case in cases:
        label = case.display_id
        if len(backends) > 1:
            label += f" [{case.backend}]"
        print(f"test {label} ... ", end="", flush=True)
        try:
            result = _run_case(
                case,
                args.timeout,
                args.sanitize,
                args.profile,
                args.host,
                args.keep,
            )
        except Exception as exc:
            result = CaseResult(case, False, 0.0, phase="runner", message=str(exc))

        if result.passed:
            passed += 1
            print(f"ok ({result.duration_s:.3f}s)")
            if args.verbose:
                if result.stdout:
                    print("  stdout:")
                    print("\n".join("    " + line for line in result.stdout.rstrip("\n").splitlines()))
                if result.stderr:
                    print("  stderr:")
                    print("\n".join("    " + line for line in result.stderr.rstrip("\n").splitlines()))
            continue

        failures += 1
        print(f"FAILED ({result.phase}, {result.duration_s:.3f}s)")
        if result.message:
            print("  " + result.message.replace("\n", "\n  "))
        if result.stdout:
            print("  stdout:")
            print("\n".join("    " + line for line in result.stdout.rstrip("\n").splitlines()))
        if result.stderr:
            print("  stderr:")
            print("\n".join("    " + line for line in result.stderr.rstrip("\n").splitlines()))
        if args.fail_fast:
            break

    elapsed = time.monotonic() - started
    ran = passed + failures
    status = "ok" if failures == 0 else "FAILED"
    print(
        f"\ntest result: {status}. {passed} passed; {failures} failed; "
        f"{len(cases) - ran} not run; finished in {elapsed:.3f}s"
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
