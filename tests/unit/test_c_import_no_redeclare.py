"""@cImport must not re-declare anything the #include already provides.

The generator emits `#include "header.h"` for every @cImport. Anything it
also emits from the parsed header is a duplicate, and C rejects duplicates
whose spelling differs from the original.

This surfaced as a Linux-only CI failure while macOS stayed green:

    tests/lang/test_c_import_auto.flow
    error: typedef redefinition with different types
           ('struct lldiv_t' vs 'struct lldiv_t' (aka 'lldiv_t'))
    error: conflicting types for 'llrint'

macOS hid it twice over. Its system headers expand differently, and on some
installs `cpp -P -` fails outright, so @cImport parsed nothing at all and the
tests passed without exercising the feature.

These tests use a fixture header rather than a system one, so they assert the
same thing on every platform.
"""

from __future__ import annotations

import shutil
import subprocess
import textwrap

import pytest

from flow.c_generator import flow_to_c
from flow.c_header_parser import _preprocess_header, parse_c_header, resolve_c_imports
from flow.parser import CImportDecl, ExternTypeDecl, parse_flow_code

needs_clang = pytest.mark.skipif(
    shutil.which("clang") is None, reason="clang not available"
)


def build_c(source: str, source_dir) -> str:
    """Parse, resolve @cImport, and generate C, as the transpiler does."""
    decls = parse_flow_code(source)
    decls = resolve_c_imports(decls, str(source_dir))
    return flow_to_c(decls)

# Shaped like glibc's stdlib.h (names chosen not to clash with libc): an anonymous struct bound to a name by typedef,
# plus extern functions. This is the shape that broke the build.
GLIBC_SHAPED = """\
#ifndef FIXTURE_H
#define FIXTURE_H
typedef struct { long long quot; long long rem; } fixdiv_t;
typedef struct _fixopaque_s fixopaque_t;
extern long long fixrint (double __x);
extern fixdiv_t fixdiv (long long __n, long long __d);
#endif
"""


@pytest.fixture()
def header_dir(tmp_path):
    (tmp_path / "fixture.h").write_text(GLIBC_SHAPED)
    return tmp_path


def test_preprocessor_expands_the_header(header_dir):
    """A working preprocessor must be found, whatever `cpp` does here.

    Empty output used to be accepted, which silently disabled @cImport.
    """
    text = _preprocess_header("fixture.h", [str(header_dir)])
    assert "fixdiv_t" in text, (
        "no preprocessor produced output; @cImport would silently import nothing"
    )


def test_every_imported_declaration_is_marked(header_dir):
    """resolve_c_imports must mark all declarations, not just functions."""
    decls = resolve_c_imports(
        [CImportDecl(header="fixture.h", alias=None)], str(header_dir)
    )
    imported = [d for d in decls if not isinstance(d, type(decls[0]))]
    marked = [d for d in decls if getattr(d, "is_c_import", False)]
    unmarked = [
        d
        for d in imported
        if not getattr(d, "is_c_import", False) and hasattr(d, "name")
    ]
    assert not unmarked, f"unmarked imported declarations would be re-emitted: {unmarked}"
    assert marked, "expected at least one marked declaration"


PROGRAM = """\
@cImport("fixture.h")

extern {
    function puts(s: string) -> i32
}

function main() -> i32 {
    puts("ok")
    return 0
}
"""


def test_imported_types_are_not_redeclared_in_c(header_dir):
    """The generated C must not contain a typedef for an imported type."""
    c_out = build_c(PROGRAM, header_dir)

    assert '#include "fixture.h"' in c_out, "the header include should still be emitted"
    for name in ("fixdiv_t", "fixopaque_t"):
        assert f"typedef struct {name} {name};" not in c_out, (
            f"{name} is declared by the included header; re-emitting it is a "
            "typedef redefinition and clang rejects it on glibc"
        )


@needs_clang
def test_generated_c_compiles_against_the_real_header(header_dir, tmp_path):
    """The end the bug was actually felt at: clang must accept the output."""
    c_out = build_c(PROGRAM, header_dir)
    c_file = tmp_path / "prog.c"
    c_file.write_text(c_out)

    result = subprocess.run(
        ["clang", "-fsyntax-only", "-I", str(header_dir), str(c_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "generated C does not compile against the header it imported:\n"
        f"{result.stderr}"
    )


def test_non_imported_extern_types_still_emit(tmp_path):
    """The skip must be scoped to @cImport, not applied to every extern type."""
    source = textwrap.dedent(
        """\
        extern type MyHandle

        extern {
            function puts(s: string) -> i32
        }

        function main() -> i32 {
            puts("ok")
            return 0
        }
        """
    )
    c_out = build_c(source, tmp_path)
    assert "typedef struct MyHandle MyHandle;" in c_out, (
        "a plain `extern type` has no #include behind it, so it still needs "
        "its own declaration"
    )


def test_parse_returns_extern_type_for_named_struct_typedef(header_dir):
    """`typedef struct _fixopaque_s fixopaque_t;` should yield an ExternTypeDecl."""
    parsed = parse_c_header("fixture.h", [str(header_dir)])
    names = {getattr(d, "name", None) for d in parsed if isinstance(d, ExternTypeDecl)}
    assert "fixopaque_t" in names, f"expected fixopaque_t among {names}"
