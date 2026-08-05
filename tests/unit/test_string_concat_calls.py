"""
String concatenation must not truncate string-returning function calls.

`_is_string_expr` historically only recognized literals, variables, fields,
and `+` chains. A call like `area_pair_json(...)` returning `string` was
treated as a non-string operand and forced through `_gen_stringify_expr`,
which copies into a 64-byte stack buffer via `snprintf("%s", ...)`. Anything
longer was silently truncated — the repo-stats JSON emitter lost digits and
closing braces that way (`"lines": 35913` became `"lines": 3591`).
"""

import re

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


LONG_HELPER = """
function long_piece() -> string {
    return "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!!"
}

function main() -> i32 {
    let out: string = "[" + long_piece() + "]"
    print(out)
    return 0
}
"""


def generate_c(code: str) -> str:
    return flow_to_c(parse_flow_code(code))


def test_string_returning_call_is_not_forced_through_snprintf_buffer():
    c = generate_c(LONG_HELPER)
    # Before the fix, the call was wrapped as:
    #   snprintf(buf, 64, "%s", long_piece());
    # which truncates anything over 63 bytes. The call must go straight
    # into flow_strcat instead.
    assert "flow_strcat" in c
    assert "long_piece" in c
    wrapped = re.findall(
        r'snprintf\s*\([^;]*long_piece\s*\(\s*\)[^;]*\)',
        c,
    )
    assert wrapped == [], f"long_piece result still snprintf-wrapped: {wrapped}"


def test_generated_c_keeps_full_helper_return_in_strcat():
    c = generate_c(LONG_HELPER)
    assert re.search(r'flow_strcat\([^)]*long_piece\s*\(\s*\)', c)
