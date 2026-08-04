"""Unit tests for declarative `|> sort` / `sortBy` (Ordering PRD Phase 1)."""

from flow.parser import Lexer, Parser, SortExpr, FunctionDecl, SortKey
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
