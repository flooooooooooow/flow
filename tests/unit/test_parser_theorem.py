"""Parser support for verification syntax."""

from flow.parser import (
    AssumeStmt,
    BinaryOperation,
    ForStatement,
    FunctionCall,
    FunctionDecl,
    IfStatement,
    Lexer,
    Parser,
    TheoremDecl,
    ThereforeStmt,
    TokenType,
    VarDecl,
)


def _parse(source: str):
    return Parser(Lexer(source), source=source).parse()


class TestTheoremParser:
    def test_claim_path_token(self):
        lexer = Lexer("theorem Nat/+.zero-left(m: Nat) { }")
        types = []
        while True:
            tok = lexer.next_token()
            if tok.type == TokenType.EOF:
                break
            types.append(tok.type)
        assert TokenType.CLAIM_PATH in types

    def test_parse_definition_theorem(self):
        decls = _parse(
            """
            theorem «Nat» «addition» «zero is the left identity» (m: Nat) {
                therefore 0 + m == m
            }
            """
        )
        assert len(decls) == 1
        thm = decls[0]
        assert isinstance(thm, TheoremDecl)
        assert "zero is the left identity" in thm.claim_path
        assert len(thm.body.statements) == 1
        assert isinstance(thm.body.statements[0], ThereforeStmt)

    def test_parse_inductive_proof(self):
        decls = _parse(
            """
            theorem Nat/+.zero-right(n: Nat) {
                if n == 0 {
                    assume Nat/+.zero-left(0)
                    therefore 0 + 0 == 0
                } else {
                    assume Nat/+.zero-right(k)
                    therefore n + 0 == n
                }
            }
            """
        )
        thm = decls[0]
        assert isinstance(thm, TheoremDecl)
        inner = thm.body.statements[0]
        assert isinstance(inner, IfStatement)
        assert isinstance(inner.then_block.statements[0], AssumeStmt)
        assert inner.then_block.statements[0].claim_path == "Nat/+.zero-left"

    def test_export_claim_paths(self):
        decls = _parse("export Nat/+.zero-left, Nat/+.succ-right")
        assert len(decls) == 1
        assert decls[0].symbols == ["Nat/+.zero-left", "Nat/+.succ-right"]


class TestEnglishLogicalOperators:
    """English `and`/`or` are soft keywords: infix == &&/||, also usable as names."""

    def test_infix_and_or_normalize_to_symbolic(self):
        decls = _parse(
            """
            function f(a: bool, b: bool, c: bool) -> bool {
                return a and b or c
            }
            """
        )
        fn = decls[0]
        assert isinstance(fn, FunctionDecl)
        ret = fn.body.statements[0]
        expr = ret.value
        # a and b or c  →  (a && b) || c
        assert isinstance(expr, BinaryOperation)
        assert expr.operator == "||"
        assert isinstance(expr.left, BinaryOperation)
        assert expr.left.operator == "&&"

    def test_and_or_as_function_names_and_calls(self):
        decls = _parse(
            """
            function and(a: i32, b: i32) -> i32 { return a }
            function or(a: i32, b: i32) -> i32 { return a }
            function f() -> i32 {
                let x: i32 = and(1, 0)
                let y: i32 = or(1, 0)
                return x
            }
            """
        )
        assert [d.name for d in decls if isinstance(d, FunctionDecl)] == [
            "and",
            "or",
            "f",
        ]
        f = decls[2]
        x = f.body.statements[0]
        assert isinstance(x, VarDecl)
        assert isinstance(x.initializer, FunctionCall)
        assert x.initializer.name == "and"

    def test_therefore_english_and_by_exhaustive(self):
        decls = _parse(
            """
            theorem FullAdder/out.correct(A: i32, B: i32, Cin: i32) {
                therefore A == B and Cin == 0 by exhaustive
            }
            """
        )
        thm = decls[0]
        assert isinstance(thm, TheoremDecl)
        th = thm.body.statements[0]
        assert isinstance(th, ThereforeStmt)
        assert th.method == "exhaustive"
        assert isinstance(th.expression, BinaryOperation)
        assert th.expression.operator == "&&"

    def test_step_is_contextual_for_range_keyword(self):
        decls = _parse(
            """
            function f() -> i32 {
                let step: i32 = 1
                let mut s: i32 = 0
                for i in 0 to 10 step 2 {
                    s = s + i
                }
                return s + step
            }
            """
        )
        fn = decls[0]
        assert isinstance(fn.body.statements[0], VarDecl)
        assert fn.body.statements[0].name == "step"
        loop = fn.body.statements[2]
        assert isinstance(loop, ForStatement)
        assert loop.step is not None
