"""Unit tests for declarative `|> sort` / `sortBy` (Ordering PRD Phase 1)."""

from flow.parser import Lexer, Parser, SortExpr, FindExpr, FunctionDecl, SortKey


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


# test_typecheck_and_codegen_i32_sort and test_codegen_struct_multi_key
# asserted that the emitted C mentions __flow_sort_ and the key field
# names. Sorted order is what those asserts stood for, and
# tests/lang/test_sort.flow checks it by running the sort.


# The C-text checks for float totalOrder comparators, plan selection
# (insertion, already_ordered, counting, bottom_up_merge, linear_scan,
# binary_search) and distinct sort helpers went with the Python C backend.
# Sorted results for every plan are checked by running tests/lang/test_sort.flow,
# test_sort_nan.flow and test_sort_plans.flow. The float struct key comparator
# is pinned by tests/cgen/sort_expr_float_key.


# ---------------------------------------------------------------------------
# Declarative search (issue #147)
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
