"""Programmable geometry script language."""

import os

from flow.geometry_script import run_geometry_script, run_geometry_script_file
from flow.geometry_diagram import diagram_for_theorem, render_svg, render_tikz
from flow.proof_document import parse_proof_file, write_proof_artifacts


ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
TAYLOR_GEOM = os.path.join(
    ROOT, "examples", "verify", "geometry", "scripts", "taylor-sin.geom"
)
TAYLOR_FLOW = os.path.join(
    ROOT, "examples", "verify", "geometry", "taylor-sin-maclaurin.flow"
)


class TestGeometryScript:
    def test_while_and_def_compute_factorial(self):
        src = """
        def fact(n) {
          let r = 1
          let i = 2
          while i <= n {
            let r = r * i
            let i = i + 1
          }
          return r
        }
        let y = fact(5)
        size 100 100
        axes 10 90 10 -1 1 -1 1
        plot y * 0 + 1 from 0 to 1 color #000
        """
        diag = run_geometry_script(src)
        assert diag.axes is not None

    def test_taylor_sin_script_renders_curves(self):
        diag = run_geometry_script_file(TAYLOR_GEOM)
        assert len(diag.curves) >= 4
        assert diag.axes is not None
        svg = render_svg(diag)
        assert "<polyline" in svg
        assert "sin" in svg.lower() or "Taylor" in diag.title

    def test_taylor_tikz_avoids_raw_hex_colors(self):
        diag = run_geometry_script_file(TAYLOR_GEOM)
        tikz = render_tikz(diag)
        assert r"\definecolor{geomc0}{HTML}" in tikz
        assert "fill=#" not in tikz
        assert "draw=#" not in tikz

    def test_builtin_diagram_tikz_renders_angle_marks(self):
        from flow.geometry_diagram import _templates

        diag = _templates()["vertical-angles"]
        tikz = render_tikz(diag)
        assert r"\pic" in tikz
        assert r"$\alpha$" in tikz

    def test_taylor_flow_uses_diagram_script(self):
        doc = parse_proof_file(TAYLOR_FLOW)
        thm = doc.theorems[0]
        assert "taylor-sin.geom" in thm.meta.diagram_script
        diag = diagram_for_theorem(thm, flow_file_dir=os.path.dirname(TAYLOR_FLOW))
        assert diag is not None
        assert len(diag.curves) >= 4

    def test_write_taylor_proof_artifacts(self, tmp_path):
        import shutil

        dst = tmp_path / "taylor-sin-maclaurin.flow"
        shutil.copy(TAYLOR_FLOW, dst)
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        shutil.copy(TAYLOR_GEOM, scripts / "taylor-sin.geom")
        md, tex, diagrams = write_proof_artifacts(str(dst))
        assert any(p.endswith(".svg") for p in diagrams)
        with open(md) as f:
            md_text = f.read()
        assert "Taylor" in md_text or "Maclaurin" in md_text