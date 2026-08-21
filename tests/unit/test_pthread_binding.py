"""The pthread types are the platform's own, not sizes guessed in Flow.

lib/stdlib/concurrent.flow used to model the pthread objects as byte arrays
with hand-written sizes. Two of the four guesses were wrong on macOS, and the
rwlock one was a live memory bug: pthread_rwlock_t is 200 bytes there and the
struct reserved 128, so pthread_rwlock_init wrote 72 bytes past the field. The
numbers differ per platform as well, so no fixed set is correct.

These tests pin the three compiler gaps that had to close before the real
header types could be used.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

from flow.c_header_parser import parse_c_header, resolve_c_imports
from flow.module_resolver import resolve_modules
from flow.type_checker import TypeChecker

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    not any(shutil.which(c) for c in ("cpp", "clang", "gcc")),
    reason="needs a C preprocessor",
)


FIXTURE = ROOT / "tests" / "fixtures" / "c_headers" / "glibc_style.h"


def imported_type_names(header: str, dirs: list) -> set:
    return {
        d.name
        for d in parse_c_header(header, dirs)
        if type(d).__name__ == "ExternTypeDecl"
    }


def test_the_pthread_types_are_recorded_on_the_host():
    """A dropped declaration made Flow forget the name existed.

    The header defines these names, so nothing needs emitting for them.
    Returning no declaration at all went further than that: using pthread_t as
    a field type then made the generator invent
    `typedef struct pthread_t pthread_t;` on top of the real one, which clang
    rejects as a redefinition with a different type.
    """
    names = imported_type_names("pthread.h", [])
    for want in ("pthread_t", "pthread_mutex_t", "pthread_cond_t"):
        assert want in names, f"{want} missing; got {len(names)} types"


def test_the_pthread_types_are_recorded_in_the_glibc_spelling():
    """glibc writes each pthread object as a union naming its type after the brace.

    macOS uses simple aliases, so a host-only test passes there and says
    nothing about Linux. The chunk splitter ended a declaration at the closing
    brace unless a semicolon followed immediately, which dropped
    `} pthread_mutex_t` into the next chunk and lost every one of these.
    """
    names = imported_type_names(str(FIXTURE), [str(FIXTURE.parent)])
    for want in ("pthread_t", "pthread_mutex_t", "pthread_cond_t", "pthread_rwlock_t"):
        assert want in names, f"{want} missing; got {sorted(names)}"


def test_an_imported_pointer_parameter_is_a_structured_pointer_type():
    """Imported params were named "ptr<X>" as one flat string.

    The Flow parser builds a pointer as name "ptr_X" with is_pointer set and
    an element type, so the flat spelling never unified and passing `&m.inner`
    to `pthread_mutex_lock` failed overload resolution against that function's
    own signature.
    """
    decls = parse_c_header("pthread.h", [])
    lock = next(
        d for d in decls
        if type(d).__name__ == "FunctionDecl" and d.name == "pthread_mutex_lock"
    )
    param = lock.parameters[0].type
    assert param.is_pointer
    assert param.name == "ptr_pthread_mutex_t"
    assert param.element_type.name == "pthread_mutex_t"


def test_a_field_of_an_opaque_c_type_may_be_left_out_of_a_literal(tmp_path):
    """Flow cannot write a pthread_mutex_t value, so requiring one is unsatisfiable.

    The field is omitted and zero-initialized, which is what C's `= {0}` does,
    and pthread_mutex_init overwrites it.
    """
    src = tmp_path / "m.flow"
    src.write_text(textwrap.dedent("""
        @cImport("pthread.h")

        struct Lock {
            inner: pthread_mutex_t,
            held: bool
        }

        function make() -> Lock {
            return Lock { held: false }
        }

        function main() -> i32 {
            let mut l: Lock = make()
            pthread_mutex_init(&l.inner, null)
            pthread_mutex_destroy(&l.inner)
            return 0
        }
    """))
    decls = resolve_c_imports(resolve_modules(str(src)), str(tmp_path))
    checker = TypeChecker()
    checker.strict = True
    assert checker.check(decls).errors == []


@pytest.mark.skipif(not shutil.which("cc"), reason="needs a C compiler")
def test_the_stdlib_locks_are_at_least_as_large_as_the_objects_they_hold(tmp_path):
    """The regression itself: RwLock reserved 128 bytes for a 200-byte object.

    Also covers mutex init/lock/unlock through the normal import -> C -> clang
    path, which is what issue #590 asks for.

    Driven through the `flow` driver so the runtime link set stays in one
    place rather than being restated here.
    """
    src = tmp_path / "sizes.flow"
    src.write_text(textwrap.dedent("""
        import concurrent

        function main() -> i32 {
            if sizeof<Mutex>() < sizeof<pthread_mutex_t>() { return 1 }
            if sizeof<CondVar>() < sizeof<pthread_cond_t>() { return 2 }
            if sizeof<RwLock>() < sizeof<pthread_rwlock_t>() { return 3 }
            let mut m: Mutex = mutex_new()
            mutex_lock(&m)
            if !mutex_is_locked(m) { return 4 }
            mutex_unlock(&m)
            mutex_destroy(&m)
            let mut rw: RwLock = rwlock_new()
            rwlock_wrlock(&rw)
            rwlock_unlock(&rw)
            rwlock_destroy(&rw)
            return 0
        }
    """))
    run = subprocess.run(
        ["./flow", "run", str(src)],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "FLOW_HOST": "python"},
    )
    assert "Exit code: 0" in run.stdout, (
        "a lock is smaller than the pthread object it holds\n"
        + run.stdout[-2000:] + run.stderr[-2000:]
    )
