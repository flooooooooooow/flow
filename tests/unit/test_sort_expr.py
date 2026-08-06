"""Unit tests for declarative `|> sort` / `sortBy` (Ordering PRD Phase 1)."""

from flow.parser import Lexer, Parser, SortExpr, FindExpr, FunctionDecl, SortKey
from flow.c_generator import flow_to_c


def _parse(src: str):
    return Parser(Lexer(src)).parse()


def _main_sorts(src: str):
    decls = _parse(src)
    fn = next(d for d in decls if isinstance(d, FunctionDecl) and d.name == "main")
    out = []

    def walk(n):
        if isinstance(n, SortExpr):
            out.append(n)
        if hasattr(n, "__dataclass_fields__"):
            for f in n.__dataclass_fields__:
                walk(getattr(n, f))
        elif isinstance(n, (list, tuple)):
            for x in n:
                walk(x)

    walk(fn)
    return decls, out


def test_parse_sort_bare():
    _, sorts = _main_sorts(
        """
        function main() -> i32 {
            let mut xs: array<i32, 3> = [3, 1, 2]
            xs |> sort
            return 0
        }
        """
    )
    assert len(sorts) == 1
    assert sorts[0].keys == []
    assert sorts[0].descending is False


def test_parse_sort_by_multi_key():
    _, sorts = _main_sorts(
        """
        struct Item { score: i32, name: i32 }
        function main() -> i32 {
            let mut items: array<Item, 1> = [Item { score: 1, name: 2 }]
            items |> sort by [desc .score, asc .name]
            return 0
        }
        """
    )
    assert [(k.field, k.descending) for k in sorts[0].keys] == [
        ("score", True),
        ("name", False),
    ]


def test_parse_sortBy_alias_and_entropy():
    _, sorts = _main_sorts(
        """
        struct Item { score: i32 }
        function main() -> i32 {
            let mut items: array<Item, 1> = [Item { score: 1 }]
            items |> sortBy [asc .score] stable with entropy(seed: 7) parallel
            return 0
        }
        """
    )
    s = sorts[0]
    assert s.keys[0] == SortKey(field="score", descending=False)
    assert s.stable is True
    assert s.entropy == "7"
    assert "parallel" in s.policies


def test_typecheck_and_codegen_i32_sort():
    src = """
    function main() -> i32 {
        let mut xs: array<i32, 4> = [4, 2, 3, 1]
        xs |> sort
        return xs[0]
    }
    """
    c = flow_to_c(_parse(src))
    assert "__flow_sort_" in c
    assert "int32_t *a" in c


def test_codegen_struct_multi_key():
    src = """
    struct P { score: i32, name: i32 }
    function main() -> i32 {
        let mut ps: array<P, 2> = [
            P { score: 1, name: 2 },
            P { score: 2, name: 1 }
        ]
        ps |> sortBy [desc .score, asc .name]
        return ps[0].score
    }
    """
    c = flow_to_c(_parse(src))
    assert ".score" in c
    assert ".name" in c


# ---------------------------------------------------------------------------
# Float total order (issue #144)
# ---------------------------------------------------------------------------


def _scrambled_sort(elem: str, n: int, policy: str = "") -> str:
    """C for a sort whose input the compiler cannot reason about."""
    src = """
    function scramble(xs: ptr<%s>, n: i32) -> i32 {
        return n
    }
    function main() -> i32 {
        let mut xs: array<%s, %d> = [%s]
        scramble(xs, %d)
        xs |> sort %s
        return 0
    }
    """ % (
        elem,
        elem,
        n,
        ", ".join("0.0" if elem.startswith("f") else "0" for _ in range(n)),
        n,
        policy,
    )
    return flow_to_c(_parse(src))


def test_float_sort_uses_the_total_order_comparator():
    c = _scrambled_sort("f64", 8)
    # Not raw `<`: NaN makes that comparator intransitive.
    assert "__flow_ord_cmp_f64" in c
    assert "__flow_ord_key_f64" in c


def test_f32_gets_its_own_width():
    c = _scrambled_sort("f32", 8)
    assert "__flow_ord_cmp_f32" in c
    assert "uint32_t" in c


def test_integer_sort_keeps_plain_comparison():
    c = _scrambled_sort("i32", 8)
    assert "__flow_ord_cmp" not in c


def test_total_order_helper_is_emitted_once_per_width():
    src = """
    function scramble(xs: ptr<f64>, n: i32) -> i32 {
        return n
    }
    function main() -> i32 {
        let mut a: array<f64, 8> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        let mut b: array<f64, 8> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        scramble(a, 8)
        scramble(b, 8)
        a |> sort
        b |> sort descending
        return 0
    }
    """
    c = flow_to_c(_parse(src))
    assert c.count("static inline int32_t __flow_ord_cmp_f64") == 1


