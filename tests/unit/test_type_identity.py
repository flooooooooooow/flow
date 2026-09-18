"""Stable compiler-derived type identity for user structs (#775).

Each user `struct` gets a deterministic 64-bit type key emitted into the C
backend as `<Name>_TYPE_KEY`. The key must be the same for the same public
definition across compilations, and different for different definitions, so a
library never has to assign a `type_key` by hand.
"""

import re

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c, derive_type_key


_KEY_RE = re.compile(r"#define (\w+)_TYPE_KEY (0x[0-9A-F]{16}ULL)")


def _keys(source: str) -> dict:
    """Map struct name -> emitted type-key literal from generated C."""
    c_code = flow_to_c(parse_flow_code(source))
    return {name: lit for name, lit in _KEY_RE.findall(c_code)}


def test_type_key_is_emitted_for_a_user_struct():
    source = """
struct Point { x: f32, y: f32 }
function main() -> i32 { return 0 }
"""
    keys = _keys(source)
    assert "Point" in keys
    assert keys["Point"].endswith("ULL")


def test_type_key_is_deterministic_across_generations():
    source = """
struct Point { x: f32, y: f32 }
struct Sample { left: f32, right: f32, frame: i64 }
function main() -> i32 { return 0 }
"""
    first = _keys(source)
    second = _keys(source)
    assert first == second
    assert first["Point"] == second["Point"]
    assert first["Sample"] == second["Sample"]


def test_distinct_types_get_distinct_keys():
    source = """
struct Point { x: f32, y: f32 }
struct Point3 { x: f32, y: f32, z: f32 }
struct Named { x: f32, y: f32, tag: i32 }
function main() -> i32 { return 0 }
"""
    keys = _keys(source)
    values = [keys[n] for n in ("Point", "Point3", "Named")]
    assert len(set(values)) == len(values)


def test_field_order_is_part_of_identity():
    a = _keys(
        """
struct Rec { x: f32, y: f32 }
function main() -> i32 { return 0 }
"""
    )
    b = _keys(
        """
struct Rec { y: f32, x: f32 }
function main() -> i32 { return 0 }
"""
    )
    assert a["Rec"] != b["Rec"]


def test_field_type_is_part_of_identity():
    a = _keys(
        """
struct Rec { x: f32, y: f32 }
function main() -> i32 { return 0 }
"""
    )
    b = _keys(
        """
struct Rec { x: f32, y: i32 }
function main() -> i32 { return 0 }
"""
    )
    assert a["Rec"] != b["Rec"]


def test_key_is_independent_of_declaration_order_of_other_structs():
    a = _keys(
        """
struct Point { x: f32, y: f32 }
struct Other { a: i32 }
function main() -> i32 { return 0 }
"""
    )
    b = _keys(
        """
struct Other { a: i32 }
struct Point { x: f32, y: f32 }
function main() -> i32 { return 0 }
"""
    )
    assert a["Point"] == b["Point"]


def test_derive_type_key_matches_emitted_key():
    """The public helper agrees with what the C backend emits."""
    from flow.parser import StructDecl

    source = """
struct Point { x: f32, y: f32 }
function main() -> i32 { return 0 }
"""
    decls = parse_flow_code(source)
    struct = next(d for d in decls if isinstance(d, StructDecl) and d.name == "Point")
    layout = [(f.name, f.type) for f in struct.fields]
    key = derive_type_key("Point", layout)

    emitted = _keys(source)["Point"]
    assert emitted == f"0x{key:016X}ULL"
