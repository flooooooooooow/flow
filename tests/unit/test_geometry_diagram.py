"""Geometric proof diagrams."""

import os
from pathlib import Path

from flow.geometry_diagram import (
    _templates,
    diagram_for_theorem,
    render_svg,
    write_diagram_artifacts,
)
from flow.proof_document import GEOMETRY_PROOF_BUNDLE, parse_proof_file


ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
TRIANGLE = os.path.join(ROOT, "examples", "verify", "geometry", "triangle-angle-sum.flow")
PARALLEL = os.path.join(ROOT, "examples", "verify", "geometry", "parallel-lines-alternate.flow")
THALES = os.path.join(ROOT, "examples", "verify", "geometry", "thales-right-angle.flow")
INSCRIBED = os.path.join(
    ROOT, "examples", "verify", "geometry", "inscribed-angle-half-central.flow"
)


class TestGeometryDiagram:
    def test_triangle_diagram_from_metadata(self):
        doc = parse_proof_file(TRIANGLE)
        thm = doc.theorems[0]
        diag = diagram_for_theorem(thm)
        assert diag is not None
        svg = render_svg(diag)
        assert "<svg" in svg
        assert "Triangle ABC" in svg or "α" in svg
        assert "A" in svg and "B" in svg and "C" in svg

    def test_parallel_lines_diagram(self):
        doc = parse_proof_file(PARALLEL)
        thm = doc.theorems[0]
        diag = diagram_for_theorem(thm)
        assert diag is not None
        assert diag.title == "Parallel lines and a transversal"
        svg = render_svg(diag)
        assert "parallel" in svg.lower() or "α" in svg

    def test_thales_diagram_has_circle_and_right_angle(self):
        doc = parse_proof_file(THALES)
        diag = diagram_for_theorem(doc.theorems[0])
        assert diag is not None
        svg = render_svg(diag)
        assert "<circle" in svg
        assert "Thales" in diag.title or "semicircle" in diag.caption.lower()

    def test_inscribed_angle_diagram_has_central_and_inscribed_marks(self):
        doc = parse_proof_file(INSCRIBED)
        diag = diagram_for_theorem(doc.theorems[0])
        assert diag is not None
        labels = [m[3] for m in diag.angle_marks]
        assert "θ" in labels and "2θ" in labels

    def test_legacy_geometry_templates_exist(self):
        templates = _templates()
        legacy = [
            "examples/verify/geometry/triangle-angle-sum.flow",
            "examples/verify/geometry/parallel-lines-alternate.flow",
            "examples/verify/geometry/thales-right-angle.flow",
            "examples/verify/geometry/pythagoras.flow",
        ]
        for rel in legacy:
            path = os.path.join(ROOT, rel)
            doc = parse_proof_file(path)
            thm = doc.theorems[0]
            key = thm.meta.diagram or ""
            assert key in templates, f"missing template for {rel}"

    def test_write_diagram_artifacts(self, tmp_path):
        doc = parse_proof_file(TRIANGLE)
        thm = doc.theorems[0]
        svg, tex = write_diagram_artifacts(thm, tmp_path, "triangle-angle-sum")
        assert svg and os.path.exists(svg)
        assert tex and os.path.exists(tex)
        assert Path(svg).suffix == ".svg"