def test_float_struct_key_also_uses_the_total_order():
    src = """
    struct P { t: f64 }
    function scramble(xs: ptr<P>, n: i32) -> i32 {
        return n
    }
    function main() -> i32 {
        let mut ps: array<P, 8> = [
            P { t: 0.0 }, P { t: 0.0 }, P { t: 0.0 }, P { t: 0.0 },
            P { t: 0.0 }, P { t: 0.0 }, P { t: 0.0 }, P { t: 0.0 }
        ]
        scramble(ps, 8)
        ps |> sortBy [asc .t]
        return 0
    }
    """
    assert "__flow_ord_cmp_f64" in flow_to_c(_parse(src))


# ---------------------------------------------------------------------------
# Plan selection through the C generator (issues #145, #146, #147)
# ---------------------------------------------------------------------------


def _selections(src: str):
    flow_to_c(_parse(src))
    return list(getattr(flow_to_c, "last_selections", []))


def test_selection_records_reach_the_caller():
    sels = _selections(
        """
        function main() -> i32 {
            let mut xs: array<i32, 4> = [4, 2, 3, 1]
            xs |> sort
            return xs[0]
        }
        """
    )
    assert len(sels) == 1
    assert sels[0].construct == "sort"
    assert sels[0].location.endswith("in main()")
    assert sels[0].chosen == "insertion"


def test_a_proven_sorted_array_skips_the_sort():
    src = """
    function main() -> i32 {
        let mut xs: array<i32, 4> = [1, 2, 3, 4]
        xs |> sort
        return xs[0]
    }
    """
    assert _selections(src)[0].chosen == "already_ordered"
    assert "already in this order" in flow_to_c(_parse(src))


def test_u8_elements_reach_the_counting_plan():
    n = 1024
    src = """
    function scramble(xs: ptr<u8>, n: i32) -> i32 {
        return n
    }
    function main() -> i32 {
        let mut xs: array<u8, %d> = [%s]
        scramble(xs, %d)
        xs |> sort
        return 0
    }
    """ % (n, ", ".join("0" for _ in range(n)), n)
    sels = _selections(src)
    assert sels[0].chosen == "counting"
    assert sels[0].facts.get("key_range") == [0, 255]


def test_the_general_policy_pins_the_general_plan():
    src = """
    function main() -> i32 {
        let mut xs: array<i32, 4> = [1, 2, 3, 4]
        xs |> sort general
        return xs[0]
    }
    """
    assert _selections(src)[0].chosen == "bottom_up_merge"


def test_each_plan_emits_a_distinct_helper():
    src = """
    function scramble(xs: ptr<i32>, n: i32) -> i32 {
        return n
    }
    function main() -> i32 {
        let mut a: array<i32, 1024> = [%s]
        let mut b: array<i32, 1024> = [%s]
        scramble(a, 1024)
        scramble(b, 1024)
        a |> sort adaptive
        b |> sort general
        return 0
    }
    """ % (
        ", ".join("0" for _ in range(1024)),
        ", ".join("0" for _ in range(1024)),
    )
    c = flow_to_c(_parse(src))
    assert c.count("static void __flow_sort_") == 2


# ---------------------------------------------------------------------------
# Declarative search (issue #147: a second construct on the same selector)
# ---------------------------------------------------------------------------


def test_parse_find_pipeline():
    decls, _ = _main_sorts(
        """
        function main() -> i32 {
            let mut xs: array<i32, 3> = [3, 1, 2]
            return xs |> find(2)
        }
        """
    )
    fn = next(d for d in decls if isinstance(d, FunctionDecl) and d.name == "main")
    found = []

    def walk(n):
        if isinstance(n, FindExpr):
            found.append(n)
        if hasattr(n, "__dataclass_fields__"):
            for f in n.__dataclass_fields__:
                walk(getattr(n, f))
        elif isinstance(n, (list, tuple)):
            for x in n:
                walk(x)

    walk(fn)
    assert len(found) == 1
    assert found[0].line > 0


def test_find_outside_a_pipeline_is_still_a_normal_call():
    src = """
    function find(a: i32) -> i32 {
        return a
    }
    function main() -> i32 {
        return find(3)
    }
    """
    c = flow_to_c(_parse(src))
    assert "__flow_find_" not in c


def test_unsorted_find_scans_linearly():
    src = """
    function main() -> i32 {
        let mut xs: array<i32, 8> = [5, 2, 9, 1, 7, 3, 8, 4]
        return xs |> find(9)
    }
    """
    sels = _selections(src)
    assert sels[0].construct == "search"
    assert sels[0].chosen == "linear_scan"


def test_a_sort_flips_the_next_find_to_binary_search():
    src = """
    function main() -> i32 {
        let mut xs: array<i32, 8> = [5, 2, 9, 1, 7, 3, 8, 4]
        xs |> sort
        return xs |> find(9)
    }
    """
    sels = _selections(src)
    assert [s.chosen for s in sels] == ["insertion", "binary_search"]
    assert "lo + (hi - lo) / 2" in flow_to_c(_parse(src))


def test_float_find_uses_the_total_order_too():
    src = """
    function main() -> i32 {
        let mut xs: array<f64, 4> = [1.0, 2.0, 3.0, 4.0]
        return xs |> find(3.0)
    }
    """
    assert "__flow_ord_cmp_f64" in flow_to_c(_parse(src))
