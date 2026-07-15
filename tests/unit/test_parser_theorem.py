"""Parser support for verification syntax."""

from flow.parser import (
    AssumeStmt,
    IfStatement,
    Lexer,
    Parser,
    TheoremDecl,
    ThereforeStmt,
    TokenType,
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