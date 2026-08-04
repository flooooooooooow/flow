"""Pin fixed fuzz crashes as permanent SyntaxError regressions.

Mirrors tests/fuzz/test_crash_regressions.py but lives in the main unit
suite so `./flow test-python` always exercises them.
"""

from pathlib import Path

import pytest

from flow.parser import parse_flow_code


CRASH_DIR = Path(__file__).resolve().parents[1] / "fuzz" / "crashes"


@pytest.mark.parametrize(
    "name",
    [
        "parse-valueerror-parser-parse-type.flow",
        "parse-recursionerror-parser-parse-expression-without-assign.flow",
    ],
)
def test_known_fuzz_crash_is_clean_syntax_error(name: str):
    path = CRASH_DIR / name
    assert path.is_file(), path
    src = path.read_text()
    with pytest.raises(SyntaxError):
        parse_flow_code(src)
