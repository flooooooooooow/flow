"""
Explicit casts between byte pointers and `string`.

`string` is a `char*` in the C backend, so `ptr<i8>`, `ptr<u8>` and
`ptr<void>` share its representation. FFI code needs to move between the
two: hand a malloc'd buffer to `snprintf` and read it back as a string, or
pass a string to a C function declared over raw bytes. Casts between a
byte pointer and `string` are therefore legal; casts between a wider
pointer and `string` are not, since the element sizes disagree.
"""

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def cast_errors(code: str) -> list[str]:
    checker = TypeChecker()
    checker.strict = True
    result = checker.check(parse_flow_code(code))
    return [e for e in result.errors if "Cannot cast" in e]


PRELUDE = """
extern {
    function malloc(size: i64) -> ptr<void>
    function snprintf(buf: ptr<i8>, n: i64, fmt: string, v: i32) -> i32
}
"""


def test_byte_pointer_casts_to_string():
    code = PRELUDE + """
function render(n: i32) -> string {
    let buf: ptr<i8> = malloc(48) as ptr<i8>
    let _w: i32 = snprintf(buf, 48, "%d", n)
    return buf as string
}
"""
    assert cast_errors(code) == []


def test_string_casts_to_byte_pointer():
    code = """
function first_byte(s: string) -> i32 {
    let bytes: ptr<u8> = s as ptr<u8>
    return bytes[0] as i32
}
"""
    assert cast_errors(code) == []


def test_void_pointer_casts_to_string():
    code = PRELUDE + """
function grab() -> string {
    let raw: ptr<void> = malloc(16)
    return raw as string
}
"""
    assert cast_errors(code) == []


def test_wide_pointer_does_not_cast_to_string():
    code = """
function bad(p: ptr<i32>) -> string {
    return p as string
}
"""
    assert cast_errors(code) != []
