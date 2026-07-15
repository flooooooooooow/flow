"""Tests for proof artifact generation."""

import os

from flow.proof_document import (
    parse_proof_file,
    render_english,
    render_latex,
    write_proof_artifacts,
    flow_expr_to_latex,
)


FIXTURE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "examples",
    "verify",
    "math",
    "derived",
    "Nat-plus-zero-right.flow",
)


class TestProofDocument:
    def test_parse_theorem_metadata(self):
        doc = parse_proof_file(FIXTURE)
        assert doc.module.startswith("examples.verify")
        assert len(doc.theorems) == 1
        thm = doc.theorems[0]
        assert "zero is the right identity" in thm.claim_path
        assert "zero on the right" in thm.meta.means.lower()
        assert thm.meta.tier == "derived"

    def test_english_contains_numbered_theorem(self):
        doc = parse_proof_file(FIXTURE)
        doc.theorems[0].number = 3
        text = render_english(doc)
        assert "Derived fact 3" in text
        assert "induction" in text.lower()
        lower = text.lower()
        assert "we invoke" in lower or "inductive boundary" in lower
        assert "from " in lower and ("④" in text or "⑤" in text)
        assert "we can deduce" in lower or "this implies" in lower
        assert "Hence proven." in text
        assert "Coordinate." in text
        assert "Derived fact" in text
        assert "**Trace.**" in text

    def test_latex_has_numbered_equations(self):
        doc = parse_proof_file(FIXTURE)
        doc.theorems[0].number = 3
        tex = render_latex(doc)
        assert r"\textbf{1.}" in tex
        assert r"\label{thm:Nat-addition-zero_is_the_right_identity}" in tex
        assert r"\begin{tabular}" in tex
        assert r"Goal." in tex
        assert r"\end{document}" in tex
        assert r"natural numbers \cdot addition" in tex
        assert r"\textperiodcentered" not in tex or r"\cdot" in tex

    def test_latex_shows_substitution_annotations(self):
        doc = parse_proof_file(FIXTURE)
        tex = render_latex(doc)
        assert "instantiated" in tex
        assert "0 + 0 = 0" in tex or "0+0=0" in tex.replace(" ", "")

    def test_flow_expr_to_latex(self):
        assert "succ" in flow_expr_to_latex("n + succ(m) == succ(n + m)")
        assert "=" in flow_expr_to_latex("0 + m == m")

    def test_write_artifacts(self, tmp_path):
        import shutil

        dst = tmp_path / "Nat-plus-zero-right.flow"
        shutil.copy(FIXTURE, dst)
        md, tex, _diagrams = write_proof_artifacts(str(dst))
        assert os.path.exists(md)
        assert os.path.exists(tex)
        assert md.endswith(".proof.md")
        assert tex.endswith(".proof.tex")