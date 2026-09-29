"""Debug-info line directives in generated C.

The unhandled-effect checks that used to live here (FLOW_STRICT_EFFECTS and
--strict-effects) are covered for flowc by compiler/scripts/parity_effects.sh
(fixtures strict_unhandled, strict_row_call and runtime_strict_abort).
"""

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def test_debug_info_emits_statement_line_directives():
    code = """
function main() -> i32 {
    let x: i32 = 1
    return x
}
"""
    c = flow_to_c(
        parse_flow_code(code),
        source_file="/tmp/demo.flow",
        debug_info=True,
    )
    assert '#line ' in c
    assert "/tmp/demo.flow" in c
