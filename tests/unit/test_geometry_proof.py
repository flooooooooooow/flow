"""Geometry proofs with embedded diagrams."""

import os

from flow.math_prose import flow_expr_to_mathematical_english, geometry_expr_to_latex
from flow.proof_document import (
    GEOMETRY_PROOF_BUNDLE,
    load_geometry_proof_bundle,
    write_proof_artifacts,
)


ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
TRIANGLE = os.path.join(ROOT, "examples", "verify", "geometry", "triangle-angle-sum.flow")


class TestGeometryProof:
    def test_geometry_prose_reads_like_mathematics(self):
        eng = flow_expr_to_mathematical_english(
            "angle_A + angle_B + angle_C == two_right_angles"
        )
        assert "angle A" in eng
        assert "two right angles" in eng
        tex = geometry_expr_to_latex("c * c == a * a + b * b")
        assert "c^{2}" in tex
        thales = flow_expr_to_mathematical_english("angle_ACB == one_right_angle")
        assert "one right angle" in thales
        assert geometry_expr_to_latex("angle_ACB == one_right_angle") == r"\angle ACB = 90^\circ"

    def test_markdown_embeds_figure(self, tmp_path):
        import shutil

        dst = tmp_path / "triangle-angle-sum.flow"
        shutil.copy(TRIANGLE, dst)
        md, tex, diagrams = write_proof_artifacts(str(dst))
        with open(md) as f:
            text = f.read()
        assert "**Figure.**" in text
        assert ".proof.svg" in text
        assert len(diagrams) >= 1
        assert "Euclidean plane" in text or "interior angles" in text.lower()
        assert "two right angles" in text

    def test_geometry_bundle_loads_euclid_book_i(self, tmp_path):
        docs = load_geometry_proof_bundle(ROOT, diagram_dir=tmp_path)
        assert len(docs) == len(GEOMETRY_PROOF_BUNDLE)
        assert len(GEOMETRY_PROOF_BUNDLE) == 48
        total = sum(len(d.theorems) for d in docs)
        assert total == 48