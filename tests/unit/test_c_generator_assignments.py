from flow.c_generator import flow_to_c
from flow.parser import parse_flow_code


def test_nested_assignment_is_lowered_as_a_c_expression():
    source = """
function main() -> i32 {
    let mut value: i32 = 0
    let mut other: i32 = 0
    value = other = 1
    return value + other
}
"""

    c_code = flow_to_c(parse_flow_code(source))

    assert "value = (other = 1);" in c_code
