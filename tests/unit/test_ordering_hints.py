"""Unit tests for the ordering-provenance pass (issue #145).

The pass is only useful if it is never wrong. A missed hint costs a general
plan; a wrong hint skips a sort that was needed. These tests spend most of
their attention on the second kind.
"""

from flow.ordering_hints import analyze_function, annotate_ordering_hints
from flow.parser import FunctionDecl, Lexer, Parser


def facts(src: str, index: int = 0):
    decls = Parser(Lexer(src)).parse()
    fns = [d for d in decls if isinstance(d, FunctionDecl)]
    annotate_ordering_hints(fns)
    main = next(f for f in fns if f.name == "main")
    return analyze_function(main).sites[index][1]


def body(inner: str) -> str:
    return "function main() -> i32 {\n%s\n    return 0\n}\n" % inner


def test_ascending_literal_is_recognised():
    f = facts(body("""
    let mut xs: array<i32, 4> = [1, 2, 3, 4]
    xs |> sort
"""))
    assert f.order == "asc_strict"
    assert f.key_range == (1, 4)


def test_descending_literal_is_recognised():
    f = facts(body("""
    let mut xs: array<i32, 4> = [9, 5, 2, 1]
    xs |> sort
"""))
    assert f.order == "desc_strict"


def test_repeated_values_are_ordered_but_not_strictly():
    f = facts(body("""
    let mut xs: array<i32, 4> = [1, 2, 2, 3]
    xs |> sort
"""))
    assert f.order == "asc"


def test_unordered_literal_yields_nothing():
    f = facts(body("""
    let mut xs: array<i32, 4> = [3, 1, 4, 2]
    xs |> sort
"""))
    assert f.order == "unknown"
    assert f.key_range == (1, 4)


def test_short_initializer_says_nothing_about_the_tail():
    # `array<i32, 64> = [1, 2]` zero-fills, so the literal covers a prefix.
    f = facts(body("""
    let mut xs: array<i32, 64> = [1, 2]
    xs |> sort
"""))
    assert f.order == "unknown"
    assert f.key_range is None


def test_negative_literals_keep_their_sign_in_the_range():
    f = facts(body("""
    let mut xs: array<i32, 3> = [-5, 0, 7]
    xs |> sort
"""))
    assert f.key_range == (-5, 7)


def test_float_literals_give_order_but_no_integer_range():
    f = facts(body("""
    let mut xs: array<f64, 3> = [1.0, 2.0, 3.0]
    xs |> sort
"""))
    assert f.order == "asc_strict"
    assert f.key_range is None


def test_non_literal_elements_yield_nothing():
    src = """
function pick() -> i32 {
    return 3
}

function main() -> i32 {
    let mut xs: array<i32, 3> = [1, pick(), 3]
    xs |> sort
    return 0
}
"""
    assert facts(src).order == "unknown"


def test_a_sort_makes_the_array_ascending_for_the_next_site():
    f = facts(body("""
    let mut xs: array<i32, 8> = [8, 7, 6, 5, 4, 3, 2, 1]
    xs |> sort
    let hit: i32 = xs |> find(3)
"""), index=1)
    assert f.order == "asc"


def test_a_descending_sort_records_descending():
    f = facts(body("""
    let mut xs: array<i32, 8> = [1, 2, 3, 4, 5, 6, 7, 8]
    xs |> sort descending
    let hit: i32 = xs |> find(3)
"""), index=1)
    assert f.order == "desc"


def test_sort_unique_leaves_a_strict_order():
    f = facts(body("""
    let mut xs: array<i32, 4> = [4, 4, 2, 1]
    xs |> sort unique
    let hit: i32 = xs |> find(2)
"""), index=1)
    assert f.order == "asc_strict"


def test_a_multi_key_sort_says_nothing_about_whole_element_order():
    src = """
struct P { a: i32, b: i32 }

function main() -> i32 {
    let mut xs: array<P, 2> = [P { a: 2, b: 1 }, P { a: 1, b: 2 }]
    xs |> sortBy [asc .a]
    xs |> sort by [asc .b]
    return 0
}
"""
    assert facts(src, index=1).order == "unknown"


def test_an_element_write_invalidates_the_hint():
    f = facts(body("""
    let mut xs: array<i32, 8> = [1, 2, 3, 4, 5, 6, 7, 8]
    xs[0] = 99
    xs |> sort
"""))
    assert f.order == "unknown"


def test_passing_the_array_to_a_call_invalidates_the_hint():
    src = """
function shuffle(xs: ptr<i32>, n: i32) -> i32 {
    return n
}

function main() -> i32 {
    let mut xs: array<i32, 8> = [1, 2, 3, 4, 5, 6, 7, 8]
    shuffle(xs, 8)
    xs |> sort
    return 0
}
"""
    assert facts(src).order == "unknown"


def test_a_write_inside_a_loop_invalidates_the_hint():
    f = facts(body("""
    let mut xs: array<i32, 8> = [1, 2, 3, 4, 5, 6, 7, 8]
    for i in 0 to 8 {
        xs[i] = 8 - i
    }
    xs |> sort
"""))
    assert f.order == "unknown"


def test_a_write_inside_a_conditional_invalidates_the_hint():
    f = facts(body("""
    let mut xs: array<i32, 8> = [1, 2, 3, 4, 5, 6, 7, 8]
    let flag: i32 = 1
    if flag > 0 {
        xs[3] = 0
    }
    xs |> sort
"""))
    assert f.order == "unknown"


def test_a_site_inside_a_loop_gets_no_hint():
    # The array is sorted on the first iteration but scrambled by the body,
    # so a hint taken from the literal would be wrong on iteration two.
    f = facts(body("""
    let mut xs: array<i32, 8> = [1, 2, 3, 4, 5, 6, 7, 8]
    for i in 0 to 3 {
        xs |> sort
        xs[0] = 99
    }
"""))
    assert f.order == "unknown"


def test_reassigning_the_whole_array_invalidates_the_hint():
    f = facts(body("""
    let mut xs: array<i32, 4> = [1, 2, 3, 4]
    let mut ys: array<i32, 4> = [4, 3, 2, 1]
    xs = ys
    xs |> sort
"""))
    assert f.order == "unknown"


def test_hints_are_written_onto_the_ast_nodes():
    decls = Parser(Lexer(body("""
    let mut xs: array<i32, 4> = [1, 2, 3, 4]
    xs |> sort
"""))).parse()
    fns = [d for d in decls if isinstance(d, FunctionDecl)]
    annotate_ordering_hints(fns)
    site = analyze_function(fns[0]).sites[0][0]
    assert site.hint_input_order == "asc_strict"
    assert site.hint_key_range == [1, 4]
