"""@cImport reads the declaration forms glibc uses, not only Apple's.

Three defects stacked up, and each hid the next. Together they meant
`@cImport` imported almost nothing on Linux while working on macOS, which is
why two POSIX tutorials verified locally and failed in CI.

The fixture is a header rather than the host's, so this runs the same on
either platform.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from flow.c_header_parser import parse_c_header

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "c_headers" / "glibc_style.h"

pytestmark = pytest.mark.skipif(
    not any(shutil.which(c) for c in ("cpp", "clang", "gcc")),
    reason="needs a C preprocessor",
)


def imported() -> dict:
    return {
        d.name: d
        for d in parse_c_header(str(FIXTURE), [str(FIXTURE.parent)])
        if hasattr(d, "name")
    }


def test_extern_function_declarations_are_imported():
    """glibc writes `extern int open (...)` for every function.

    The whole chunk was skipped as an "extern variable declaration", so on
    Linux almost nothing arrived.
    """
    names = imported()
    for want in ("open", "openat", "creat", "fcntl", "lseek"):
        assert want in names, f"{want} missing; got {sorted(names)}"


def test_a_nested_attribute_does_not_eat_the_declaration():
    """`__attribute__ ((__nonnull__ (1)))` has parentheses inside it.

    A regex stopping at the first `)` left a stray one behind and the
    declaration around it stopped parsing.
    """
    assert "creat" in imported()


def test_an_absolute_header_path_is_quoted():
    """`#include /path/x.h` is not valid C; it has to be quoted.

    The preprocessor produced nothing and @cImport reported only that it
    could not preprocess the header.
    """
    assert imported(), "an absolute path imported nothing"


def test_a_variadic_declaration_keeps_its_fixed_prefix():
    open_decl = imported()["open"]
    assert [p.type.name for p in open_decl.parameters][:2] == ["ptr<u8>", "i32"]
    assert open_decl.is_variadic


def test_posix_typedefs_map_to_flow_integers():
    """`off_t` left as a C name matches no call."""
    lseek = imported()["lseek"]
    assert [p.type.name for p in lseek.parameters] == ["i32", "i64", "i32"]


def test_the_reserved_typedef_spellings_map_too():
    """glibc declares prototypes against `__off_t`, not `off_t`.

    Mapping only the portable spelling left `lseek` taking a parameter typed
    `__off_t`, which matched no call, so the fix for `off_t` looked complete
    while Linux still failed.
    """
    names = imported()
    assert [p.type.name for p in names["lseek"].parameters] == ["i32", "i64", "i32"]
    assert names["lseek"].return_type.name == "i64"
    assert names["read"].return_type.name == "i64"
