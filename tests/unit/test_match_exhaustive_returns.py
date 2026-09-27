"""An exhaustive match emits a total if/else chain, so C can see it returns.

A match covering every variant, where every arm returns, used to lower with
the last arm as `else if`. C cannot tell such a chain is total, so clang
reported every such function as falling off the end under -Wreturn-type. See
issue #620.

The dispatch check (the last arm still runs for its own variant and no
other) lives in tests/lang/test_enum_match_arms.flow.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    not shutil.which("clang"), reason="needs clang for -Werror=return-type"
)

SOURCE = """
enum Kind { A, B, C }

function pick(k: Kind) -> f64 {
    match k.tag {
        Kind_A => { return 1.0 }
        Kind_B => { return 2.0 }
        Kind_C => { return 3.0 }
    }
}

extern { function printf(fmt: string, a: f64) -> i32 }

function main() -> i32 {
    printf("%.1f\\n", pick(Kind { tag: Kind_A }))
    printf("%.1f\\n", pick(Kind { tag: Kind_B }))
    printf("%.1f\\n", pick(Kind { tag: Kind_C }))
    return 0
}
"""


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("match")
    src = tmp / "m.flow"
    src.write_text(textwrap.dedent(SOURCE))
    run = subprocess.run(
        ["./flow", "run", str(src)],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "FLOW_HOST": "python"},
    )
    return run, (ROOT / "build" / "m.c").read_text()


def test_clang_sees_the_chain_as_total(built, tmp_path):
    _, generated = built
    c_file = tmp_path / "m.c"
    c_file.write_text(generated)
    compiled = subprocess.run(
        ["clang", "-fsyntax-only", "-Werror=return-type", str(c_file)],
        capture_output=True, text=True,
    )
    assert compiled.returncode == 0, compiled.stderr
