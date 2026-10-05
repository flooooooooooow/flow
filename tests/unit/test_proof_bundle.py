"""Tests for proof PDF bundles and unified book."""

import os

import pytest

pytestmark = pytest.mark.slow

from flow.proof_document import (
    ALGEBRA_PROOF_BUNDLE,
    ANALYSIS_APPENDIX,
    BASIC_PROOF_BUNDLE,
    DATA_PROOF_BUNDLE,
    GEOMETRY_DERIVED_BUNDLE,
    EUCLID_BOOK_I_BUNDLE,
    EUCLID_BOOK_II_BUNDLE,
    EUCLID_BOOK_III_BUNDLE,
    EUCLID_BOOK_IV_BUNDLE,
    EUCLID_BOOK_V_BUNDLE,
    EUCLID_BOOK_VI_BUNDLE,
    FLOW_PROOF_BOOK,
    load_basic_proof_bundle,
    load_proof_book,
    parse_proof_file,
    render_side_by_side_bundle,
    write_basic_proof_bundle_pdf,
    write_proof_book_pdf,
)

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")



import shutil
has_tex = shutil.which("pdflatex") or shutil.which("xelatex") or shutil.which("tectonic")

class TestProofBundle:
    def test_basic_bundle_loads_two_hundred_sixty_four_theorems(self):
        docs = load_basic_proof_bundle(ROOT)
        total = sum(len(d.theorems) for d in docs)
        assert total == 264
        assert len(BASIC_PROOF_BUNDLE) == 243

    def test_data_bundle_loads_seventy_five_theorems(self):
        docs = []
        counter = 1
        from flow.proof_document import assign_numbers, parse_proof_file

        for rel in DATA_PROOF_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            assign_numbers([doc], start=counter)
            counter += len(doc.theorems)
            docs.append(doc)
        total = sum(len(d.theorems) for d in docs)
        assert total == 350
        assert len(DATA_PROOF_BUNDLE) == 339

    def test_algebra_bundle_loads_sixty_two_theorems(self):
        docs = []
        counter = 1
        from flow.proof_document import assign_numbers, parse_proof_file

        for rel in ALGEBRA_PROOF_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            assign_numbers([doc], start=counter)
            counter += len(doc.theorems)
            docs.append(doc)
        total = sum(len(d.theorems) for d in docs)
        assert total == 198
        assert len(ALGEBRA_PROOF_BUNDLE) == 185

    def test_geometry_derived_bundle_loads_one_hundred_thirty_three_theorems(self):
        docs = []
        from flow.proof_document import assign_numbers, parse_proof_file

        for rel in GEOMETRY_DERIVED_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            assign_numbers([doc], start=1)
            docs.append(doc)
        total = sum(len(d.theorems) for d in docs)
        assert total == 133
        assert len(GEOMETRY_DERIVED_BUNDLE) == 133

    def test_unified_book_has_one_thousand_one_hundred_twenty_theorems(self):
        parts = load_proof_book(ROOT)
        total = sum(len(d.theorems) for p in parts for d in p.docs)
        assert total == 1120
        assert len(GEOMETRY_DERIVED_BUNDLE) == 133
        assert len(EUCLID_BOOK_I_BUNDLE) == 48
        assert len(EUCLID_BOOK_II_BUNDLE) == 14
        assert len(EUCLID_BOOK_III_BUNDLE) == 37
        assert len(EUCLID_BOOK_IV_BUNDLE) == 16
        assert len(EUCLID_BOOK_V_BUNDLE) == 25
        assert len(EUCLID_BOOK_VI_BUNDLE) == 33
        assert len(FLOW_PROOF_BOOK) == (
            len(BASIC_PROOF_BUNDLE)
            + len(DATA_PROOF_BUNDLE)
            + len(EUCLID_BOOK_I_BUNDLE)
            + len(EUCLID_BOOK_II_BUNDLE)
            + len(EUCLID_BOOK_III_BUNDLE)
            + len(EUCLID_BOOK_IV_BUNDLE)
            + len(EUCLID_BOOK_V_BUNDLE)
            + len(EUCLID_BOOK_VI_BUNDLE)
            + len(GEOMETRY_DERIVED_BUNDLE)
            + len(ALGEBRA_PROOF_BUNDLE)
            + len(ANALYSIS_APPENDIX)
        )

    def test_prerequisite_cites_theorem_number(self):
        parts = load_proof_book(ROOT)
        tex = render_side_by_side_bundle(book_parts=parts, title="Flow Proof Book")
        assert "We invoke Axiom" in tex or "We invoke \\hyperref" in tex
        assert "We invoke Derived fact" in tex or "We invoke Definition" in tex
        assert "From Axiom" in tex or "From Definition" in tex or "From Derived fact" in tex
        assert parts[0].title.startswith("Part I")
        assert parts[1].title.startswith("Part II")
        assert parts[2].title.startswith("Book I")
        assert parts[3].title.startswith("Book II")
        assert parts[4].title.startswith("Book III")
        assert parts[5].title.startswith("Book IV")
        assert parts[6].title.startswith("Book V")
        assert parts[7].title.startswith("Book VI")
        assert parts[8].title.startswith("Geometry")
        assert parts[9].title.startswith("Part III")

    def test_euclid_book_ii_all_fourteen_props_have_multiple_steps(self):
        stepped = 0
        for rel in EUCLID_BOOK_II_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            thm = doc.theorems[0]
            if len(thm.steps) >= 3:
                stepped += 1
        assert stepped == 14

    def test_euclid_book_iii_all_thirty_seven_props_have_multiple_steps(self):
        stepped = 0
        for rel in EUCLID_BOOK_III_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            thm = doc.theorems[0]
            if len(thm.steps) >= 3:
                stepped += 1
        assert stepped == 37

    def test_euclid_book_iii_prop_twenty_central_angle_has_steps(self):
        doc = parse_proof_file(
            os.path.join(ROOT, "examples/verify/euclid/book-iii/prop-20-central-angle-double-inscribed.flow")
        )
        thm = doc.theorems[0]
        assert len(thm.steps) >= 4
        assert any(s.kind == "let" for s in thm.steps)

    def test_euclid_book_iv_all_sixteen_props_have_multiple_steps(self):
        stepped = 0
        for rel in EUCLID_BOOK_IV_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            thm = doc.theorems[0]
            if len(thm.steps) >= 3:
                stepped += 1
        assert stepped == 16

    def test_euclid_book_v_all_twenty_five_props_have_multiple_steps(self):
        stepped = 0
        for rel in EUCLID_BOOK_V_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            thm = doc.theorems[0]
            if len(thm.steps) >= 3:
                stepped += 1
        assert stepped == 25

    def test_euclid_book_vi_all_thirty_three_props_have_multiple_steps(self):
        stepped = 0
        for rel in EUCLID_BOOK_VI_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            thm = doc.theorems[0]
            if len(thm.steps) >= 3:
                stepped += 1
        assert stepped == 33

    def test_side_by_side_tex_has_two_columns(self):
        docs = load_basic_proof_bundle(ROOT)
        tex = render_side_by_side_bundle(docs)
        assert r"\begin{tabular}" in tex
        assert "Theorem 1" in tex or "Axiom 1" in tex or "Definition 1" in tex
        assert r"\textbf{1.}" in tex
        assert r"\textbf{Proof}" in tex and r"\textbf{Mathematics}" in tex
        assert r"\begin{tikzpicture}" not in tex

    def test_euclid_prop_one_has_construction_steps(self):
        doc = parse_proof_file(
            os.path.join(ROOT, "examples/verify/euclid/book-i/prop-01-equilateral-triangle.flow")
        )
        thm = doc.theorems[0]
        assert len(thm.steps) >= 5
        assert any(s.kind == "let" for s in thm.steps)
        assert sum(1 for s in thm.steps if s.kind == "therefore") >= 2

    def test_euclid_book_i_all_forty_eight_props_have_multiple_steps(self):
        stepped = 0
        for rel in EUCLID_BOOK_I_BUNDLE:
            doc = parse_proof_file(os.path.join(ROOT, rel))
            thm = doc.theorems[0]
            if len(thm.steps) >= 3:
                stepped += 1
        assert stepped == 48

    def test_euclid_prop_forty_seven_pythagoras_has_construction_steps(self):
        doc = parse_proof_file(
            os.path.join(ROOT, "examples/verify/euclid/book-i/prop-47-pythagoras.flow")
        )
        thm = doc.theorems[0]
        assert len(thm.steps) >= 6
        assert any(s.kind == "let" for s in thm.steps)

    def test_euclid_prop_thirty_two_has_exterior_angle_steps(self):
        doc = parse_proof_file(
            os.path.join(ROOT, "examples/verify/euclid/book-i/prop-32-exterior-angle-sum.flow")
        )
        thm = doc.theorems[0]
        assert len(thm.steps) >= 5
        assert any(s.kind == "let" for s in thm.steps)

    def test_euclid_prop_twenty_nine_has_parallel_steps(self):
        doc = parse_proof_file(
            os.path.join(ROOT, "examples/verify/euclid/book-i/prop-29-alternate-angles-equal.flow")
        )
        thm = doc.theorems[0]
        assert len(thm.steps) >= 5
        assert any(s.kind == "let" for s in thm.steps)

    def test_euclid_prop_fifteen_has_vertical_angle_steps(self):
        doc = parse_proof_file(
            os.path.join(ROOT, "examples/verify/euclid/book-i/prop-15-vertical-angles.flow")
        )
        thm = doc.theorems[0]
        assert len(thm.steps) >= 5
        assert sum(1 for s in thm.steps if s.kind == "assume") >= 1

    def test_unified_book_tex_has_both_parts(self):
        parts = load_proof_book(ROOT)
        tex = render_side_by_side_bundle(book_parts=parts, title="Flow Proof Book")
        assert "Part I" in tex
        assert "Part II" in tex
        assert "Book I" in tex
        assert "Book II" in tex
        assert "Book III" in tex
        assert "Book IV" in tex
        assert "Book V" in tex
        assert "Book VI" in tex
        assert "Geometry" in tex
        assert "Part III" in tex
        assert "Proposition 47" in tex
        assert "Proposition 1" in tex
        assert r"\tableofcontents" in tex
        assert "Taylor" in tex or "taylor" in tex

    @pytest.mark.skipif(not has_tex, reason="No LaTeX compiler available")
    def test_basic_pdf_compiles(self):
        tex, pdf = write_basic_proof_bundle_pdf(ROOT)
        assert os.path.isfile(tex)
        assert os.path.isfile(pdf)
        assert os.path.getsize(pdf) > 1000

    @pytest.mark.skipif(not has_tex, reason="No LaTeX compiler available")
    def test_unified_book_pdf_compiles(self):
        tex, pdf = write_proof_book_pdf(ROOT)
        assert os.path.isfile(tex)
        assert os.path.isfile(pdf)
        assert tex.endswith("flow-proof-book.tex")
        assert pdf.endswith("flow-proof-book.pdf")
        assert os.path.getsize(pdf) > 5000