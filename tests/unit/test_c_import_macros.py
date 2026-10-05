"""@cImport reads integer `#define`s out of a header (#550).

Ordinary preprocessing expands macros and discards the definitions, so a
constant like O_RDONLY disappeared before the parser saw it. Writing the
number into a .flow file instead is wrong on some platform: O_CREAT is 0x200
on macOS and 0x40 on Linux, and SIGCHLD is 20 against 17.
"""

from __future__ import annotations

import shutil

import pytest

from flow.c_header_parser import parse_header_macros

pytestmark = pytest.mark.skipif(
    shutil.which("cpp") is None and shutil.which("clang") is None,
    reason="needs a C preprocessor",
)


def _macros(header: str) -> dict[str, str]:
    return {c.name: c.value.value for c in parse_header_macros(header)}


def test_plain_integer_defines_are_read():
    flags = _macros("fcntl.h")
    assert flags["O_RDONLY"] == "0"
    assert flags["O_WRONLY"] == "1"
    assert int(flags["O_CREAT"]) > 0


def test_hex_and_octal_are_decoded():
    """O_CREAT is 0x00000200 on macOS and 0100 on Linux."""
    value = int(_macros("fcntl.h")["O_CREAT"])
    assert value in (0x200, 0o100), value


def test_cast_wrapped_defines_are_read():
    """INADDR_ANY is `((u_int32_t)0x00000000)`, not a bare integer."""
    addresses = _macros("netinet/in.h")
    assert addresses["INADDR_ANY"] == "0"
    assert addresses["INADDR_LOOPBACK"] == str(0x7F000001)


def test_compiler_internal_defines_are_skipped():
    names = set(_macros("fcntl.h"))
    assert not any(n.startswith("_") for n in names)


def test_a_missing_header_yields_nothing():
    """cpp still prints its own built-ins when the include fails.

    Without checking the exit status, @cImport of a header that is not
    installed imported 22 platform macros and none of what it asked for,
    which broke an unrelated test that imports julia.h.
    """
    assert parse_header_macros("definitely/not/a/real/header.h") == []
