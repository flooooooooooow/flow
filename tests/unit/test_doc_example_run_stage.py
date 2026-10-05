"""The doc-example gate can run programs, not only compile them.

Compiling proves an example is well-formed. It does not prove it works: a
`defer` that freed memory before the return value was read compiled cleanly
and returned garbage (#594), and returning a fixed-size array handed back a
pointer into a dead frame (#573). Both were found by running the examples.

A doc example may return a non-zero status on purpose, so only a crash or a
hang counts as a failure.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_doc_examples as C  # noqa: E402
from docs_blocks import Block  # noqa: E402

pytestmark = pytest.mark.skipif(
    shutil.which("clang") is None, reason="the run stage needs clang"
)


def _result(body: str) -> C.Result:
    block = Block(path="d.md", line=1, info="flow", lang="flow", code="x")
    result = C.Result(block, "verified")
    result.csource = "#include <stdint.h>\n" + body
    return result


def test_a_segfault_is_a_failure():
    crashing = _result("int32_t main(void) { int *p = 0; *p = 1; return 0; }\n")
    C._batch_execute([crashing], timeout=5)
    assert crashing.status == "unverified"
    assert crashing.stage == "run"
    assert "SIGSEGV" in crashing.detail


def test_a_hang_is_a_failure():
    looping = _result("int32_t main(void) { while (1) {} return 0; }\n")
    C._batch_execute([looping], timeout=1)
    assert looping.status == "unverified"
    assert looping.stage == "run"
    assert "did not finish" in looping.detail


def test_a_deliberate_non_zero_exit_is_not_a_failure():
    """docs/book/01-a-complete-program.md returns 2 to show a failure path."""
    deliberate = _result("int32_t main(void) { return 2; }\n")
    C._batch_execute([deliberate], timeout=5)
    assert deliberate.status == "verified"


def test_a_clean_program_stays_verified():
    clean = _result("int32_t main(void) { return 0; }\n")
    assert C._batch_execute([clean], timeout=5) == 1
    assert clean.status == "verified"


def test_a_block_without_a_main_is_not_run():
    fragment = _result("int32_t helper(void) { return 0; }\n")
    assert C._batch_execute([fragment], timeout=5) == 0
    assert fragment.status == "verified"
