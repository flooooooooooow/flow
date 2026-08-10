"""Shared helpers for compiler-suite unit tests (C-compiler-grade harness)."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import List, Optional

import pytest

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c
from flow.monomorphize import monomorphize
from flow.type_checker import TypeChecker, TypeCheckResult


needs_clang = pytest.mark.skipif(
    shutil.which("clang") is None, reason="clang not available"
)


def parse(source: str):
    return parse_flow_code(source)


def typecheck(source: str, *, strict: bool = True) -> TypeCheckResult:
    checker = TypeChecker()
    checker.strict = strict
    return checker.check(parse(source))


def errors(source: str, *, strict: bool = True) -> List[str]:
    return typecheck(source, strict=strict).errors


def warnings(source: str, *, strict: bool = True) -> List[str]:
    return typecheck(source, strict=strict).warnings


def to_c(source: str, *, do_mono: bool = True, **kwargs) -> str:
    decls = parse(source)
    if do_mono:
        decls = monomorphize(decls)
    return flow_to_c(decls, **kwargs)


def compile_and_run(
    source: str,
    *,
    do_mono: bool = True,
    extra_cflags: Optional[List[str]] = None,
) -> int:
    """Transpile → clang → run; return process exit code."""
    c_code = to_c(source, do_mono=do_mono)
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        bin_path = os.path.join(td, "prog")
        with open(c_path, "w") as f:
            f.write(c_code)
        cmd = ["clang", "-O0", "-o", bin_path, c_path, "-lm"]
        if extra_cflags:
            cmd[1:1] = extra_cflags
        build = subprocess.run(cmd, capture_output=True, text=True)
        assert build.returncode == 0, f"clang failed:\n{build.stderr}\n---\n{c_code}"
        return subprocess.run([bin_path], capture_output=True).returncode


def compile_c_only(source: str, *, do_mono: bool = True) -> str:
    """Return generated C after a successful clang -fsyntax-only."""
    c_code = to_c(source, do_mono=do_mono)
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        with open(c_path, "w") as f:
            f.write(c_code)
        syn = subprocess.run(
            ["clang", "-fsyntax-only", c_path], capture_output=True, text=True
        )
        assert syn.returncode == 0, f"clang -fsyntax-only failed:\n{syn.stderr}\n---\n{c_code}"
    return c_code
