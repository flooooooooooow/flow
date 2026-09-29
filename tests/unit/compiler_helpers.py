"""Shared helpers for compiler-suite unit tests (C-compiler-grade harness)."""

from __future__ import annotations

import shutil
from typing import List

import pytest

from flow.parser import parse_flow_code
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
