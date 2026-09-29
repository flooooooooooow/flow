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

import pytest

from flow.c_header_parser import _preprocess_header, parse_c_header, resolve_c_imports
from flow.parser import CImportDecl, ExternTypeDecl


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
    """resolve_c_imports must mark every declaration, functions and the rest."""
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


# The C-output checks (no typedef for an imported type, the output builds
# against the header, a plain `extern type` still gets its typedef) are now
# tests/cgen/c_import_no_redeclare.flow and
# tests/cgen/c_import_no_redeclare_extern_type.flow.


def test_parse_returns_extern_type_for_named_struct_typedef(header_dir):
    """`typedef struct _fixopaque_s fixopaque_t;` should yield an ExternTypeDecl."""
    parsed = parse_c_header("fixture.h", [str(header_dir)])
    names = {getattr(d, "name", None) for d in parsed if isinstance(d, ExternTypeDecl)}
    assert "fixopaque_t" in names, f"expected fixopaque_t among {names}"
